from util_variant import GeneVariant, GeneReference, map_aa_3to1, map_chr_to_num, MyVariantUtil
from source_gene_source import GeneSource
from config import config
import util_query


class COSMIC(GeneSource):
    ID_ROUTE = 'http://cancer.sanger.ac.uk/cosmic/mutation/overview?id='
    QUERY_ROUTE = 'http://cancer.sanger.ac.uk/cosmic/search?q='

    @staticmethod
    def search_variant_db(variant, only_count=False, start=0, limit=0):
        res = None
        if isinstance(variant, GeneVariant):
            cancer_db = config.connect_db(config.CANCER_DB_KEY)
            cursor = cancer_db.cursor()
            if variant.info_type == GeneVariant.INFO_TYPE_G:  # chr1:g.11796321>A vs 10:26541626-26541626
                chr_num = 0
                s = None
                for i, c in enumerate(variant.ref_seq):
                    if c.isdigit():
                        if not s:
                            s = i
                        chr_num = chr_num * 10 + int(c)
                    elif s:
                        break
                s = None
                e = len(variant.var_info)
                for i, c in enumerate(variant.var_info):
                    if c.isdigit():
                        if not s:
                            s = i
                    elif s:
                        e = i
                        break
                pos = variant.var_info[s:e]
                chr_pos = str(map_chr_to_num(chr_num)) + ':' + pos
                base_query = "SELECT " + ("COUNT(*) count" if only_count else "*") \
                             + " FROM COSMICMutantExport WHERE Mutation_Genome_Position LIKE %s"
                base_params = (chr_pos + '%',)
                query, params = util_query.add_limit(base_query, base_params, start, limit)
                cursor.execute(query, params)
                res = cursor.fetchall()
            # Only NM or ENST format supported for COSMIC
            else:
                var_info = variant.var_info
                if variant.info_type == variant.INFO_TYPE_C:
                    info_attr = 'Mutation_CDS'
                elif variant.info_type == variant.INFO_TYPE_P:
                    var_info = map_aa_3to1(var_info)
                    info_attr = 'Mutation_AA'
                else:
                    return []
                ref_seq1 = variant.transform_ref_seq(GeneVariant.REF_TYPE_ENST)
                ref_seq2 = variant.transform_ref_seq(GeneVariant.REF_TYPE_NM)

                base_query = "SELECT " + ("COUNT(*) count" if only_count else "*") \
                             + " FROM COSMICMutantExport WHERE Accession_Number=%s AND " + info_attr + " LIKE %s"
                for ref_seq in (ref_seq1, ref_seq2):
                    if ref_seq:
                        base_params = (ref_seq, var_info)
                        query, params = util_query.add_limit(base_query, base_params, start, limit)
                        cursor.execute(query, params)
                        res = cursor.fetchall()
                        if res:
                            break
            if not res or (only_count and not res[0]['count']):
                # try myvariant directly
                mv_res = variant.get_myvariant_res()
                if mv_res:
                    cosmic_id = MyVariantUtil.extract(mv_res, 'cosmic.cosmic_id')
                    if cosmic_id:
                        base_query = "SELECT " + ("COUNT(*) count" if only_count else "*") \
                                     + " FROM COSMICMutantExport WHERE ID_Mutation=%s"
                        base_params = (cosmic_id,)
                        query, params = util_query.add_limit(base_query, base_params, start, limit)
                        cursor.execute(query, params)
                        res = cursor.fetchall()
            if res:
                return res if not only_count else res[0]['count']
        return [] if not only_count else 0

    @staticmethod
    def search_gene_db(reference, only_count=False, start=0, limit=0):
        res = None
        if isinstance(reference, GeneReference):
            gene = reference.ref_seq
            if reference.ref_type != GeneVariant.REF_TYPE_GENE:
                gene = reference.transform_ref_seq(GeneVariant.REF_TYPE_GENE)
            if gene:
                cancer_db = config.connect_db(config.CANCER_DB_KEY)
                cursor = cancer_db.cursor()
                base_query = "SELECT " + ("COUNT(*) count" if only_count else "*") \
                             + " FROM COSMICMutantExport WHERE Gene_Name LIKE %s"
                base_params = (gene,)
                query, params = util_query.add_limit(base_query, base_params, start, limit)
                cursor.execute(query, params)
                res = cursor.fetchall()
        if res:
            return res if not only_count else res[0]['count']
        return [] if not only_count else 0

    @staticmethod
    def search_transcript_db(reference, only_count=False, start=0, limit=0):
        res = None
        if isinstance(reference, GeneReference):
            base_query = "SELECT " + ("COUNT(*) count" if only_count else "*") \
                         + " FROM COSMICMutantExport WHERE Accession_Number LIKE %s"
            cancer_db = config.connect_db(config.CANCER_DB_KEY)
            cursor = cancer_db.cursor()
            ref_seq1 = reference.transform_ref_seq(GeneVariant.REF_TYPE_ENST)
            ref_seq2 = reference.transform_ref_seq(GeneVariant.REF_TYPE_NM)
            for ref_seq in (ref_seq1, ref_seq2):
                if ref_seq:
                    base_params = (ref_seq,)
                    query, params = util_query.add_limit(base_query, base_params, start, limit)
                    cursor.execute(query, params)
                    res = cursor.fetchall()
                    if res:
                        break
        if res:
            return res if not only_count else res[0]['count']
        return [] if not only_count else 0

    @staticmethod
    def gene_exist(gene):
        res = COSMIC.search_gene_db(reference=gene, only_count=True, limit=1)
        return res >= 1

    @staticmethod
    def get_cosmic_url(data):
        '''
        Get COSMIC URL based on input
        :param data: COSMIC ID or COSMIC search result or transcript / gene
        :return: Two different URL based on whether the data is a COSMIC ID or it's a dictionary (COSMIC record) that contains the ID
        '''
        query = None
        if isinstance(data, dict):  # if it's a COSMIC record
            query = data.get('ID_Mutation', None)
        elif isinstance(data, basestring):
            query = data
        else:
            return None
        if query:
            if query.startswith('COSM'):
                query = query[4:]
                if query.isdigit():
                    return COSMIC.ID_ROUTE + query
            else:
                return COSMIC.QUERY_ROUTE + query

        return None

    @staticmethod
    def search_variant(variant):
        cosmic_count = COSMIC.search_variant_db(variant, only_count=True)
        if cosmic_count > 0:
            cosmic_example = COSMIC.search_variant_db(variant, limit=1)
            cosmic_example = cosmic_example[0] if cosmic_example else {}
            return {
                'count': cosmic_count,
                'example': cosmic_example,
                'url': COSMIC.get_cosmic_url(cosmic_example)
            }
        return None

    @staticmethod
    def search_gene(gene):
        if isinstance(gene, GeneReference):
            ref_seq = gene.transform_ref_seq(GeneReference.REF_TYPE_GENE)
            if ref_seq:
                cosmic_count = COSMIC.search_gene_db(GeneReference(ref_seq), only_count=True)
                if cosmic_count > 0:
                    return {
                        'count': cosmic_count,
                        'url': COSMIC.get_cosmic_url(ref_seq)
                    }
        return None

    @staticmethod
    def search_transcript(transcript):
        if isinstance(transcript, GeneReference):
            cosmic_count = COSMIC.search_transcript_db(transcript, only_count=True)
            if cosmic_count > 0:
                return {
                    'count': cosmic_count,
                    'url': COSMIC.get_cosmic_url(transcript.transform_ref_seq(GeneReference.REF_TYPE_ENST))
                }
        return None
