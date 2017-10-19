from util_species import Species


class TestSpecies:
    def test_search_species(self):
        assert Species.search_species('hsa')
        assert Species.search_species('Mmu')

    def test_transform_species_format(self):
        assert Species.transform_species_format('hsa', Species.SPECIES_ID_KEY) == '9606'

