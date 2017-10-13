from source_mirna_source import MiRNASource
import requests


# hsa-miR-28-3p
class TargetScan(MiRNASource):
    SEARCH_ROUTE = 'http://www.targetscan.org/cgi-bin/targetscan/vert_71/targetscan.cgi?species=Human&gid=&mir_sc=&mir_c=&mir_nc=&mir_vnc=&mirg='
    GENE_TD_FLAG = 'http://www.ensembl.org/Homo_sapiens/Gene/Summary'
    META = {'score_1_descr': 'Cumulative weighted context++ score'}
    @staticmethod
    def search_mirna(mirna):
        from bs4 import BeautifulSoup

        url = TargetScan.SEARCH_ROUTE + mirna

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
        res = []
        while i < len(tds):
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
            i += 1
        return res


temp = TargetScan.search_mirna('miR-16-5p')
# print len(temp)
