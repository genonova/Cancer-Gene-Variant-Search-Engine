from source_mirna_source import MiRNASource
from util_species import Species
import requests


# hsa-miR-28-3p
# mmu-miR-132-5p_L-1R+1
class TargetScan(MiRNASource):
    SEARCH_ROUTE = 'http://www.targetscan.org/cgi-bin/targetscan/vert_71/targetscan.cgi?species=<SPECIES_COMMON_NAME>&gid=&mir_sc=&mir_c=&mir_nc=&mir_vnc=&mirg='
    GENE_TD_FLAG = 'http://www.ensembl.org/Homo_sapiens/Gene/Summary'
    META = {'score_1_descr': 'Cumulative weighted context++ score'}

    @staticmethod
    def search_mirna(mirna, count=20):
        from bs4 import BeautifulSoup
        species_common_name = Species.transform_species_format(mirna.split('-')[0], Species.COMMON_NAME_KEY)
        res = []
        if species_common_name:
            url = TargetScan.SEARCH_ROUTE.replace('<SPECIES_COMMON_NAME>', species_common_name) + mirna

            r = requests.get(url)
            r_text = r.text

            # TEST ONLY
            # with open('local.target_scan_sample.html', 'w') as f:
            #     f.write(r_text)
            # with open('local.target_scan_sample.html', 'r') as f:
            #     r_text = f.read()
            # /TEST ONLY

            soup = BeautifulSoup(r_text, 'html.parser')

            tds = soup.find_all('td')
            i = 0
            while i < len(tds):
                if count == 0:
                    break
                td = tds[i]
                a = td.find('a')
                if a and a['href'].startswith(TargetScan.GENE_TD_FLAG):
                    record = {
                        'target_gene': '',
                        'score_1': ''
                    }
                    try:
                        record['target_gene'] = tds[i].get_text()
                        record['score_1'] = float(tds[i + 15].get_text())
                    except Exception as e:
                        pass
                    if record['target_gene']:
                        res.append(record)
                        count -= 1
                i += 1
        return res

# temp = TargetScan.search_mirna('hsa-miR-16-5p')
# print len(temp)
