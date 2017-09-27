from util_variant import GeneVariant, GeneReference

from source_civic import CIViC


class TestCIViC:
    def test_search_gene(self):
        gene = GeneReference('BRAF')
        assert CIViC.search_gene(gene)
        gene = GeneReference('ENSG00000157764')
        assert CIViC.search_gene(gene)

    def test_search_variant(self):
        variant = GeneVariant('chr1:g.11856378G>A')
        assert CIViC.search_variant(variant)

from source_gtex import GTEx

class TestGTex:
    def test_search_gene(self):
        gene = GeneReference('ENSG00000157764')
        assert GTEx.get_gene_url(gene) == GTEx.GENE_ROUTE + 'BRAF'

    def test_search_variant(self):
        variant = GeneVariant('chr1:g.11856378G>A')
        assert GTEx.get_variant_url(variant) == GTEx.VARIANT_ROUTE + 'rs1801133'

from source_cosmic import COSMIC

from source_decipher import DECIPHER

class TestDECIPHER:
    def test_search_gene(self):
        gene = GeneReference('ENSG00000157764')
        assert DECIPHER.get_gene_url(gene) == 'https://decipher.sanger.ac.uk/search?q=BRAF#consented-patients/results'

    def test_search_variant(self):
        variant = GeneVariant('chr1:g.11856378G>A')
        assert DECIPHER.get_variant_url(variant) == 'https://decipher.sanger.ac.uk/search?q=1%3A11856378#consented-patients/results'


class TestCOSMIC:
    def test_search_variants(self):
        variant = GeneVariant("chr1:g.114716127G>A")
        assert COSMIC.search_variant_db(variant=variant, only_count=True) > 0

        # cDNA
        variant = GeneVariant("ENST00000376236:c.1089C>T")
        assert COSMIC.search_variant_db(variant=variant, only_count=True) > 0

        variant = GeneVariant("ENST00000376236:p.N363N")
        assert COSMIC.search_variant_db(variant=variant, only_count=True) > 0

        variant = GeneVariant("ENST00000376236:p.Asn363Asn")
        assert COSMIC.search_variant_db(variant=variant, only_count=True) > 0

    def test_search_transcript(self):
        transcript = GeneReference("ENST00000376236")
        assert COSMIC.search_transcript_db(transcript, only_count=True) > 0

    def test_search_gene(self):
        gene = GeneReference('KIT')
        assert COSMIC.gene_exist(gene)
        assert COSMIC.search_gene_db(gene, only_count=True) > 0

    def test_get_cosmic_url(self):
        assert COSMIC.get_cosmic_url('COSM1') == COSMIC.ID_ROUTE + '1'
        assert COSMIC.get_cosmic_url({'ID_Mutation': 'COSM1'}) == COSMIC.ID_ROUTE + '1'
        assert not COSMIC.get_cosmic_url({})
        assert COSMIC.get_cosmic_url('abc111') == COSMIC.QUERY_ROUTE + 'abc111'
        assert not COSMIC.get_cosmic_url(123)
        assert COSMIC.get_cosmic_url(u'BRAF') == COSMIC.QUERY_ROUTE + 'BRAF'

from source_my_cancer_genome import MyCancerGenome

class TestMyCancerGenome:
    def test_search_variant_local(self):
        variant = GeneVariant('PTEN:c.697C>T')
        res = MyCancerGenome.search_variant_local(variant)
        assert res and res['variant_match'] == True and res['url'] == 'https://www.mycancergenome.org/content/gene/PTEN'

    def test_search_gene_local(self):
        gene = GeneReference('ENSG00000157764')
        assert MyCancerGenome.search_gene_local(gene)

from source_gnomad import GnomAD


class TestGnomAD:
    def test_get_variant_url(self):
        variant = GeneVariant('chr1:g.11856378G>A')
        assert GnomAD.get_variant_url(variant) == GnomAD.VARIANT_ROUTE + '1-11856378-G-A'
        variant = GeneVariant('NM_001098210.1:c.241+6_241+7del')
        assert GnomAD.get_variant_url(variant) == GnomAD.VARIANT_ROUTE + '3-41266247-AAG-A'
        variant = GeneVariant('NC_000003.11:g.41266248_41266249delAG')
        assert GnomAD.get_variant_url(variant) == GnomAD.VARIANT_ROUTE + '3-41266247-AAG-A'

    def test_get_gene_url(self):
        gene = GeneReference('BRAF')
        assert GnomAD.get_gene_url(gene) == GnomAD.GENE_ROUTE + 'ENSG00000157764'

from source_gene_cards import GeneCards

class TestGeneCards:
    def test_get_gene_url(self):
        gene = GeneReference('ENSG00000157764')
        assert GeneCards.get_gene_url(gene) == GeneCards.GENE_ROUTE + 'BRAF'

from source_hgnc import HGNC


class TestHGNC:
    def test_search_gene(self):
        gene = GeneReference('BRAF')
        assert HGNC.search_gene(gene)

        gene = GeneReference('BRAF1')
        assert HGNC.search_gene(gene)

        gene = GeneReference('ENSG00000157764')
        assert HGNC.search_gene(gene)
