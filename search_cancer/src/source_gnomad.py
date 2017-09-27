from util_variant import GeneVariant, GeneReference, map_chr_to_str
from source_gene_source import GeneSource
from config import config

import urllib

class GnomAD(GeneSource):
    VARIANT_ROUTE = 'http://gnomad.broadinstitute.org/variant/'
    TRANSCRIPT_ROUTE = 'http://gnomad.broadinstitute.org/transcript/'
    GENE_ROUTE = 'http://gnomad.broadinstitute.org/gene/'

    @staticmethod
    def get_variant_url(variant):
        if isinstance(variant, GeneVariant):
            chr_pos_ref_alt = variant.transform_variant(GeneVariant.TRANSFORM_CHR_POS_REF_ALT)
            if chr_pos_ref_alt:
                query = '-'.join(chr_pos_ref_alt)
                return GnomAD.VARIANT_ROUTE + urllib.quote(query)
        return

    @staticmethod
    def get_trascript_url(reference):
        if isinstance(reference, GeneReference):
            ref_seq = reference.ref_seq
            if reference.ref_type != GeneVariant.REF_TYPE_ENST:
                ref_seq = reference.transform_ref_seq(GeneVariant.REF_TYPE_ENST)
                if not ref_seq:
                    return None
            return GnomAD.TRANSCRIPT_ROUTE + urllib.quote(ref_seq)
        return None

    @staticmethod
    def get_gene_url(reference):
        if isinstance(reference, GeneReference):
            ref_seq = reference.ref_seq
            if reference.ref_type != GeneVariant.REF_TYPE_ENSG:
                ref_seq = reference.transform_ref_seq(GeneVariant.REF_TYPE_ENSG)
                if not ref_seq:
                    return None
            return GnomAD.GENE_ROUTE + urllib.quote(ref_seq)
        return None

    @staticmethod
    def search_variant_db(variant):
        if isinstance(variant, GeneVariant):
            chr_pos_ref_alt = variant.transform_variant(GeneVariant.TRANSFORM_CHR_POS_REF_ALT)
            if chr_pos_ref_alt:
                gnomad_id = '-'.join(chr_pos_ref_alt)
                chr_num = map_chr_to_str(chr_pos_ref_alt[0])
                table_name = 'gnomad_variants_info_sites_' + chr_num
                query = "SELECT * FROM " + table_name + " WHERE Variant_ID=%s "
                params = (gnomad_id,)

                cancer_db = config.connect_db(config.CANCER_DB_KEY)
                cursor = cancer_db.cursor()
                cursor.execute(query, params)
                res = cursor.fetchone()
                return res
        return None

    @staticmethod
    def search_gene(gene):
        url = GnomAD.get_gene_url(gene)
        if url:
            return {
                'url': url
            }
        return {}

    @staticmethod
    def search_variant(variant):
        url = GnomAD.get_variant_url(variant)
        if url:
            return {
                'url': url,
                'match': GnomAD.search_variant_db(variant)
            }
        return None

    @staticmethod
    def search_transcript(transcript):
        url = GnomAD.get_trascript_url(transcript)
        if url:
            return {
                'url': url
            }
        return None
