from django.conf.urls import include,url
from . import views

urlpatterns = [

    url(r'^cart/$',views.CartView.as_view(),name='cart'),
    url(r'^add$',views.CartAddView.as_view(),name='add'),
]