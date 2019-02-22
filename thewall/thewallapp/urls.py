from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('profiles/', views.profile_list.as_view()),
    path('profile/<str:user_name>',views.profile_detail.as_view()),
    path('profile/id/<int:pk>',views.profile_detail_id.as_view()),
    path('comments/',csrf_exempt(views.comment_list.as_view())),
    path('comment/<int:comment_id>',csrf_exempt(views.comment_detail.as_view())),
    path('register/',views.profile_create.as_view()),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('login/',csrf_exempt(views.profile_login.as_view()),name='profile_login'),
]

urlpatterns = format_suffix_patterns(urlpatterns)