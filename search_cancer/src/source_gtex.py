from util_variant import GeneVariant, GeneReference, MyVariantUtil
from source_gene_source import GeneSource


class GTEx(GeneSource):
    VARIANT_ROUTE = 'https://www.gtexportal.org/home/snp/'
    GENE_ROUTE = 'https://www.gtexportal.org/home/gene/'

    @staticmethod
    def get_variant_url(variant):
        if isinstance(variant, GeneVariant):
            for field in MyVariantUtil.SNP_ID_FIELDS:
                rs_id = MyVariantUtil.extract(variant.get_myvariant_res(), field)
                if rs_id:
                    return GTEx.VARIANT_ROUTE + rs_id
        return None

    @staticmethod
    def get_gene_url(gene):
        if isinstance(gene, GeneReference):
            gene_name = gene.transform_ref_seq(GeneReference.REF_TYPE_GENE)
            if gene_name:
                return GTEx.GENE_ROUTE + gene_name
        return None

    @staticmethod
    def search_gene(gene):
        url = GTEx.get_gene_url(gene)
        if url:
            return {
                'url': url
            }
        return {}

    @staticmethod
    def search_transcript(transcript):
        return None

    @staticmethod
    def search_variant(variant):
        url = GTEx.get_variant_url(variant)
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
