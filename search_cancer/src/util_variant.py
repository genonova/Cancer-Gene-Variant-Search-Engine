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
    try:
        for key in aa_map_3to1:
            temp = temp.replace(key, aa_map_3to1[key])
    except Exception as e:
        print e.message
        return None
    return temp


def map_aa_1to3(aa):
    try:
        # first 3 to 1 to make sure it's in 1 format
        temp = map_aa_3to1(aa)
        for key in aa_map_1to3:
            temp = temp.replace(key, aa_map_1to3[key])
    except Exception as e:
        print e.message
        return None
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
        self.myvariant_res = None
        self.ref_seq = ref_seq
        ref_type = self.get_ref_type(ref_seq)
        if ref_type:
            self.ref_type = ref_type
        else:
            raise ValueError("Malformed reference sequence: " + str(ref_seq))

    def get_all_ids(self):
        res = {
            'ref_seq': []
        }
        for a in dir(self):
            if a.startswith('REF_TYPE_'):
                ref_type = getattr(self, a)
                new_ref_seq = self.transform_ref_seq(ref_type)
                if new_ref_seq:
                    res['ref_seq'].append(new_ref_seq)
        return res

    def get_myvariant_res(self, downgrade=True):
        if not self.myvariant_res:
            mv_results = MyVariantUtil.query(self.ref_seq)
            if mv_results:
                self.myvariant_res = mv_results[0]
        return self.myvariant_res

    @staticmethod
    def get_ref_type(target):
        if target:
            if target.startswith(GeneVariant.REF_TYPE_ENST):
                return GeneVariant.REF_TYPE_ENST
            elif target.startswith(GeneVariant.REF_TYPE_NM):
                return GeneVariant.REF_TYPE_NM
            elif target.startswith(GeneVariant.REF_TYPE_NC):
                return GeneVariant.REF_TYPE_NC
            elif target.startswith(GeneVariant.REF_TYPE_NP):
                return GeneVariant.REF_TYPE_NP
            elif target.startswith(GeneVariant.REF_TYPE_CHR):
                return GeneVariant.REF_TYPE_CHR
            elif target.startswith(GeneVariant.REF_TYPE_ENSG):
                return GeneVariant.REF_TYPE_ENSG
            elif all(x.isupper() or x.isdigit() or x == '-' for x in target):
                return GeneVariant.REF_TYPE_GENE
        return None

    def transform_ref_seq(self, to_type):
        '''
        Transform the reference sequence to target type
        :param to_type: type of reference sequence
        :return:
        '''

        if self.ref_type == to_type:
            return self.ref_seq

        ''' All transformation: myvariant'''
        # MyVariantInfo(url='http://myvariant.info/v1')
        mv_res = self.get_myvariant_res()
        if mv_res:
            res = MyVariantUtil.extract(mv_res, to_type)
            if res:
                return res

        ''' Fall back : EnsemblTranscriptDict '''
        if to_type == GeneVariant.REF_TYPE_ENST or self.ref_type == GeneVariant.REF_TYPE_ENST:
            ''' If ENST transformation, first try DB:EnsemblTranscriptDict '''
            cancer_db = config.connect_db(config.CANCER_DB_KEY)
            from_ENST = self.ref_type == GeneVariant.REF_TYPE_ENST
            query = "SELECT Ref_Seq FROM EnsemblTranscriptDict WHERE ENST_ID = %s" \
                if from_ENST else "SELECT ENST_ID FROM EnsemblTranscriptDict WHERE Ref_Seq = %s"
            result_key = 'Ref_Seq' if from_ENST else 'ENST_ID'
            params = (self.ref_seq,)
            cursor = cancer_db.cursor()
            cursor.execute(query, params)
            res = cursor.fetchone()
            if res:
                to_ref_seq = res.get(result_key, None)
                if to_ref_seq and GeneReference.get_ref_type(to_ref_seq) == to_type:
                    return to_ref_seq

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
                raise ValueError("Malformed expression: " + str(expr))
        else:
            expr = ref_seq + ':' + var_info

        GeneReference.__init__(self, ref_seq)
        self.var_info = var_info
        self.expr = expr
        info_type = self.get_info_type(var_info)
        if info_type:
            self.info_type = info_type
        else:
            raise ValueError("Malformed variant detail info: " + str(var_info))

    def get_myvariant_res(self, downgrade=False):
        if not self.myvariant_res:
            mv_results = MyVariantUtil.query(self.expr)
            if mv_results:
                self.myvariant_res = mv_results[0]
            else:
                mv_results = MyVariantUtil.query(self.ref_seq)
                if mv_results:
                    self.myvariant_res = mv_results[0]
        return self.myvariant_res

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

    TRANSFORM_CHR_POS_REF_ALT = 0  # 1-123123-G-A
    TRANSFORM_CHR_POS = 1  # 1:123123

    def transform_variant(self, to_ref_type=None, to_info_type=None):
        if to_ref_type == GeneVariant.TRANSFORM_CHR_POS_REF_ALT:  # special case
            mv_res = self.get_myvariant_res()
            if mv_res:
                return MyVariantUtil.extract(mv_res, MyVariantUtil.MYVARIANT_CHR_POS_REF_ALT)
            else:
                return []
        if to_ref_type == GeneVariant.TRANSFORM_CHR_POS:
            mv_res = self.get_myvariant_res()
            # if mv_res:
            #     chr_pos_ref_alt = MyVariantUtil.extract(mv_res, MyVariantUtil.MYVARIANT_CHR_POS_REF_ALT)
            #     if chr_pos_ref_alt:
            #         return chr_pos_ref_alt[:2]
            # fall back to manual extract
            chr_name = self.transform_ref_seq(GeneReference.REF_TYPE_CHR)
            if not chr_name:
                nc_seq = self.transform_ref_seq(GeneReference.REF_TYPE_NC)
                if nc_seq:
                    chr_num = 0
                    s = None
                    for i, c in enumerate(nc_seq):
                        if c.isdigit():
                            if not s:
                                s = i
                            chr_num = chr_num * 10 + int(c)
                        elif s:
                            break
                else:
                    return []
            else:
                chr_num = chr_name[3:]
            info_arr = self.transform_variant(self.ref_type, GeneVariant.INFO_TYPE_G)
            if not info_arr:
                return []
            s = None
            g_info = info_arr[1]
            e = len(g_info)
            for i, c in enumerate(g_info):
                if c.isdigit():
                    if not s:
                        s = i
                elif s:
                    e = i
                    break
            pos = g_info[s:e]
            return [chr_num, pos]

        to_var_info = None
        to_ref_seq = None
        if to_ref_type == self.ref_type:
            to_ref_seq = self.ref_seq
        elif to_ref_type:
            to_ref_seq = self.transform_ref_seq(to_ref_type)

        if to_info_type == self.info_type:
            to_var_info = self.var_info
        elif to_info_type:
            mv_res = self.get_myvariant_res()
            if mv_res:
                to_var_info = MyVariantUtil.extract(mv_res, to_info_type)
        return [to_ref_seq, to_var_info]

    def get_aa(self):
        p_info = self.transform_variant(self.ref_type, GeneVariant.INFO_TYPE_P)[1]
        if p_info:
            p_info = map_aa_3to1(p_info[2:])
            ref_aa = p_info[0]
            alt_aa = p_info[-1]
            return [ref_aa, alt_aa]
        return [None, None]

    @staticmethod
    def calculate_grantham_score(ref_aa=None, alt_aa=None, variant=None):
        grantham_matrix = {
            'S': {'R': 110, 'L': 145, 'P': 74, 'T': 58, 'A': 99, 'V': 124, 'G': 56, 'I': 142, 'F': 155, 'Y': 144,
                  'C': 112,
                  'H': 89, 'Q': 68, 'N': 46, 'K': 121, 'D': 65, 'E': 80, 'M': 135, 'W': 177},
            'R': {'R': 0, 'L': 102, 'P': 103, 'T': 71, 'A': 112, 'V': 96, 'G': 125, 'I': 97, 'F': 97, 'Y': 77, 'C': 180,
                  'H': 29, 'Q': 43, 'N': 86, 'K': 26, 'D': 96, 'E': 54, 'M': 91, 'W': 101, 'S': 0},
            'L': {'R': 0, 'L': 0, 'P': 98, 'T': 92, 'A': 96, 'V': 32, 'G': 138, 'I': 5, 'F': 22, 'Y': 36, 'C': 198,
                  'H': 99,
                  'Q': 113, 'N': 153, 'K': 107, 'D': 172, 'E': 138, 'M': 15, 'W': 61, 'S': 0},
            'P': {'R': 0, 'L': 0, 'P': 0, 'T': 38, 'A': 27, 'V': 68, 'G': 42, 'I': 95, 'F': 114, 'Y': 110, 'C': 169,
                  'H': 77, 'Q': 76, 'N': 91, 'K': 103, 'D': 108, 'E': 93, 'M': 87, 'W': 147, 'S': 0},
            'T': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 58, 'V': 69, 'G': 59, 'I': 89, 'F': 103, 'Y': 92, 'C': 149,
                  'H': 47,
                  'Q': 42, 'N': 65, 'K': 78, 'D': 85, 'E': 65, 'M': 81, 'W': 128, 'S': 0},
            'A': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 64, 'G': 60, 'I': 94, 'F': 113, 'Y': 112, 'C': 195,
                  'H': 86,
                  'Q': 91, 'N': 111, 'K': 106, 'D': 126, 'E': 107, 'M': 84, 'W': 148, 'S': 0},
            'V': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 109, 'I': 29, 'F': 50, 'Y': 55, 'C': 192,
                  'H': 84,
                  'Q': 96, 'N': 133, 'K': 97, 'D': 152, 'E': 121, 'M': 21, 'W': 88, 'S': 0},
            'G': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 135, 'F': 153, 'Y': 147, 'C': 159,
                  'H': 98,
                  'Q': 87, 'N': 80, 'K': 127, 'D': 94, 'E': 98, 'M': 127, 'W': 184, 'S': 0},
            'I': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 21, 'Y': 33, 'C': 198, 'H': 94,
                  'Q': 109, 'N': 149, 'K': 102, 'D': 168, 'E': 134, 'M': 10, 'W': 61, 'S': 0},
            'F': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 22, 'C': 205, 'H': 100,
                  'Q': 116, 'N': 158, 'K': 102, 'D': 177, 'E': 140, 'M': 28, 'W': 40, 'S': 0},
            'Y': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 0, 'C': 194, 'H': 83,
                  'Q': 99, 'N': 143, 'K': 85, 'D': 160, 'E': 122, 'M': 36, 'W': 37, 'S': 0},
            'C': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 0, 'C': 0, 'H': 174,
                  'Q': 154, 'N': 139, 'K': 202, 'D': 154, 'E': 170, 'M': 196, 'W': 215, 'S': 0},
            'H': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 0, 'C': 0, 'H': 0,
                  'Q': 24,
                  'N': 68, 'K': 32, 'D': 81, 'E': 40, 'M': 87, 'W': 115, 'S': 0},
            'Q': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 0, 'C': 0, 'H': 0,
                  'Q': 0,
                  'N': 46, 'K': 53, 'D': 61, 'E': 29, 'M': 101, 'W': 130, 'S': 0},
            'N': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 0, 'C': 0, 'H': 0,
                  'Q': 0,
                  'N': 0, 'K': 94, 'D': 23, 'E': 42, 'M': 142, 'W': 174, 'S': 0},
            'K': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 0, 'C': 0, 'H': 0,
                  'Q': 0,
                  'N': 0, 'K': 0, 'D': 101, 'E': 56, 'M': 95, 'W': 110, 'S': 0},
            'D': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 0, 'C': 0, 'H': 0,
                  'Q': 0,
                  'N': 0, 'K': 0, 'D': 0, 'E': 45, 'M': 160, 'W': 181, 'S': 0},
            'E': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 0, 'C': 0, 'H': 0,
                  'Q': 0,
                  'N': 0, 'K': 0, 'D': 0, 'E': 0, 'M': 126, 'W': 152, 'S': 0},
            'M': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 0, 'C': 0, 'H': 0,
                  'Q': 0,
                  'N': 0, 'K': 0, 'D': 0, 'E': 0, 'M': 0, 'W': 67, 'S': 0},
            'W': {'R': 0, 'L': 0, 'P': 0, 'T': 0, 'A': 0, 'V': 0, 'G': 0, 'I': 0, 'F': 0, 'Y': 0, 'C': 0, 'H': 0,
                  'Q': 0,
                  'N': 0, 'K': 0, 'D': 0, 'E': 0, 'M': 0, 'W': 0, 'S': 0}}
        if variant and isinstance(variant, GeneVariant):
            aa = variant.get_aa()
            ref_aa = aa[0]
            alt_aa = aa[1]
        if ref_aa and len(ref_aa) == 3:
            ref_aa = map_aa_3to1(ref_aa)
        if alt_aa and len(alt_aa) == 3:
            alt_aa = map_aa_3to1(alt_aa)
        if not ref_aa or not alt_aa or len(ref_aa) != 1 or len(alt_aa) != 1:
            return -1
        if ref_aa == alt_aa:
            return 0
        else:
            try:
                if int(grantham_matrix[ref_aa][alt_aa]) != 0:
                    return int(grantham_matrix[ref_aa][alt_aa])
                else:
                    return int(grantham_matrix[alt_aa][ref_aa])
            except Exception as e:
                return -1


class MyVariantUtil:
    SNP_ID_FIELDS = ['clinvar.rsid', 'dbnsfp.rsid', 'dbsnp.rsid', 'mutdb.rsid']
    MYVARIANT_CHR_POS_REF_ALT = 'chr_pos_ref_alt'
    REDIS_MV = redis.StrictRedis(host='localhost', port=6379, db=0)
    REDIS_MV_NOT_EXIST = redis.StrictRedis(host='localhost', port=6379, db=1)

    @staticmethod
    def extract(mv_res, field):
        # reference type retrieval
        res = None
        if field == MyVariantUtil.MYVARIANT_CHR_POS_REF_ALT:
            try:
                chr_num = mv_res['_id'].split(':')[0][3:]
                vcf = mv_res['vcf']
                alt = vcf['alt']
                pos = str(vcf['position'])
                ref = vcf['ref']
                return [chr_num, pos, ref, alt]
            except Exception as e:
                return []

        ref_type = GeneVariant.get_ref_type(field)
        info_type = GeneVariant.get_info_type(field)

        if ref_type:
            if field == GeneVariant.REF_TYPE_ENST:
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
            elif field == GeneVariant.REF_TYPE_GENE:
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
            elif field == GeneVariant.REF_TYPE_CHR:
                if not res:
                    try:
                        res = mv_res['_id'].split(':')[0]
                    except Exception as e:
                        pass
            elif field == GeneVariant.REF_TYPE_NM:
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
            elif field == GeneVariant.REF_TYPE_ENSG:
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
            if field == GeneVariant.INFO_TYPE_P:
                if not res:
                    try:
                        ann = mv_res['snpeff']['ann']
                        if isinstance(ann, list):
                            ann = ann[0]
                        res = ann['hgvs_p']
                    except Exception as e:
                        pass
            elif field == GeneVariant.INFO_TYPE_C:
                if not res:
                    try:
                        ann = mv_res['snpeff']['ann']
                        if isinstance(ann, list):
                            ann = ann[0]
                        res = ann['hgvs_c']
                    except Exception as e:
                        pass
            elif field == GeneVariant.INFO_TYPE_G:
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
                        if info_type and GeneVariant.get_info_type(arr[1]) == info_type:
                            res = arr[1]  # take the var_info part
                except Exception as e:
                    pass
            # if it's custom field like snpeff.ann.genename
            else:
                field_arr = field.split('.')
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
    def query(target, field='ref_seq'):
        '''
        Currently only use snpeff, dbnsfp, cadd, cosmic data

        :param target: search target, can be expression
        :param field: myvariant field e.g. cosmic.cosmic_id
        :return: hits array
        '''
        cached_data = MyVariantUtil.REDIS_MV.get(target)
        if cached_data:
            return json.loads(cached_data)
        if MyVariantUtil.REDIS_MV_NOT_EXIST.get(target):
            return None
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
            MyVariantUtil.REDIS_MV.set(target, json.dumps(res), ex=2073600)  # TODO: change ex current: 1 day!
            return res
        else:
            MyVariantUtil.REDIS_MV_NOT_EXIST.set(target, 1, ex=2073600)  # TODO: change ex current: 1 day!
            return []


'''
"hgvs_expressions": [
      "NM_005957.4:c.665C>T",
      "NP_005948.3:p.Ala222Val",
      "ENST00000376592.1:c.665G>A",
      "NC_000001.10:g.11856378G>A"
    ]
'''

'''
Granthan score matrix 
		Arg	Leu	Pro	Thr	Ala	Val	Gly	Ile	Phe	Tyr	Cys	His	Gln	Asn	Lys	Asp	Glu	Met	Trp		
		R	L	P	T	A	V	G	I	F	Y	C	H	Q	N	K	D	E	M	W		
Ser	S	110	145	74	58	99	124	56	142	155	144	112	89	68	46	121	65	80	135	177	S	Ser
Arg	R	0	102	103	71	112	96	125	97	97	77	180	29	43	86	26	96	54	91	101	R	Arg
Leu	L	0	0	98	92	96	32	138	5	22	36	198	99	113	153	107	172	138	15	61	L	Leu
Pro	P	0	0	0	38	27	68	42	95	114	110	169	77	76	91	103	108	93	87	147	P	Pro
Thr	T	0	0	0	0	58	69	59	89	103	92	149	47	42	65	78	85	65	81	128	T	Thr
Ala	A	0	0	0	0	0	64	60	94	113	112	195	86	91	111	106	126	107	84	148	A	Ala
Val	V	0	0	0	0	0	0	109	29	50	55	192	84	96	133	97	152	121	21	88	V	Val
Gly	G	0	0	0	0	0	0	0	135	153	147	159	98	87	80	127	94	98	127	184	G	Gly
Ile	I	0	0	0	0	0	0	0	0	21	33	198	94	109	149	102	168	134	10	61	I	Ile
Phe	F	0	0	0	0	0	0	0	0	0	22	205	100	116	158	102	177	140	28	40	F	Phe
Tyr	Y	0	0	0	0	0	0	0	0	0	0	194	83	99	143	85	160	122	36	37	Y	Tyr
Cys	C	0	0	0	0	0	0	0	0	0	0	0	174	154	139	202	154	170	196	215	C	Cys
His	H	0	0	0	0	0	0	0	0	0	0	0	0	24	68	32	81	40	87	115	H	His
Gln	Q	0	0	0	0	0	0	0	0	0	0	0	0	0	46	53	61	29	101	130	Q	Gln
Asn	N	0	0	0	0	0	0	0	0	0	0	0	0	0	0	94	23	42	142	174	N	Asn
Lys	K	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	101	56	95	110	K	Lys
Asp	D	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	45	160	181	D	Asp
Glu	E	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	126	152	E	Glu
Met	M	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	67	M	Met

'''
