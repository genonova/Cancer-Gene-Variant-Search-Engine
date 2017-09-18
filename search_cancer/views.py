# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from .src import search

# Create your views here.
from django.http import HttpResponse

context_default = {
    'search_types': {
        'variant': _('Variant'),
        'transcript': _('Transcript'),
        'gene': _('Gene')
    },
    'user_input': {
        'query_type': 'gene',
        'query': 'BRAF'
    }
}


def index(request):
    context = context_default.copy()
    if request.method == 'GET':
        # return HttpResponse("Hello, world. You're at the polls index.")
        return render(request, 'search_cancer/index.html', context)
    if request.method == 'POST':
        query = request.POST.get('query')
        query_type = request.POST.get('query_type')
        if query and type:
            return HttpResponseRedirect(reverse('search_cancer:search', args=(query_type, query,)))


def search_view(request, query_type, query):
    context = context_default.copy()
    search_handler(query, query_type, context)
    return render(request, 'search_cancer/search_result.html',
                  context)


# class SearchEngineAPIView(generics.ListCreateAPIView):
#

def search_handler(query, query_type, result=None):
    search_result = {}
    # test
    if query == 'test':
        search_result = {
            "cosmic": {
                "count": 50655,
                "url": "http://cancer.sanger.ac.uk/cosmic/search?q=BRAF"
            },
            "ids": {
                "ref_seq": [
                    "chr7",
                    "ENSG00000157764",
                    "BRAF",
                    "NM_004333.4"
                ],
                "var_info": [
                    "c.665C>T",
                    "g.11856378G>A",
                    "p.Ala222Val"
                ]
            },
            "gnomad": {
                "url": "http://gnomad.broadinstitute.org/gene/ENSG00000157764"
            },
            "civic": {
                "entrez_id": 673,
                "description": "BRAF mutations are found to be recurrent in many cancer types. Of these, the mutation of valine 600 to glutamic acid (V600E) is the most prevalent. V600E has been determined to be an activating mutation, and cells that harbor it, along with other V600 mutations are sensitive to the BRAF inhibitor dabrafenib. It is also common to use MEK inhibition as a substitute for BRAF inhibitors, and the MEK inhibitor trametinib has seen some success in BRAF mutant melanomas. BRAF mutations have also been correlated with poor prognosis in many cancer types, although there is at least one study that questions this conclusion in papillary thyroid cancer.",
                "url": "https://civic.genome.wustl.edu/events/genes/5/summary",
                "lifecycle_actions": {},
                "provisional_values": {},
                "name": "BRAF",
                "sources": [
                    {
                        "status": "fully curated",
                        "open_access": None,
                        "name": "Targeting of the BRAF gene in papillary thyroid carcinoma (review).",
                        "journal": "Oncol. Rep.",
                        "citation": "Li et al., 2009, Oncol. Rep.",
                        "pmc_id": None,
                        "full_journal_title": "Oncology reports",
                        "source_url": "http://www.ncbi.nlm.nih.gov/pubmed/19724843",
                        "pubmed_id": "19724843",
                        "is_review": False,
                        "publication_date": {
                            "month": 10,
                            "year": 2009
                        },
                        "id": 9
                    },
                    {
                        "status": "fully curated",
                        "open_access": None,
                        "name": "Clinicopathological relevance of BRAF mutations in human cancer.",
                        "journal": "Pathology",
                        "citation": "Pakneshan et al., 2013, Pathology",
                        "pmc_id": None,
                        "full_journal_title": "Pathology",
                        "source_url": "http://www.ncbi.nlm.nih.gov/pubmed/23594689",
                        "pubmed_id": "23594689",
                        "is_review": False,
                        "publication_date": {
                            "month": 6,
                            "year": 2013
                        },
                        "id": 10
                    }
                ],
                "errors": {},
                "variants": [
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "AMPLIFICATION",
                        "id": 1269
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 1,
                            "accepted_count": 12
                        },
                        "name": "V600",
                        "id": 17
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "PPFIBP2-BRAF",
                        "id": 617
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "D594A",
                        "id": 579
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 2
                        },
                        "name": "TRIM24-BRAF",
                        "id": 287
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "G596C",
                        "id": 694
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 2,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "V600_K601DELINSD",
                        "id": 1658
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "AKAP9-BRAF",
                        "id": 184
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "L597V",
                        "id": 585
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 1,
                            "accepted_count": 0
                        },
                        "name": "APC",
                        "id": 842
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "D594V",
                        "id": 580
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "G469R",
                        "id": 840
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "G466A",
                        "id": 1196
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 2
                        },
                        "name": "KIAA1549-BRAF",
                        "id": 618
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "F595L",
                        "id": 1121
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "G596V",
                        "id": 1650
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "ZKSCAN1-BRAF",
                        "id": 657
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 2
                        },
                        "name": "AGK-BRAF",
                        "id": 285
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 4
                        },
                        "name": "MUTATION",
                        "id": 399
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "G596R",
                        "id": 1627
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 2,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "V600D",
                        "id": 11
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 12,
                            "rejected_count": 0,
                            "accepted_count": 3
                        },
                        "name": "V600K",
                        "id": 563
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 2
                        },
                        "name": "L597R",
                        "id": 288
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 88,
                            "rejected_count": 0,
                            "accepted_count": 51
                        },
                        "name": "V600E",
                        "id": 12
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 2
                        },
                        "name": "L597S",
                        "id": 582
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "599INST",
                        "id": 1298
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "G469V",
                        "id": 841
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "WILD TYPE",
                        "id": 426
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "V600E+V600M",
                        "id": 13
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "BRAF-CUL1",
                        "id": 656
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "K483M",
                        "id": 581
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 5,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "D594N",
                        "id": 1107
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "DELNVTAP",
                        "id": 1663
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "G464V",
                        "id": 1106
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 3,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "V600R",
                        "id": 991
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 2
                        },
                        "name": "PAPSS1-BRAF",
                        "id": 286
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 2
                        },
                        "name": "L505H",
                        "id": 658
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 3,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "G469A",
                        "id": 992
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "L597Q",
                        "id": 583
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 3
                        },
                        "name": "D594G",
                        "id": 611
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "DEL 485-490",
                        "id": 522
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "V600E AMPLIFICATION",
                        "id": 14
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 1,
                            "rejected_count": 0,
                            "accepted_count": 1
                        },
                        "name": "K601E",
                        "id": 584
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "V600A",
                        "id": 1388
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "I463S",
                        "id": 1194
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "N581S",
                        "id": 1186
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "V600M",
                        "id": 1405
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "A728V",
                        "id": 1198
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "E586K",
                        "id": 1197
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "G469E",
                        "id": 993
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "V600L",
                        "id": 1404
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "R462I",
                        "id": 1193
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "V600G",
                        "id": 1199
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "G464E",
                        "id": 1195
                    },
                    {
                        "evidence_items": {
                            "submitted_count": 0,
                            "rejected_count": 0,
                            "accepted_count": 0
                        },
                        "name": "T599I",
                        "id": 1185
                    }
                ],
                "type": "gene",
                "id": 5,
                "aliases": [
                    "BRAF",
                    "B-raf",
                    "RAFB1",
                    "NS7",
                    "BRAF1",
                    "B-RAF1"
                ]
            },
            "hgnc": {
                "hgnc_id": "HGNC:1097",
                "ensembl_gene_id": "ENSG00000157764",
                "alias_symbol": [
                    "BRAF1"
                ],
                "refseq_accession": [
                    "NM_004333"
                ],
                "locus_group": "protein-coding gene",
                "ena": [
                    "M95712"
                ],
                "lsdb": [
                    "LRG_299|http://www.lrg-sequence.org/LRG/LRG_299"
                ],
                "ccds_id": [
                    "CCDS5863"
                ],
                "uniprot_ids": [
                    "P15056"
                ],
                "location": "7q34",
                "vega_id": "OTTHUMG00000157457",
                "omim_id": [
                    "164757"
                ],
                "prev_name": [
                    "v-raf murine sarcoma viral oncogene homolog B"
                ],
                "date_approved_reserved": "1991-07-16T00:00:00Z",
                "status": "Approved",
                "locus_type": "gene with protein product",
                "pubmed_id": [
                    2284096,
                    1565476
                ],
                "location_sortable": "07q34",
                "symbol": "BRAF",
                "iuphar": "objectId:1943",
                "date_name_changed": "2014-06-26T00:00:00Z",
                "orphanet": 119066,
                "gene_family_id": [
                    654,
                    1157
                ],
                "mgd_id": [
                    "MGI:88190"
                ],
                "_version_": 1578909784269127680,
                "gene_family": [
                    "Mitogen-activated protein kinase kinase kinases",
                    "RAF family"
                ],
                "uuid": "d9dd3f55-7fab-4f48-a074-b027577e1b14",
                "entrez_id": "673",
                "name": "B-Raf proto-oncogene, serine/threonine kinase",
                "date_modified": "2017-03-24T00:00:00Z",
                "url": "http://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id=HGNC:1097",
                "cosmic": "BRAF",
                "rgd_id": [
                    "RGD:619908"
                ],
                "ucsc_id": "uc003vwc.5"
            },
            "myvariant": {}
        }
        import logging
        logger = logging.getLogger('search_cancer')
        logger.debug('here!!!')
        try:
            0 / 0
        except Exception as e:
            logger.error('error', exc_info=True)

    else:
        if not result:
            result = {}
        if query_type == 'transcript':
            search_result = search.search_transcript(query)
        elif query_type == 'gene':
            search_result = search.search_gene(query)
        elif query_type == 'variant':
            search_result = search.search_variant(query)
    result['user_input'] = {}
    result['user_input']['query_type'] = query_type
    result['user_input']['query'] = query
    result['result'] = search_result

    # for test
    result['json_search_result_cosmic'] = json.dumps(search_result['cosmic'], indent=4)
    result['json_search_result_civic'] = json.dumps(search_result['civic'], indent=4)
    result['json_search_result_myvariant'] = json.dumps(search_result['myvariant'], indent=4)
    result['json_search_result_hgnc'] = json.dumps(search_result['hgnc'], indent=4)

    return result


class SearchQueryAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, query, format=None):
        if query:
            return Response({
                'query': query
            })
        else:
            return index(request)

    def post(self, request, query, format=None):
        query = request.POST.get('query', None)
        if query and type:
            return Response({
                'query': query
            })
        else:
            return index(request)
