from django.urls import path
from apps.landingpage.views import home

app_name = 'landingpage'

urlpatterns = [
  path('',      home.home,       name='home'),
  path('404/',  home.error_404,  name='404')
]