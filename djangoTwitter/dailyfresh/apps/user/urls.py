from django.conf.urls import url
from apps.user import views
from django.contrib.auth.decorators import login_required
urlpatterns = [

    # url(r'^register/$', views.register,name='register'),
    # url(r'^register_handle/$', views.register_handle,name='register_handle')
    url(r'^register/$',views.RegisterView.as_view(),name='register'),
    url(r'^active/(?P<token>.*)$',views.ActiveView.as_view(),name='active'),
    url(r'^login/$',views.loginView.as_view(),name='login'),
    # url(r'^info/$',login_required(views.userInfoView.as_view()),name='info'),
    url(r'^info/$',views.userInfoView.as_view(),name='info'),
    url(r'^order/$',views.userOrderView.as_view(),name='order'),
    url(r'^site/$',views.userSiteView.as_view(),name='site'),
]
