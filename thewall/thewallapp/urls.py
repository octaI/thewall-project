from django.conf import settings
from django.conf.urls import url
from django.urls import path, include
import oauth2_provider.views as oauth2_views
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


oauth2_endpoint_views = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
] #always accessible

if settings.DEBUG: #only accessible when in DEBUG mode
    oauth2_endpoint_views += [
        path('applications/', oauth2_views.ApplicationList.as_view(), name="list"),
        url(r'^applications/register/$', oauth2_views.ApplicationRegistration.as_view(), name="register"),
        url(r'^applications/(?P<pk>\d+)/$', oauth2_views.ApplicationDetail.as_view(), name="detail"),
        url(r'^applications/(?P<pk>\d+)/delete/$', oauth2_views.ApplicationDelete.as_view(), name="delete"),
        url(r'^applications/(?P<pk>\d+)/update/$', oauth2_views.ApplicationUpdate.as_view(), name="update"),
    ]


urlpatterns = [
    path('username/check',views.username_unique.as_view()),
    path('profiles/', views.profile_list.as_view()),
    path('profile/<int:user_id>',views.profile_detail.as_view()),
    path('comments/',csrf_exempt(views.comment_list.as_view())),
    path('comment/<int:comment_id>',csrf_exempt(views.comment_detail.as_view())),
    path('register/',views.profile_create.as_view()),
    path('o/', include((oauth2_endpoint_views,'thewallapp'),namespace='oauth2_provider')),
    path('login/',csrf_exempt(views.profile_login.as_view()),name='profile_login'),
]

urlpatterns = format_suffix_patterns(urlpatterns)