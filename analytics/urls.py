from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('data/', views.dashboard_data, name='dashboard_data'),
]
