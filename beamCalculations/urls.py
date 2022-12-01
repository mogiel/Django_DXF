from django.urls import path
from .views import BeamCalc

app_name = 'calcBeam'
urlpatterns = [
    path('', BeamCalc, name='main'),
]