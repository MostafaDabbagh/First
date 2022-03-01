from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.download_test_view, name='download_test'),
    ]
