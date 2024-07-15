
from rest_framework import routers
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from allfees.views import FeeView

urlpatterns = [

    path('pay/', FeeView.as_view({'post': 'manual_pay_fee'}), name='manual_pay_fee'),

]
