from django.conf.urls import include,url
from . import views

urlpatterns = [

    url(r'index/$',views.IndexView.as_view(),name='index'),
    # url(r'detail/(?P<goods_id>\d+)$',views.DetailView.as_view(),name='detail')
    url(r'detail/(?P<goods_id>\d+)$',views.DetailView.as_view(),name='detail'),
    url(r'list/(?P<type_id>\d*)/(?P<page>\d*)$',views.ListView.as_view(),name='list'),
]
