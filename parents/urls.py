from django.urls import path, include
from rest_framework.routers import DefaultRouter

from parents import views
from parents.views import ParentViewSet

router = DefaultRouter()
router.register(r'parents', ParentViewSet, basename='parent')

urlpatterns = [
    path('', include(router.urls)),
    path('parents/<int:parent_id>/students/', views.Parents, name='list student'),

    # path('api/v1/fee/parent_students/<int:student_id>/',
    #      ParentView.as_view({'get': 'parent_students'}),
    #      name='get_total_balance_for_student'),
]
