from source_gene_source import GeneSource
from util_variant import GeneVariant, GeneReference, MyVariantUtil
import requests


class CIViC(GeneSource):
    VARIANT_ROUTE = 'https://civic.genome.wustl.edu/events/genes/<gene_id>/summary/variants/<variant_id>/summary'
    GENE_ROUTE = 'https://civic.genome.wustl.edu/events/genes/<gene_id>/summary'
    GENE_API = 'https://civic.genome.wustl.edu/api/genes/<gene>?identifier_type=entrez_symbol'
    VARIANT_API = 'https://civic.genome.wustl.edu/api/variants/<variant_id>'

    @staticmethod
    def search_variant(variant):
        if isinstance(variant, GeneVariant):
            mv_res = variant.get_myvariant_res()
            if mv_res:
                '''This logic is redundant as myvariant already gives civic data
                but we can retrieve latest data from CIViC API'''
                gene_id = MyVariantUtil.extract(mv_res, 'civic.gene_id')
                variant_id = MyVariantUtil.extract(mv_res, 'civic.variant_id')
                if type(gene_id) == int and type(variant_id) == int:
                    response = requests.get(CIViC.VARIANT_API.replace('<variant_id>', str(variant_id)))
                    if response.status_code == 200:
                        res = response.json()
                    else:
                        res = {}
                    res['url'] = CIViC.VARIANT_ROUTE.replace('<variant_id>', str(variant_id)).replace('<gene_id>',
                                                                                                      str(gene_id))
                    return res
        return None
    @staticmethod
    def search_gene(gene):
        if isinstance(gene, GeneReference):
            ref_seq = gene.transform_ref_seq(GeneReference.REF_TYPE_GENE)
            if ref_seq:
                response = requests.get(CIViC.GENE_API.replace('<gene>', ref_seq))
                if response.status_code == 200:
                    res = response.json()
                    res['url'] = CIViC.GENE_ROUTE.replace('<gene_id>', str(res['id']))
                    return res
        return None

    @staticmethod
    def search_transcript(transcript):
        return None
