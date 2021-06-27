from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

app_name = 'hp'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('api/', views.HappinessAPI.as_view(), name='teams_happiness'),
    path('api/<str:date_str>/', views.HappinessAPI.as_view(), name='teams_happiness_wdate'),
]