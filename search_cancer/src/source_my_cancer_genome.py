from util_variant import GeneVariant, GeneReference
from source_gene_source import GeneSource

import requests, json, os

MCG_FILE_DIR = os.path.dirname(os.path.abspath(__file__))


class MyCancerGenome(GeneSource):
    GENE_ROUTE = 'https://www.mycancergenome.org/content/gene/'  # /BRAF/
    DISEASE_VARIANT_ROUTE = 'https://www.mycancergenome.org/content/disease/'  # /Acute-Myeloid-Leukemia/PML-RARA/253/
    GENE_FILE = os.path.join(MCG_FILE_DIR, 'source_my_cancer_genome_gene.json')
    DISEASE_FILE = os.path.join(MCG_FILE_DIR, 'source_my_cancer_genome_disease.json')
    VARIANT_DICT = None

    @staticmethod
    def get_gene_dict():
        if not MyCancerGenome.VARIANT_DICT:
            with open(MyCancerGenome.GENE_FILE, 'r') as f:
                gene_dict = json.load(f)
                for gene_name in gene_dict:
                    variant_info = gene_dict[gene_name]
                    for variant in variant_info:
                        variant_details = variant_info[variant]
                        new_details = []
                        for detail in variant_details:
                            disease = detail['disease']
                            gene = detail['gene']
                            variant_id = detail['variant_id']
                            temp = {}
                            temp['disease'] = disease
                            disease_path = '-'.join(disease.split(' '))
                            temp['url'] = MyCancerGenome.DISEASE_VARIANT_ROUTE + disease_path + '/' + gene + '/' + str(variant_id)
                            new_details.append(temp)
                        variant_info[variant] = new_details
                MyCancerGenome.VARIANT_DICT = gene_dict
        return MyCancerGenome.VARIANT_DICT

    @staticmethod
    def search_variant_local(variant):
        if isinstance(variant, GeneVariant):
            gene_dict = MyCancerGenome.get_gene_dict()
            gene_name = variant.transform_ref_seq(GeneReference.REF_TYPE_GENE)
            if gene_name and gene_name in gene_dict:
                res = {
                    'url': MyCancerGenome.GENE_ROUTE + gene_name,
                    'variants': gene_dict[gene_name],
                    'variant_match': False
                }
                cdna = variant.transform_variant(variant.ref_type, GeneVariant.INFO_TYPE_C)[1]
                if cdna:
                    variants = gene_dict[gene_name]
                    for variant in variants:
                        if variant.startswith(cdna):
                            res['variant_match'] = True
                            res['variants'] = {variant: variants[variant]}
                return res
        return {}

    @staticmethod
    def search_gene_local(gene):
        if isinstance(gene, GeneReference):
            gene_dict = MyCancerGenome.get_gene_dict()
            gene_name = gene.transform_ref_seq(GeneReference.REF_TYPE_GENE)
            if gene_name and gene_name in gene_dict:
                return {
                    'url': MyCancerGenome.GENE_ROUTE + gene_name,
                    'variants': gene_dict[gene_name],
                    'variant_match': False
                }
        return {}

    @staticmethod
    def update_source():
        '''1. Parse the HTML to get all the diseases'''
        DISEASE_DROP_DOWN_KEY = 'DiseaseDropdown'
        ROOT_URL = 'https://www.mycancergenome.org'
        res = {}
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
        }
        r = requests.get(ROOT_URL, headers=headers)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        disease_dict = {}
        for option in soup.find(id=DISEASE_DROP_DOWN_KEY).find_all('option'):
            d_id = option['value']
            if d_id:
                disease = option.get_text()
                disease_dict[d_id] = {}
                disease_dict[d_id]['disease'] = disease
        '''
        Cache
        disease_dict = {u'24': {'disease': u'Prostate Cancer'},
                        u'20': {'disease': u'Acute Myeloid Leukemia'}, u'21': {'disease': u'Glioma'},
                        u'22': {'disease': u'Myelodysplastic Syndromes'},
                        u'23': {'disease': u'Chronic Lymphocytic Leukemia'}, u'1': {'disease': u'Breast Cancer'},
                        u'3': {'disease': u'Colorectal Cancer'}, u'2': {'disease': u'Lung Cancer'},
                        u'5': {'disease': u'Melanoma'}, u'4': {'disease': u'GIST'},
                        u'7': {'disease': u'Thyroid Cancer'}, u'6': {'disease': u'Thymic Carcinoma'},
                        u'9': {'disease': u'Gastric Cancer'}, u'11': {'disease': u'Basal Cell Carcinoma'},
                        u'10': {'disease': u'Ovarian Cancer'}, u'13': {'disease': u'Neuroblastoma'},
                        u'12': {'disease': u'Medulloblastoma'}, u'15': {'disease': u'Anaplastic Large Cell Lymphoma'},
                        u'14': {'disease': u'Rhabdomyosarcoma'},
                        u'17': {'disease': u'Inflammatory Myofibroblastic Tumor'},
                        u'16': {'disease': u'Acute Lymphoblastic Leukemia'}, u'19': {'disease': u'Bladder Cancer'},
                        u'18': {'disease': u'Chronic Myeloid Leukemia'}}
        '''
        '''2. Use API to get all genes related to those diseases'''
        GET_GENE_URL = 'https://www.mycancergenome.org/api/sp-genome/get-genes-for-disease/'
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
            'X-Requested-With': 'XMLHttpRequest'
        }
        for d_id in disease_dict:
            if d_id:
                r = requests.get(GET_GENE_URL, headers=headers, params={'disease': d_id})
                if r.text:
                    gene_dict = r.json()
                    disease_dict[d_id]['gene_dict'] = gene_dict
        '''
        Cache
        disease_dict = {u'24': {'disease': u'Prostate Cancer', 'gene_dict': {u'AR': 42}},
                        u'20': {'disease': u'Acute Myeloid Leukemia',
                                'gene_dict': {u'DEK-NUP214': 33, u'DNMT3A': 39, u'RPN1-EVI1': 34, u'CBFB-MYH11': 30,
                                              u'RUNX1-RUNX1T1': 29, u'PML-RARA': 31, u'IDH2': 37, u'IDH1': 36,
                                              u'MLL-MLLT3': 32, u'KIT': 19, u'RBM15-MKL1': 35, u'FLT3': 38}},
                        u'21': {'disease': u'Glioma', 'gene_dict': {u'IDH2': 37, u'IDH1': 36, u'BRAF': 4}},
                        u'22': {'disease': u'Myelodysplastic Syndromes',
                                'gene_dict': {u'ZRSR2': 56, u'DNMT3A': 39, u'TP53': 54, u'BCOR': 45, u'ETV6': 46,
                                              u'ASXL1': 44, u'TET2': 53, u'SRSF2': 51, u'SF3B1': 50, u'STAG2': 52,
                                              u'EZH2': 47, u'NF1': 48, u'U2AF1': 55, u'RUNX1': 49}},
                        u'23': {'disease': u'Chronic Lymphocytic Leukemia',
                                'gene_dict': {u'BIRC3': 109, u'NOTCH1': 428}}, u'1': {'disease': u'Breast Cancer',
                                                                                      'gene_dict': {u'ERBB2': 9,
                                                                                                    u'ESR1': 27,
                                                                                                    u'PTEN': 3,
                                                                                                    u'PIK3CA': 2,
                                                                                                    u'AKT1': 1,
                                                                                                    u'AR': 42,
                                                                                                    u'PGR': 28,
                                                                                                    u'FGFR2': 41,
                                                                                                    u'FGFR3': 243,
                                                                                                    u'FGFR1': 7}},
                        u'3': {'disease': u'Colorectal Cancer',
                               'gene_dict': {u'AKT1': 1, u'SMAD4': 21, u'PIK3CA': 2, u'NRAS': 13, u'PTEN': 3,
                                             u'BRAF': 4, u'KRAS': 10}}, u'2': {'disease': u'Lung Cancer',
                                                                               'gene_dict': {u'ERBB2': 9,
                                                                                             u'RICTOR': 528, u'ALK': 5,
                                                                                             u'MET': 12, u'DDR2': 6,
                                                                                             u'CD274': 140, u'NRAS': 13,
                                                                                             u'EGFR': 8, u'NTRK1': 43,
                                                                                             u'RET': 20, u'ROS1': 14,
                                                                                             u'PTEN': 3, u'AKT1': 1,
                                                                                             u'MAP2K1': 11, u'BRAF': 4,
                                                                                             u'PIK3CA': 2, u'KRAS': 10,
                                                                                             u'FGFR3': 243,
                                                                                             u'FGFR1': 7}},
                        u'5': {'disease': u'Melanoma',
                               'gene_dict': {u'GNAQ': 17, u'NRAS': 13, u'KIT': 19, u'CTNNB1': 15, u'MAP2K1': 11,
                                             u'BRAF': 4, u'NF1': 48, u'GNA11': 16}},
                        u'4': {'disease': u'GIST', 'gene_dict': {u'PDGFRA': 18, u'BRAF': 4, u'KIT': 19}},
                        u'7': {'disease': u'Thyroid Cancer',
                               'gene_dict': {u'HRAS': 40, u'NRAS': 13, u'BRAF': 4, u'RET': 20, u'KRAS': 10}},
                        u'6': {'disease': u'Thymic Carcinoma', 'gene_dict': {u'KIT': 19}},
                        u'9': {'disease': u'Gastric Cancer', 'gene_dict': {u'ERBB2': 9}},
                        u'11': {'disease': u'Basal Cell Carcinoma', 'gene_dict': {u'SMO': 22}},
                        u'10': {'disease': u'Ovarian Cancer',
                                'gene_dict': {u'PTEN': 3, u'PIK3CA': 2, u'BRAF': 4, u'KRAS': 10}},
                        u'13': {'disease': u'Neuroblastoma', 'gene_dict': {u'ALK': 5}},
                        u'12': {'disease': u'Medulloblastoma', 'gene_dict': {u'SMO': 22}},
                        u'15': {'disease': u'Anaplastic Large Cell Lymphoma', 'gene_dict': {u'ALK': 5}},
                        u'14': {'disease': u'Rhabdomyosarcoma', 'gene_dict': {u'ALK': 5}},
                        u'17': {'disease': u'Inflammatory Myofibroblastic Tumor', 'gene_dict': {u'ALK': 5}},
                        u'16': {'disease': u'Acute Lymphoblastic Leukemia', 'gene_dict': {u'JAK2': 24, u'CRLF2': 23}},
                        u'19': {'disease': u'Bladder Cancer', 'gene_dict': {u'FGFR3': 243, u'TSC1': 26}},
                        u'18': {'disease': u'Chronic Myeloid Leukemia', 'gene_dict': {u'BCR-ABL1': 25}}}
        '''
        '''3. Use API to get all variants related to those genes and do reverse indexing'''
        GET_VARIANT_URL = 'https://www.mycancergenome.org/api/sp-genome/get-variants-for-gene-and-disease/'
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
            'X-Requested-With': 'XMLHttpRequest'
        }
        res_dict = {}
        for d_id in disease_dict:
            disease_info = disease_dict[d_id]
            disease = disease_info['disease']
            if 'gene_dict' in disease_info:
                gene_dict = disease_info['gene_dict']
                for gene in gene_dict:
                    gene_id = gene_dict[gene]
                    gene_dict[gene] = {}
                    r = requests.get(GET_VARIANT_URL, headers=headers, params={'disease': d_id, 'gene': gene_id})
                    if r.text:
                        variant_dict = r.json()
                        gene_dict[gene]['gene_id'] = gene_id
                        gene_dict[gene]['variant_dict'] = variant_dict
                        if not gene in res_dict:
                            res_dict[gene] = {}
                        for variant in variant_dict:  # BRAF c.1801A>G (K601E)
                            first_blank_index = variant.find(' ')
                            if first_blank_index != -1:
                                var_info = variant[first_blank_index + 1:]
                            else:
                                var_info = variant

                            if var_info not in res_dict[gene]:
                                res_dict[gene][var_info] = []

                            variant_info = {}
                            variant_info['variant_id'] = variant_dict[variant]
                            variant_info['disease'] = disease
                            variant_info['disease_id'] = d_id
                            variant_info['gene'] = gene
                            variant_info['gene_id'] = gene_id
                            res_dict[gene][var_info].append(variant_info)
        ''' Write out to files'''
        if res_dict:
            with open(MyCancerGenome.GENE_FILE, mode='w') as f:
                json.dump(res_dict, f)
            f.close()
            with open(MyCancerGenome.DISEASE_FILE, mode='w') as f:
                json.dump(disease_dict, f)
            f.close()
        return True

    @staticmethod
    def search_gene(gene):  # match to the summary page ?
        return MyCancerGenome.search_gene_local(gene)

    @staticmethod
    def search_variant(variant):
        return MyCancerGenome.search_variant_local(variant)

    @staticmethod
    def search_transcript(transcript):
        return None


