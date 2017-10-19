from source_target_scan import TargetScan


class TestTargetScan:
    def test_search_mirna(self):
        assert not TargetScan.search_mirna('mmu-miR-132-5p_L-1R+1')
        assert TargetScan.search_mirna('mmu-miR-132-5p')


from source_microrna import MicroRNA


class TestMicroRNA:
    def test_search_mirna(self):
        assert not MicroRNA.search_mirna('mmu-miR-132-5p')
        assert MicroRNA.search_mirna('mmu-miR-1839-5p')
