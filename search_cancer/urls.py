from django.conf.urls import url
from . import views

app_name = 'search_cancer'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^type=(?P<query_type>.*)/query=(?P<query>.*)$', views.search_view, name='search'),
    url(r'^api/type=(?P<type>.*)/query=(?P<query>.*)$', views.SearchQueryAPI.as_view(), name='api'),
]
