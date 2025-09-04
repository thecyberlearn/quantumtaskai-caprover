from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('digital-branding/', views.digital_branding_view, name='digital_branding'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('contact/', views.contact_form_view, name='contact_form'),
    path('health/', views.health_check_view, name='health_check'),
    path('test-og/', views.test_og_view, name='test_og'),
    
    # External service wrapper pages
    path('<str:page_name>/', views.external_page_view, name='external_page'),
]