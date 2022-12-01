from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('beam/', views.beam, name='beam'),
    path('beam/download_dxf_beam', views.download_dxf_beam, name='beam_download'),
    path('author/', views.author, name='author')
]