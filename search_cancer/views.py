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
    test_mode = False
    test_redis_key = 'BRAF_TEST'
    REDIS_TEST = None
    if query == 'test':
        test_mode = True
        import redis
        REDIS_TEST = redis.StrictRedis(host='localhost', port=6379, db=10)
        search_result = REDIS_TEST.get(test_redis_key)
        if search_result:
            search_result = json.loads(search_result)
        else:
            query = 'BRAF'
    if not search_result:
        if query_type == 'transcript':
            search_result = search.search_transcript(query)
        elif query_type == 'gene':
            search_result = search.search_gene(query)
        elif query_type == 'variant':
            search_result = search.search_variant(query)

    if not result:
        result = {}
    result['user_input'] = {}
    result['user_input']['query_type'] = query_type
    result['user_input']['query'] = query
    result['result'] = search_result

    # for test
    result['source_jsons'] = {}
    for key in search_result:
        result['source_jsons'][key] = json.dumps(search_result[key], indent=4)
    if test_mode and REDIS_TEST:
        REDIS_TEST.set(test_redis_key, json.dumps(search_result))  # TODO: change ex
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
