from source_mirna_source import MiRNASource
from util_species import Species

import requests


# hsa-miR-28-3p
class MicroRNA(MiRNASource):
    SEARCH_ROUTE = 'http://www.microrna.org/microrna/getTargets.do?matureName=<HSA_MIRNA>&organism=<SPECIES_ID>'
    GENE_TD_FLAG = 'http://www.ensembl.org/Homo_sapiens/Gene/Summary'
    META = {'score_1_descr': 'mirSVR score'}

    @staticmethod
    def search_mirna(mirna, count=200):
        from bs4 import BeautifulSoup
        species_id = Species.transform_species_format(mirna.split('-')[0], Species.SPECIES_ID_KEY)
        res = []
        if species_id:
            url = MicroRNA.SEARCH_ROUTE.replace('<HSA_MIRNA>', mirna).replace('<SPECIES_ID>', species_id)

            r = requests.get(url)
            r_text = r.text

            # TEST ONLY
            # with open('local.microrna_sample.html', 'w') as f:
            #     f.write(r_text)
            # with open('local.microrna_sample.html', 'r') as f:
            #     r_text = f.read()
            # /TEST ONLY

            soup = BeautifulSoup(r_text, 'html.parser')
            for div in soup.find_all(attrs={'class': 'resultHeader'}):
                if count == 0:
                    break
                record = {
                    'symbol': '',
                    'score_1': ''
                }
                try:
                    # Find gene name
                    tds = div.find('table').find_all('td')
                    record['symbol'] = tds[1].get_text().split('\n')[0]
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
                count -= 1
        return res

# temp = MicroRNA.search_mirna('hsa-miR-28-3p')
# print len(temp)
