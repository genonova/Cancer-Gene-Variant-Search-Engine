from source_cosmic import COSMIC
from source_gnomad import GnomAD
from source_civic import CIViC
from source_hgnc import HGNC
from source_gene_cards import GeneCards

from util_variant import GeneVariant, GeneReference

gene_sources = [COSMIC, GnomAD, CIViC, HGNC, GeneCards]

import time


def search_variant(variant_str):
    variant = GeneVariant(variant_str)
    time_start = time.clock()
    all_ids = variant.get_all_ids()
    time_elapsed = (time.clock() - time_start)
    print 'All ids takes time ' + str(time_elapsed)
    time_start = time.clock()
    mv_res = variant.get_myvariant_res()
    time_elapsed = (time.clock() - time_start)
    print 'One MV search takes time ' + str(time_elapsed)
    res = {
        'ids': all_ids,
        'myvariant': mv_res
    }  # for test
    for source in gene_sources:
        time_start = time.clock()
        source_res = source.search_variant(variant)
        if not source_res:
            source_res = source.search_transcript(variant)
            if source_res:
                source_res['downgrade'] = 'Transcript'
        if not source_res:
            source_res = source.search_gene(variant)
            if source_res:
                source_res['downgrade'] = 'Gene'
        res[source.__name__.lower()] = source_res
        time_elapsed = (time.clock() - time_start)
        print source.__name__ + ' takes time ' + str(time_elapsed)
    return res


def search_gene(gene_str):
    gene = GeneReference(gene_str)
    res = {
        'ids': gene.get_all_ids(),
        'myvariant': gene.get_myvariant_res()
    }  # for test
    for source in gene_sources:
        res[source.__name__.lower()] = source.search_gene(gene)
    return res


def search_transcript(transcript_str):
    transcript = GeneReference(transcript_str)
    res = {
        'ids': transcript.get_all_ids(),
        'myvariant': transcript.get_myvariant_res()
    }  # for test
    for source in gene_sources:
        source_res = source.search_transcript(transcript)
        if not source_res:
            source_res = source.search_gene(transcript)
            if source_res:
                source_res['downgrade'] = 'Gene'
        res[source.__name__.lower()] = source_res
    return res
