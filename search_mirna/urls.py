from django.conf.urls import url
from . import views

app_name = 'search_mirna'
urlpatterns = [
    url(r'^api/search-mirna/mirnas=(?P<mirnas>.*)/$', views.SearchMiRNA.as_view(), name='api'),
    url(r'^api/search-mirna/$', views.SearchMiRNA.as_view(), name='api'),

    # url(r'^type=(?P<query_type>.*)/query=(?P<query>.*)$', views.search_view, name='search'),
    # url(r'^api/type=(?P<type>.*)/query=(?P<query>.*)$', views.SearchQueryAPI.as_view(), name='api'),
]
