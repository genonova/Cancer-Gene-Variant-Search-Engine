from util_variant import GeneVariant, GeneReference, MyVariantUtil
from source_gene_source import GeneSource
import urllib

class DECIPHER(GeneSource):
    QUERY_ROUTE = 'https://decipher.sanger.ac.uk/search?q=<query>#consented-patients/results'

    @staticmethod
    def get_variant_url(variant):
        if isinstance(variant, GeneVariant):
            chr_pos = variant.transform_variant(GeneVariant.TRANSFORM_CHR_POS)
            if chr_pos:
                return DECIPHER.QUERY_ROUTE.replace('<query>', urllib.quote(chr_pos[0] + ':' + chr_pos[1]))
        return None

    @staticmethod
    def get_gene_url(gene):
        if isinstance(gene, GeneReference):
            gene_name = gene.transform_ref_seq(GeneReference.REF_TYPE_GENE)
            if gene_name:
                return DECIPHER.QUERY_ROUTE.replace('<query>', gene_name)
        return None

    @staticmethod
    def search_gene(gene):
        url = DECIPHER.get_gene_url(gene)
        if url:
            return {
                'url': url
            }
        return {}

    @staticmethod
    def search_transcript(transcript):
        return None  # DECIPHER seems to not work

    @staticmethod
    def search_variant(variant):
        url = DECIPHER.get_variant_url(variant)
        if url:
            return {
                'url': url
            }
        return {}

        # search_url = 'http://rest.genenames.org/fetch/symbol/BRAF'
        # r = requests.get(search_url,
        #                  headers=HGNC.HEADER_JSON).json()
        # import pprint
        # pprint.pprint(r)
