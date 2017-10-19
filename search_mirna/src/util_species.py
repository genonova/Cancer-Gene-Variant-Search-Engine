import os, json, requests

FILE_DIR = os.path.dirname(os.path.abspath(__file__))


class Species:
    SYMBOL_KEY = 0
    COMMON_NAME_KEY = 1
    SPECIES_KEY = 2
    SPECIES_ID_KEY = 3

    # This URL shall be updated in the future
    SOURCE_URL = 'http://www.targetscan.org/vert_70/docs/species100.html'
    SPECIES_FILE = os.path.join(FILE_DIR, 'util_species.json')
    SPECIES_ARRAY = []

    @staticmethod
    def get_species_array():
        if not Species.SPECIES_ARRAY:
            with open(Species.SPECIES_FILE, 'r') as f:
                Species.SPECIES_ARRAY = json.load(f)
        return Species.SPECIES_ARRAY

    @staticmethod
    def update_source():
        from bs4 import BeautifulSoup
        url = Species.SOURCE_URL

        r = requests.get(url)
        r_text = r.text

        soup = BeautifulSoup(r_text, 'html.parser')
        res = []
        header = True
        found_hsa = False
        for tr in soup.find_all('tr'):
            if header:
                header = False
                continue
            record = []
            for td in tr.find_all('td'):
                record.append(td.get_text())
            res.append(record)
            if record and record[0] == 'Hsa':
                found_hsa = True
        if found_hsa:
            Species.SPECIES_ARRAY = res
            with open(Species.SPECIES_FILE, 'w') as f:
                json.dump(res, f)
            return True
        else:
            return False

    @staticmethod
    def search_species(query):
        try:
            for species in Species.get_species_array():
                for val in species:
                    if val.lower() == str(query).lower():
                        return species
        except Exception as e:
            pass
        return []

    @staticmethod
    def transform_species_format(query, to_key):
        species = Species.search_species(query)
        if species:
            try:
                return species[to_key]
            except Exception as e:
                pass
        return None

# Species.update_source()