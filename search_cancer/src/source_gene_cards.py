from util_variant import GeneVariant, GeneReference
from source_gene_source import GeneSource
import urllib


class GeneCards(GeneSource):
    GENE_ROUTE = 'http://www.genecards.org/cgi-bin/carddisp.pl?gene='

    @staticmethod
    def get_gene_url(reference):
        if isinstance(reference, GeneReference):
            ref_seq = reference.ref_seq
            if reference.ref_type != GeneVariant.REF_TYPE_GENE:
                ref_seq = reference.transform_ref_seq(GeneVariant.REF_TYPE_GENE)
                if not ref_seq:
                    return None
            return GeneCards.GENE_ROUTE + urllib.quote(ref_seq)
        return None

    @staticmethod
    def search_gene(gene):
        url = GeneCards.get_gene_url(gene)
        if url:
            return {
                'url': url
            }
        return {}

    @staticmethod
    def search_variant(variant):
        return {}

    @staticmethod
    def search_transcript(transcript):
        return {}
