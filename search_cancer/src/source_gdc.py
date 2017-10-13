from util_variant import GeneVariant, GeneReference, map_aa_3to1, MyVariantUtil
from source_gene_source import GeneSource

import requests


class GDC(GeneSource):
    GDC_GENE_ROUTE = 'https://portal.gdc.cancer.gov/genes/'  # /BRAF/
    GDC_ID_ROUTE = 'https://portal.gdc.cancer.gov/ssms/'  # /Acute-Myeloid-Leukemia/PML-RARA/253/
    GDC_API_URL = 'https://api.gdc.cancer.gov/v0/all'

    @staticmethod
    def search_gene(gene):  # match to the summary page ?
        if isinstance(gene, GeneReference):
            ensg_gene = gene.transform_ref_seq(GeneReference.REF_TYPE_ENSG)
            if not ensg_gene:
                headers = {
                    'Referer': 'https://portal.gdc.cancer.gov/',
                    'Origin': 'https://portal.gdc.cancer.gov',
                    'Accept': 'application/json, text/javascript',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
                }

                r = requests.get(GDC.GDC_API_URL, headers=headers, params={'query': ensg_gene, 'size': 1})
                try:
                    res = r.json()
                    ensg_gene = res['data']['query']['hits']['gene_id']
                except Exception as e:
                    pass
            if ensg_gene:
                return {
                    'url': GDC.GDC_GENE_ROUTE + ensg_gene
                }
        return None

    @staticmethod
    def search_variant(variant):
        if isinstance(variant, GeneVariant):
            headers = {
                'Referer': 'https://portal.gdc.cancer.gov/',
                'Origin': 'https://portal.gdc.cancer.gov',
                'Accept': 'application/json, text/javascript',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
            }
            ssm_id = None
            def one_shot_query(query):
                r = requests.get(GDC.GDC_API_URL, headers=headers,
                                 params={'query': query, 'size': 1})
                try:
                    res = r.json()
                    ssm_id = res['data']['query']['hits'][0]['ssm_id']
                    if ssm_id:
                        return ssm_id
                except Exception as e:
                    return None

            # query on myvariant id (chr1:g.123123123C>T)
            mv_res = variant.get_myvariant_res()
            if mv_res:
                variant_id = MyVariantUtil.extract(mv_res, '_id')
                ssm_id = one_shot_query(variant_id)

            # fall back on gene name and protein info (BRAF A222V)
            if not ssm_id:
                gene_name = variant.transform_ref_seq(GeneReference.REF_TYPE_GENE)
                arr = variant.transform_variant(variant.ref_type, GeneVariant.INFO_TYPE_P)
                p_info = arr[1]
                if gene_name and p_info:
                    p_info = map_aa_3to1(p_info[2:])

                    p_id = gene_name + ' ' + p_info
                    ssm_id = one_shot_query(p_id)
            # fall back on cosmic id query
            if not ssm_id:
                if mv_res:
                    cosmic_id = MyVariantUtil.extract(mv_res, 'cosmic.cosmic_id')
                    r = requests.get(GDC.GDC_API_URL, headers=headers,
                                     params={'query': cosmic_id, 'size': 5})
                    try:
                        res = r.json()
                        found = False
                        for hit in res['data']['query']['hits']:
                            if found:
                                break
                            for candidate_id in hit['cosmic_id']:
                                if candidate_id == cosmic_id:
                                    ssm_id = hit['ssm_id']
                                    found = True
                                    break
                    except Exception as e:
                        pass
            if ssm_id:
                return {'url': GDC.GDC_ID_ROUTE + ssm_id}
        return None

    @staticmethod
    def search_transcript(transcript):
        return None


