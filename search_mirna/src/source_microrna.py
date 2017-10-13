from source_mirna_source import MiRNASource
import requests


# hsa-miR-28-3p
class MicroRNA(MiRNASource):
    SEARCH_ROUTE = 'http://www.microrna.org/microrna/getTargets.do?matureName=<HSA_MIRNA>&organism=9606'
    GENE_TD_FLAG = 'http://www.ensembl.org/Homo_sapiens/Gene/Summary'
    META = {'score_1_descr': 'mirSVR score'}

    @staticmethod
    def search_mirna(mirna):
        from bs4 import BeautifulSoup

        url = MicroRNA.SEARCH_ROUTE.replace('<HSA_MIRNA>', mirna)

        r = requests.get(url)
        r_text = r.text

        # TEST ONLY
        # with open('local.microrna_sample.html', 'w') as f:
        #     f.write(r_text)
        # with open('local.microrna_sample.html', 'r') as f:
        #     r_text = f.read()
        # /TEST ONLY

        soup = BeautifulSoup(r_text, 'html.parser')
        res = []
        for div in soup.find_all(attrs={'class': 'resultHeader'}):
            record = {
                'target_gene': '',
                'score_1': ''
            }
            try:
                # Find gene name
                tds = div.find('table').find_all('td')
                record['target_gene'] = tds[1].get_text().split('\n')[0]
            except Exception as e:
                continue

            # Find prediction score
            min_score = 0
            for right_div in div.find_all(
                    attrs={'class': 'right'}):  # find the minimum score among alternative isoforms
                try:
                    score = float(right_div.get_text())
                    min_score = min(min_score, score)
                except Exception as e:
                    pass
            record['score_1'] = min_score
            res.append(record)
        return res

# temp = MicroRNA.search_mirna('hsa-miR-28-3p')
# print len(temp)
