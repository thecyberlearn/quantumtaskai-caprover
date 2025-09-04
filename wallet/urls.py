from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.wallet_view, name='wallet'),
    path('topup/', views.wallet_topup_view, name='wallet_topup'),
    path('top-up/success/', views.wallet_topup_success_view, name='wallet_topup_success'),
    path('top-up/cancel/', views.wallet_topup_cancel_view, name='wallet_topup_cancel'),
    path('stripe/debug/', views.stripe_debug_view, name='stripe_debug'),
    path('stripe/webhook/', views.stripe_webhook_view, name='stripe_webhook'),
    path('api/deduct/', views.wallet_deduct_api, name='wallet_deduct_api'),
]