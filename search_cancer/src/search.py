from source_cosmic import COSMIC
from source_gnomad import GnomAD
from source_civic import CIViC
from source_hgnc import HGNC
from source_gene_cards import GeneCards
from source_gtex import GTEx
from source_decipher import DECIPHER

from util_variant import GeneVariant, GeneReference

from django.utils.translation import ugettext_lazy as _

import time

TYPE_GENE = 0
TYPE_VARIANT = 1
TYPE_TRANSCRIPT = 2

GENE_SOURCES = {COSMIC, GnomAD, CIViC, HGNC, GeneCards, GTEx, DECIPHER}
MY_VARIANT = 'myvariant'
IDS_KEY = 'ids'
SOURCE_NAMES_KEY = 'source_names'
REPORT_KEY = 'report'
GRANTHAM_SCORE_KEY = 'grantham_score'
GRANTHAM_INFO_KEY = 'grantham_info'
REF_AA_KEY = 'ref_aa'
ALT_AA_KEY = 'alt_aa'
SOURCE_URLS_KEY = 'source_urls'

def search_sources(target_str, search_type):
    if search_type == TYPE_GENE or search_type == TYPE_TRANSCRIPT:
        target = GeneReference(target_str)
    elif search_type == TYPE_VARIANT:
        target = GeneVariant(target_str)
    else:
        raise ValueError("Invalid search type")

    mv_res = target.get_myvariant_res()
    res = {
        MY_VARIANT: mv_res,
        SOURCE_NAMES_KEY: {}
    }

    for source in GENE_SOURCES:
        time_start = time.clock()
        if search_type == TYPE_GENE:
            source_res = source.search_gene(target)
        elif search_type == TYPE_VARIANT:
            source_res = source.search_variant(target)
        elif search_type == TYPE_TRANSCRIPT:
            source_res = source.search_transcript(target)

        if search_type == TYPE_VARIANT and not source_res:
            source_res = source.search_transcript(target)
            if source_res:
                source_res['downgrade'] = 'Transcript'

        if search_type != TYPE_GENE and not source_res:
            source_res = source.search_gene(target)
            if source_res:
                source_res['downgrade'] = 'Gene'
        res[source.__name__.lower()] = source_res
        res[SOURCE_NAMES_KEY][source.__name__.lower()] = source.__name__
        time_elapsed = (time.clock() - time_start)
        print source.__name__ + ' takes time ' + str(time_elapsed)
    prepare_source_report(res, search_type)
    report = res[REPORT_KEY]

    time_start = time.clock()
    all_ids = target.get_all_ids()
    time_elapsed = (time.clock() - time_start)
    print 'All ids takes time ' + str(time_elapsed)
    report[IDS_KEY] = all_ids

    if search_type == TYPE_VARIANT:
        aa = target.get_aa()
        if aa[0] and aa[1]:
            # calculate grantham score
            def translate_grantham_score(score):
                if score > 150:
                    return _("Radical Substitution")
                elif score <= 150 and score > 100:
                    return _("Moderately Radical Substitution")
                elif score <= 100 and score > 50:
                    return _("Moderately Conservative Substitution")
                elif score <= 50 and score >= 0:
                    return _("Conservative Substitution")
                return 'N/A'
            grantham_score = GeneVariant.calculate_grantham_score(ref_aa=aa[0], alt_aa=aa[1])
            report[GRANTHAM_SCORE_KEY] = grantham_score
            report[GRANTHAM_INFO_KEY] = translate_grantham_score(grantham_score)
            # add in aa info
            report[REF_AA_KEY] = aa[0]
            report[ALT_AA_KEY] = aa[1]
    return res

'''
    Extract out field data from sources (func: extract_field) and merge them to one dictionary marked by REPORT_KEY
'''
def prepare_source_report(res, search_type):
    if REPORT_KEY not in res:
        res[REPORT_KEY] = {}
    report_res = res[REPORT_KEY]
    report_variant_extract_dict = {
        COSMIC.__name__.lower(): {
            'mutation_description': 'example.Mutation_Description'
        },
        GnomAD.__name__.lower(): {
            'allele_freq': 'match.Total_freq',
            'homozygotes_num': 'match.Total_hom_cnt'
        },
        MY_VARIANT: {
            # 'allele_origin': 'dbsnp.allele_origin',
            # 'alleles': 'dbsnp.alleles',
            'pred_rank_score.polyphen2_hdiv.pred': 'dbnsfp.polyphen2.hdiv.pred',
            'pred_rank_score.polyphen2_hdiv.score': 'dbnsfp.polyphen2.hdiv.score',

            'pred_rank_score.polyphen2_hvar.pred': 'dbnsfp.polyphen2.hvar.pred',
            'pred_rank_score.polyphen2_hvar.score': 'dbnsfp.polyphen2.hvar.score',

            'pred_rank_score.mutationtaster.pred': 'dbnsfp.mutationtaster.pred',
            'pred_rank_score.mutationtaster.score': 'dbnsfp.mutationtaster.score',

            'pred_rank_score.fathmm.pred': 'dbnsfp.fathmm.pred',
            'pred_rank_score.fathmm.score': 'dbnsfp.fathmm.score',

            'pred_rank_score.sift.pred': 'dbnsfp.sift.pred',
            'pred_rank_score.sift.score': 'dbnsfp.sift.score',

            'effect': 'snpeff.ann.effect'
        }
    }

    pred_info_dict = {
        'pred_rank_score.polyphen2_hvar.description': [
            '[0.909,1] : ' + unicode(_('Probably Damaging')),
            '[0.447,0.908] : ' + unicode(_('Possibly Damaging')),
            '[0,0.446] : ' + unicode(_('Benign'))
        ],
        'pred_rank_score.polyphen2_hvar.score_range': '0 ~ 1',
        'pred_rank_score.polyphen2_hvar.score_relation': True,  # True: score higher the more likely to be deleterious

        'pred_rank_score.polyphen2_hdiv.description': [
            '[0.957,1] : ' + unicode(_('Probably Damaging')),
            '[0.453, 0.956]: ' + unicode(_('Possibly Damaging')),
            '[0,0.452] : ' + unicode(_('Benign')),

        ],
        'pred_rank_score.polyphen2_hdiv.score_range': '0 ~ 1',
        'pred_rank_score.polyphen2_hdiv.score_relation': True,  # True: score higher the more likely to be deleterious

        # http://www.mutationtaster.org/info/documentation.html#bayes
        'pred_rank_score.mutationtaster.description': [
            'MTori(' + unicode(_('score')) + ' ' + unicode(_('or')) + ' ' + unicode(_('probability')) + ') ' + unicode(
                _('to')) + ' MTnew:',
            unicode(_('Disease Causing Automatic')) + ' ' + unicode(_('or')) + ' ' + unicode(_('Disease Causing')) + ' MTnew=MTori',
            unicode(_('Polymorphism')) + ' ' + unicode(_('or')) + ' ' + unicode(_('Polymorphism Automatic')) + ' MTnew=1-MTori',
            'MTnew < 0.5 : ' + unicode(_('Disease Causing')),
            'MTnew > 0.5 : ' + unicode(_('Polymorphism'))
        ],
        'pred_rank_score.mutationtaster.score_range': '0 ~ 1',
        'pred_rank_score.mutationtaster.score_relation': True,
        # True: score higher the more likely to be precise prediction

        'pred_rank_score.fathmm.description': [
            '<= -1.5 : ' + unicode(_('Damaging')),
            '> -1.5: ' + unicode(_('Tolerated'))
        ],
        'pred_rank_score.fathmm.score_range': '-16.13 ~ 10.64',
        'pred_rank_score.fathmm.score_relation': False,  # False: score higher the more likely to be tolerated

        'pred_rank_score.sift.description': [
            '< 0.05 : ' + unicode(_('Damaging')),
            '>= 0.05 : ' + unicode(_('Tolerated'))
        ],
        'pred_rank_score.sift.score_range': '0 ~ 1',
        'pred_rank_score.sift.score_relation': False  # False: score higher the more likely to be tolerated
    }

    def extract_dict(target, key):
        field_arr = key.split('.')
        try:
            res = target
            for field in field_arr:
                res = res[field]
        except Exception as e:
            res = None
            pass
        return res

    def update_dict(target, key, value):
        field_arr = key.split('.')
        num = len(field_arr)
        for i in range(num):
            field = field_arr[i]
            if not field in target:
                target[field] = {}
            if i != num - 1:
                target = target[field]
            else:
                target[field] = value

    ''' Deleteriousness predictions result interpretation'''

    # Core: dbnsfp v3.0 paper
    # http://www.arrayserver.com/wiki/index.php?title=Land_Mutation_Annotation_from_VariantClassifiers
    # https://ionreporter.thermofisher.com/ionreporter/help/GUID-2097F236-C8A2-4E67-862D-0FB5875979AC.html
    def map_pred_abbr(key, abbr):
        if key == 'sift' or key == 'fathmm':
            if abbr == 'D':
                return _('Damaging')
            elif abbr == 'T':
                return _('Tolerated')
            elif abbr == 'N':
                return _('Neutral')

        elif key.startswith('polyphen2'):
            if abbr == 'P':
                return _('Possibly Damaging')
            elif abbr == 'D':
                return _('Probably Damaging')
            elif abbr == 'B':
                return _('Benign')
        elif key == 'mutationtaster':
            if abbr == 'A':
                # Translators: http://www.mutationtaster.org/info/documentation.html
                return _('Disease Causing Automatic')
            elif abbr == 'D':
                return _('Disease Causing')
            elif abbr == 'N':
                return _('Polymorphism')
            elif abbr == 'P':
                return _('Polymorphism Automatic')
        return _('Unknown')

    # extract out source url - applies to all search type
    report_res[SOURCE_URLS_KEY] = {}
    for source in GENE_SOURCES:
        report_res[SOURCE_URLS_KEY][source.__name__] = extract_dict(res[source.__name__.lower()], 'url')

    # extract out specific fields - variant
    if search_type == TYPE_VARIANT:
        for source in report_variant_extract_dict:
            key_fields = report_variant_extract_dict[source]
            for report_key in key_fields:
                field = key_fields[report_key]
                update_dict(report_res, report_key, extract_dict(res[source], field))
                if report_key == 'effect' and report_res[report_key]:  # dirty check
                    arr = report_res[report_key].split('_')
                    report_res[report_key] = ' '.join([word.capitalize() for word in arr])

                '''Deleteriousness predictions'''
                if source == MY_VARIANT:  # much dirty check
                    if report_key.endswith('pred'):
                        pred_key = report_key.split('.')[-2]  # e.g. xx.sift.pred and take out sift
                        pred = extract_dict(report_res, report_key)
                        if isinstance(pred, list):
                            for i, p in enumerate(pred):
                                pred[i] = map_pred_abbr(pred_key, pred[i])
                        else:
                            update_dict(report_res, report_key, [map_pred_abbr(pred_key, pred)])
                    if report_key.endswith('score'):
                        score = extract_dict(report_res, report_key)
                        if not isinstance(score, list):
                            update_dict(report_res, report_key, [score])
        for key in pred_info_dict:
            update_dict(report_res, key, pred_info_dict[key])