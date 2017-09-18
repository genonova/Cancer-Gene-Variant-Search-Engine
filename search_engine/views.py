# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render


def index_files(request, filename):
    return render(request, filename, {}, content_type="text/plain")
