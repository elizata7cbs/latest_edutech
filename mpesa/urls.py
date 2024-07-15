# urls.py
from django.urls import path, include

from edutech_payment_engine.urls import schema_view
from .views import call_back_url, Mpesa

urlpatterns = [
    path('lipa_na_mpesa/<str:phone>/<int:amount>', Mpesa.as_view({'post': 'lipa_na_mpesa'}), name='lipa_na_mpesa'),
    path('api/callback', call_back_url, name='call_back_url'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
