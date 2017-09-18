from config import config
import myvariant
import json

import redis
redis.StrictRedis(host='localhost', port=6379, db=0).flushall()

# Amino Acid Map
aa_map_1to3 = {'A': 'Ala',
               'B': 'Asx',
               'C': 'Cys',
               'D': 'Asp',
               'E': 'Glu',
               'F': 'Phe',
               'G': 'Gly',
               'H': 'His',
               'I': 'Ile',
               'J': 'Xle',
               'K': 'Lys',
               'L': 'Leu',
               'M': 'Met',
               'N': 'Asn',
               'O': 'Pyl',
               'P': 'Pro',
               'Q': 'Gln',
               'R': 'Arg',
               'S': 'Ser',
               'T': 'Thr',
               'U': 'Sec',
               'V': 'Val',
               'W': 'Trp',
               'X': 'Xaa',
               'Y': 'Tyr',
               'Z': 'Glx'}
aa_map_3to1 = {}

for key in aa_map_1to3:
    aa_map_3to1[aa_map_1to3[key]] = key


def map_aa_3to1(aa):
    temp = aa
    for key in aa_map_3to1:
        temp = temp.replace(key, aa_map_3to1[key])
    return temp


def map_aa_1to3(aa):
    # first 3 to 1 to make sure it's in 1 format
    temp = map_aa_3to1(aa)
    for key in aa_map_1to3:
        temp = temp.replace(key, aa_map_1to3[key])
    return temp

def map_chr_to_num(chr):
    if isinstance(chr, basestring):
        if chr.lower() == 'x':
            return 23
        elif chr.lower() == 'y':
            return 24
    return int(chr)

def map_chr_to_str(chr):
    if isinstance(chr, basestring):
        if chr.isdigit():
            chr = int(chr)
    if chr == 23:
        return 'X'
    elif chr == 24:
        return 'Y'
    return str(chr)

# <REFERENCE_SEQUENCE_ID>:<SEQUENCE_TYPE>.<POSITION><CHANGE>

class GeneReference:
    REF_TYPE_NM = "NM"
    REF_TYPE_ENST = "ENST"
    REF_TYPE_NC = "NC"
    REF_TYPE_NP = "NP"
    REF_TYPE_CHR = "chr"
    REF_TYPE_GENE = "GENE"
    REF_TYPE_ENSG = "ENSG"

    def __init__(self, ref_seq=None):
        self.ref_seq = ref_seq
        ref_type = self.get_ref_type(ref_seq)
        if ref_type:
            self.ref_type = ref_type
        else:
            raise ValueError("Malformed reference sequence: " + ref_seq)

    def get_all_ids(self):
        res = {
            'ref_seq': []
        }
        for a in dir(self):
            if a.startswith('REF_TYPE_'):
                ref_type = getattr(self, a)
                new_ref_seq = self.transform_ref_seq(self.ref_seq, ref_type)
                if new_ref_seq:
                    res['ref_seq'].append(new_ref_seq)
        return res

    @staticmethod
    def get_ref_type(ref_seq):
        if ref_seq:
            if ref_seq.startswith(GeneVariant.REF_TYPE_ENST):
                return GeneVariant.REF_TYPE_ENST
            elif ref_seq.startswith(GeneVariant.REF_TYPE_NM):
                return GeneVariant.REF_TYPE_NM
            elif ref_seq.startswith(GeneVariant.REF_TYPE_NC):
                return GeneVariant.REF_TYPE_NC
            elif ref_seq.startswith(GeneVariant.REF_TYPE_NP):
                return GeneVariant.REF_TYPE_NP
            elif ref_seq.startswith(GeneVariant.REF_TYPE_CHR):
                return GeneVariant.REF_TYPE_CHR
            elif ref_seq.startswith(GeneVariant.REF_TYPE_ENSG):
                return GeneVariant.REF_TYPE_ENSG
            elif all(x.isupper() or x.isdigit() for x in ref_seq):
                return GeneVariant.REF_TYPE_GENE
        return None

    @staticmethod
    def transform_ref_seq(target, to_type):
        '''
        Transform the reference sequence to target type
        :param target: it can be just reference sequence for transcript but full expression for gCDNA
        :param to_type: type of reference sequence
        :return:
        '''
        ref_seq = target.split(':')[0]
        from_type = GeneVariant.get_ref_type(ref_seq)
        if to_type == from_type:
            return target

        if to_type == GeneVariant.REF_TYPE_ENST or from_type == GeneVariant.REF_TYPE_ENST:
            ''' If ENST transformation, first try DB:EnsemblTranscriptDict '''
            cancer_db = config.connect_db(config.CANCER_DB_KEY)
            from_ENST = from_type == GeneVariant.REF_TYPE_ENST
            query = "SELECT Ref_Seq FROM EnsemblTranscriptDict WHERE ENST_ID = %s" \
                if from_ENST else "SELECT ENST_ID FROM EnsemblTranscriptDict WHERE Ref_Seq = %s"
            result_key = 'Ref_Seq' if from_ENST else 'ENST_ID'
            params = (ref_seq,)
            cursor = cancer_db.cursor()
            cursor.execute(query, params)
            res = cursor.fetchone()
            if res:
                to_ref_seq = res.get(result_key, None)
                if to_ref_seq and GeneVariant.get_ref_type(to_ref_seq) == to_type:
                    return to_ref_seq
        ''' All transformation: myvariant'''
        # MyVariantInfo(url='http://myvariant.info/v1')
        mv_res = MyVariantUtil.myvariant_query(target)
        if mv_res:
            return MyVariantUtil.myvariant_extract(mv_res[0], to_type)
        return None


class GeneVariant(GeneReference):
    INFO_TYPE_C = 'c.'
    INFO_TYPE_P = 'p.'
    INFO_TYPE_G = 'g.'

    def __init__(self, expr=None, ref_seq=None, var_info=None):
        if not expr and (not ref_seq or not var_info):
            raise ValueError("Variant expression or reference sequence/variant detail info not provided")
        if expr:
            try:
                arr = expr.split(':')
                ref_seq = arr[0]
                var_info = arr[1]
            except Exception as e:
                raise ValueError("Malformed expression: " + expr)
        else:
            expr = ref_seq + ':' + var_info

        GeneReference.__init__(self, ref_seq)
        self.var_info = var_info
        self.expr = expr
        info_type = self.get_info_type(var_info)
        if info_type:
            self.info_type = info_type
        else:
            raise ValueError("Malformed variant detail info: " + var_info)

    def get_all_ids(self):
        res = {
            'ref_seq': [],
            'var_info': []
        }
        for a in dir(self):
            if a.startswith('REF_TYPE_'):
                ref_type = getattr(self, a)
                arr = self.transform_variant(to_ref_type=ref_type)
                if arr[0]:
                    res['ref_seq'].append(arr[0])
            if a.startswith('INFO_TYPE_'):
                info_type = getattr(self, a)
                arr = self.transform_variant(to_info_type=info_type)
                if arr[1]:
                    res['var_info'].append(arr[1])
        return res

    @staticmethod
    def get_info_type(var_info):
        if var_info:
            if var_info.startswith(GeneVariant.INFO_TYPE_C):
                return GeneVariant.INFO_TYPE_C
            elif var_info.startswith(GeneVariant.INFO_TYPE_P):
                return GeneVariant.INFO_TYPE_P
            elif var_info.startswith(GeneVariant.INFO_TYPE_G):
                return GeneVariant.INFO_TYPE_G
        return None

    TRANSFORM_CHR_POS_REF_ALT = 'chr_pos_ref_alt'

    def transform_variant(self, to_ref_type=None, to_info_type=None):
        if to_ref_type == GeneVariant.TRANSFORM_CHR_POS_REF_ALT:  # special case
            results = MyVariantUtil.myvariant_query(self.expr)
            if results:
                return MyVariantUtil.myvariant_extract(results[0], MyVariantUtil.MYVARIANT_CHR_POS_REF_ALT)
            else:
                return []
        to_var_info = None
        to_ref_seq = None
        if to_ref_type == self.ref_type:
            to_ref_seq = self.ref_seq
        elif to_ref_type:
            to_ref_seq = GeneVariant.transform_ref_seq(self.expr, to_ref_type)

        if to_info_type == self.info_type:
            to_var_info = self.var_info
        elif to_info_type:
            results = MyVariantUtil.myvariant_query(self.expr)
            if results:
                to_var_info = MyVariantUtil.myvariant_extract(results[0], to_info_type)
        return [to_ref_seq, to_var_info]

class MyVariantUtil:
    MYVARIANT_CHR_POS_REF_ALT = 'chr_pos_ref_alt'
    REDIS_MV = redis.StrictRedis(host='localhost', port=6379, db=0)

    @staticmethod
    def myvariant_extract(mv_res, type):
        # reference type retrieval
        res = None
        if type == MyVariantUtil.MYVARIANT_CHR_POS_REF_ALT:
            try:
                chr = mv_res['_id'].split(':')[0][3:]
                vcf = mv_res['vcf']
                alt = vcf['alt']
                pos = vcf['position']
                ref = vcf['ref']
                return [chr, pos, ref, alt]
            except Exception as e:
                pass

        ref_type = GeneVariant.get_ref_type(type)
        info_type = GeneVariant.get_info_type(type)

        if ref_type:
            if type == GeneVariant.REF_TYPE_ENST:
                if not res:
                    try:
                        cadd_gene = mv_res['cadd']['gene']
                        if isinstance(cadd_gene, list):
                            cadd_gene = cadd_gene[0]
                        res = cadd_gene['feature_id']
                    except Exception as e:
                        pass
                if not res:
                    try:
                        res = mv_res['civic']['coordinates']['representative_transcript']
                    except Exception as e:
                        pass
                if res:
                    res = res.split('.')[0]
                return res
            elif type == GeneVariant.REF_TYPE_GENE:
                if not res:
                    try:
                        ann = mv_res['snpeff']['ann']
                        if isinstance(ann, list):
                            ann = ann[0]
                        res = ann['genename']
                    except Exception as e:
                        pass
                if not res:
                    try:
                        res = mv_res['dbsnp']['gene']['symbol']
                    except Exception as e:
                        pass
            elif type == GeneVariant.REF_TYPE_CHR:
                if not res:
                    try:
                        res = mv_res['_id'].split(':')[0]
                    except Exception as e:
                        pass
            elif type == GeneVariant.REF_TYPE_NM:
                if not res:
                    try:
                        ann = mv_res['snpeff']['ann']
                        if isinstance(ann, list):
                            ann = ann[0]
                        res = ann['feature_id']
                        if GeneVariant.get_ref_type(res) != GeneVariant.REF_TYPE_NM:
                            res = None
                    except Exception as e:
                        pass
            elif type == GeneVariant.REF_TYPE_ENSG:
                if not res:
                    try:
                        cadd_gene = mv_res['cadd']['gene']
                        if isinstance(cadd_gene, list):
                            cadd_gene = cadd_gene[0]
                        res = cadd_gene['gene_id']
                    except Exception as e:
                        pass
                if not res:
                    try:
                        res = mv_res['dbnsfp']['ensembl']['geneid']
                    except Exception as e:
                        pass
        # var info type retrieval
        elif info_type:
            if type == GeneVariant.INFO_TYPE_P:
                if not res:
                    try:
                        ann = mv_res['snpeff']['ann']
                        if isinstance(ann, list):
                            ann = ann[0]
                        res = ann['hgvs_p']
                    except Exception as e:
                        pass
            elif type == GeneVariant.INFO_TYPE_C:
                if not res:
                    try:
                        ann = mv_res['snpeff']['ann']
                        if isinstance(ann, list):
                            ann = ann[0]
                        res = ann['hgvs_c']
                    except Exception as e:
                        pass
            elif type == GeneVariant.INFO_TYPE_G:
                if not res:
                    try:
                        res = mv_res['_id'].split(':')[1]
                    except Exception as e:
                        pass

        if not res:
            if info_type or ref_type:
                # try civic expressions for ref_seq or var_info:
                try:
                    exprs = mv_res['civic']['hgvs_expressions']
                    for expr in exprs:
                        arr = expr.split(':')
                        if ref_type and GeneVariant.get_ref_type(arr[0]) == ref_type:
                            res = arr[0]  # take the ref_seq part
                        if info_type and GeneVariant.get_ref_type(arr[1]) == info_type:
                            res = arr[1]  # take the var_info part
                except Exception as e:
                    pass
            # if it's custom field like snpeff.ann.genename
            else:
                field_arr = type.split('.')
                try:
                    res = mv_res
                    for field in field_arr:
                        res = res[field]
                except Exception as e:
                    res = None
                    pass
        return res

    MYVARIANT_EXPR = 'civic.hgvs_expressions'

    @staticmethod
    def myvariant_query(target, field='ref_seq'):
        '''
        Currently only use snpeff, dbnsfp, cadd, cosmic data

        :param target: search target, can be expression
        :param field: myvariant field e.g. cosmic.cosmic_id
        :return: hits array
        '''
        cached_data = MyVariantUtil.REDIS_MV.get(target)
        if cached_data:
            return json.loads(cached_data)
        query = None
        res = None
        mv = myvariant.MyVariantInfo()
        if field == 'ref_seq':
            arr = target.split(':')
            ref_seq = arr[0]
            var_info = arr[1] if len(arr) > 1 else None

            ref_seq_type = GeneVariant.get_ref_type(ref_seq)
            info_type = GeneVariant.get_info_type(var_info)
            if info_type == GeneVariant.INFO_TYPE_G:
                import re
                if ref_seq_type == GeneVariant.REF_TYPE_NC:
                    ref_seq = 'chr' + re.sub(r'NC_0*', '', ref_seq).split('.')[0]
                    ref_seq_type = GeneVariant.REF_TYPE_CHR
                    target = ref_seq + ':' + var_info
                if ref_seq_type == GeneVariant.REF_TYPE_CHR:
                    var = mv.getvariant(target)
                    if var:
                        res = [var]
                    else:
                        # not sure about this : chr3:g.41266248_41266249delAG not supported by myvariant
                        # but chr3:g.41266248_41266249del
                        target = re.sub(r'[A-Z]', '', target)
                        var = mv.getvariant(target)
                        if var:
                            res = [var]
            else:
                # ref_seq part of query
                if ref_seq_type == GeneVariant.REF_TYPE_ENST:
                    query = 'cadd.gene.feature_id:' + ref_seq + \
                            '* OR dbnsfp.ensembl.transcriptid:' + ref_seq + \
                            '* OR civic.coordinates.representative_transcript:' + ref_seq + '*'
                elif ref_seq_type == GeneVariant.REF_TYPE_GENE:
                    query = 'snpeff.ann.genename:' + ref_seq
                elif ref_seq_type == GeneVariant.REF_TYPE_NM:
                    query = 'snpeff.ann.feature_id:' + ref_seq
                elif ref_seq_type == GeneVariant.REF_TYPE_ENSG:
                    query = 'cadd.gene:' + ref_seq + \
                            ' OR dbnsfp.ensembl.geneid:' + ref_seq

                # var_info part of the query
                if info_type == GeneVariant.INFO_TYPE_P:
                    var_info = map_aa_1to3(var_info)
                    target = ref_seq + ':' + var_info
                if query:
                    if info_type == GeneVariant.INFO_TYPE_P:
                        query += ' AND snpeff.ann.hgvs_p:' + var_info
                    if info_type == GeneVariant.INFO_TYPE_C:
                        query += ' AND snpeff.ann.hgvs_c:' + var_info
        if query:
            res = mv.query(query)['hits']
        if not res:
            if field == 'ref_seq':
                field = MyVariantUtil.MYVARIANT_EXPR
            target = target.replace(':', '\:')
            query = field + ':' + target + '*'  # e.g. 'cosmic.cosmic_id:COSM426644'
            res = mv.query(query)['hits']
        if res:
            MyVariantUtil.REDIS_MV.set(target, json.dumps(res), ex=60) # TODO: change ex
            return res
        else:
            return []


'''
"hgvs_expressions": [
      "NM_005957.4:c.665C>T",
      "NP_005948.3:p.Ala222Val",
      "ENST00000376592.1:c.665G>A",
      "NC_000001.10:g.11856378G>A"
    ]
'''
