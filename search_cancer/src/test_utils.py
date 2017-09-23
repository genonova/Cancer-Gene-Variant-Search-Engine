from util_variant import GeneVariant, MyVariantUtil
import pytest


class TestVariantUtil:
    def setup_method(self):
        pass

    def test_variant_init(self):
        with pytest.raises(ValueError) as excinfo:
            GeneVariant()
        with pytest.raises(ValueError) as excinfo:
            GeneVariant(ref_seq='NM_005957.4')
        with pytest.raises(ValueError) as excinfo:
            GeneVariant(var_info='c.665C>T')
        with pytest.raises(ValueError) as excinfo:
            GeneVariant(expr='ABC_1234')
        with pytest.raises(ValueError) as excinfo:
            GeneVariant(ref_seq='ABC_1234', var_info='c.665C>T')
        GeneVariant(ref_seq='NM_005957.4', var_info='c.665C>T')
        GeneVariant(expr='NM_005957.4:c.665C>T')

    def test_variant_type(self):
        variant = GeneVariant(expr='NM_005957.4:c.665C>T')
        assert variant.ref_type == GeneVariant.REF_TYPE_NM
        variant = GeneVariant(expr='ENST_005957.4:c.665C>T')
        assert variant.ref_type == GeneVariant.REF_TYPE_ENST
        variant = GeneVariant(expr='NC_005957.4:c.665C>T')
        assert variant.ref_type == GeneVariant.REF_TYPE_NC
        variant = GeneVariant(expr='NP_005957.4:c.665C>T')
        assert variant.ref_type == GeneVariant.REF_TYPE_NP
        variant = GeneVariant(expr='chr1:g.11856378G>A')
        assert variant.ref_type == GeneVariant.REF_TYPE_CHR

    def test_variant_transform_type_ENST(self):
        variant = GeneVariant(expr='NM_005957.4:c.665C>T')
        assert variant.transform_ref_seq(GeneVariant.REF_TYPE_ENST)

        variant = GeneVariant(expr='ENST00000376590:c.665C>T')
        assert variant.transform_ref_seq(GeneVariant.REF_TYPE_NM)

    def test_variant_transform_type_else(self):
        variant = GeneVariant(expr='chr1:g.11856378G>A')
        assert variant.transform_ref_seq(GeneVariant.REF_TYPE_NM)
        variant = GeneVariant(expr='chr1:g.11856378G>A')
        assert variant.transform_ref_seq(GeneVariant.REF_TYPE_NP)
        variant = GeneVariant(expr='chr1:g.11856378G>A')
        assert variant.transform_ref_seq(GeneVariant.REF_TYPE_NC)

        variant = GeneVariant(expr='NM_005957.4:c.665C>T')
        assert variant.transform_ref_seq(GeneVariant.REF_TYPE_CHR)
        variant = GeneVariant(expr='NP_005948.3:p.Ala222Val')
        assert variant.transform_ref_seq(GeneVariant.REF_TYPE_CHR)
        variant = GeneVariant(expr='NC_000001.10:g.11856378G>A')
        assert variant.transform_ref_seq(GeneVariant.REF_TYPE_CHR)

    def test_myvariant_query_transcript(self):
        assert len(MyVariantUtil.query('ENST00000376592')) >= 1
        assert len(MyVariantUtil.query('NP_005948.3')) >= 1
        assert len(MyVariantUtil.query('NM_005957')) >= 1
        '''
            "NM_005957.4:c.665C>T",
            "NP_005948.3:p.Ala222Val",
            "ENST00000376592.1:c.665G>A",
            "NC_000001.10:g.11856378G>A",
            "chr1:g.11856378G>A"
        '''
        # 1. all combination of transcripts:
        assert len(MyVariantUtil.query('NM_005957.4:c.665C>T')) == 1
        assert len(MyVariantUtil.query('NM_005957.4:p.Ala222Val')) == 1

        # NP will be covered by cosmic expressions
        assert len(MyVariantUtil.query('NP_005948.3:p.Ala222Val')) == 1
        assert len(MyVariantUtil.query('NP_005948.3:p.A222V')) == 1

        assert len(MyVariantUtil.query('ENST00000376592.1:c.665G>A')) == 1
        assert len(MyVariantUtil.query('ENST00000376592.1:p.A222V')) == 1
        assert len(MyVariantUtil.query('NC_000001.10:g.11856378G>A')) == 1
        assert len(MyVariantUtil.query('chr1:g.11856378G>A')) == 1

    def test_myvariant_query_gene(self):
        assert len(MyVariantUtil.query('MTHFR')) >= 1
        assert len(MyVariantUtil.query('MTHFR:c.665G>A')) >= 1

    def test_myvariant_extract(self):
        data = MyVariantUtil.query('chr1:g.11856378G>A')[0]
        assert MyVariantUtil.extract(data, GeneVariant.REF_TYPE_GENE) == 'MTHFR'
        assert MyVariantUtil.extract(data, GeneVariant.REF_TYPE_CHR) == 'chr1'
        assert MyVariantUtil.extract(data, GeneVariant.REF_TYPE_NC) == 'NC_000001.10'
        assert MyVariantUtil.extract(data, GeneVariant.REF_TYPE_NP) == 'NP_005948.3'
        assert MyVariantUtil.extract(data, GeneVariant.REF_TYPE_NM) == 'NM_005957.4'
        assert MyVariantUtil.extract(data, GeneVariant.REF_TYPE_ENST) == 'ENST00000376592'
        assert MyVariantUtil.extract(data, GeneVariant.REF_TYPE_ENSG) == 'ENSG00000177000'

        assert MyVariantUtil.extract(data, GeneVariant.INFO_TYPE_G) == 'g.11856378G>A'
        assert MyVariantUtil.extract(data, GeneVariant.INFO_TYPE_C) == 'c.665C>T'
        assert MyVariantUtil.extract(data, GeneVariant.INFO_TYPE_P) == 'p.Ala222Val'

import util_query

class TestQueryUtil:
    def setup_method(self):
        pass

    def test_add_limit(self):
        base_query = "SELECT * FROM COSMICTranscripts WHERE Gene_ID = %s"
        base_params = ('BRAF',)
        query, params = util_query.add_limit(base_query, base_params, 1, 3)
        assert query == base_query + " LIMIT %s,%s"
        assert params == ('BRAF', 1, 3,)