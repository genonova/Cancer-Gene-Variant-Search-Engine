from util_variant import GeneVariant, GeneReference
from source_gene_source import GeneSource
import requests
import urllib


class HGNC(GeneSource):
    FETCH_API = 'http://rest.genenames.org/fetch/'
    SEARCH_API = 'http://rest.genenames.org/search/'
    SEARCH_ROUTE = 'http://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id='

    FIELD_ENTREZ_ID = 'entrez_id'
    FIELD_ENSEMBLE_GENE_ID = 'ensembl_gene_id'
    FIELD_SYMBOL = 'symbol'
    FIELD_ALIAS_SYMBOL = 'alias_symbol'

    HEADER_JSON = {
        'Accept': 'application/json'
    }

    @staticmethod
    def search_gene(gene):
        if isinstance(gene, GeneReference):
            to_types = [GeneReference.REF_TYPE_GENE, GeneReference.REF_TYPE_ENSG]
            for to_type in to_types:
                ref_seq = GeneReference.transform_ref_seq(gene.ref_seq, to_type)
                if ref_seq:
                    fields = []
                    if to_type == GeneReference.REF_TYPE_GENE:
                        fields = [HGNC.FIELD_SYMBOL, HGNC.FIELD_ALIAS_SYMBOL]
                    elif to_type == GeneReference.REF_TYPE_ENSG:
                        fields = [HGNC.FIELD_ENSEMBLE_GENE_ID]
                    for field in fields:
                        if field:
                            search_url = HGNC.FETCH_API + field + '/' + urllib.quote(ref_seq)
                            r = requests.get(search_url,
                                             headers=HGNC.HEADER_JSON).json()
                            try:
                                res = r['response']['docs'][0]
                                if res:
                                    hgnc_id = res['hgnc_id']
                                    res['url'] = HGNC.SEARCH_ROUTE + hgnc_id
                                    return res
                            except Exception as e:
                                pass
        return {}

    @staticmethod
    def search_transcript(transcript):
        return None

    @staticmethod
    def search_variant(variant):
        return None

# search_url = 'http://rest.genenames.org/fetch/symbol/BRAF'
# r = requests.get(search_url,
#                  headers=HGNC.HEADER_JSON).json()
# import pprint
# pprint.pprint(r)