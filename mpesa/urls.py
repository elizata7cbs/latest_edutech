from django.urls import path, include

from mpesa.views import Mpesa

urlpatterns = [
    path('lipa_na_mpesa/<str:phone>/<int:amount>', Mpesa.as_view({'post': 'lipa_na_mpesa'}), name='lipa_na_mpesa'),
    path('mpesa_callback/', Mpesa.as_view({'post': 'mpesa_callback'}), name='mpesa_callback'),

]
