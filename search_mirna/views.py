# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from .src import search

# Create your views here.
from django.http import HttpResponse


class SearchMiRNA(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, mirnas=''):
        try:
            mirnas = mirnas.split(',')
        except:
            mirnas = []
        return Response(search.search_mirnas(mirnas))

    def post(self, request, mirnas=''):
        try:
            if request.content_type == 'application/json':
                json_request = request.data
                mirnas = json_request['mirnas']
            elif request.content_type == 'application/x-www-form-urlencoded':
                mirnas = request.POST.get('mirnas', '').split(',')
            else:
                mirnas = []
        except Exception as e:
            print e.message
            mirnas = []
        return Response(search.search_mirnas(mirnas))
