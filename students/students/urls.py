from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static


from .views import StudentsView
router = DefaultRouter()
router.register(r'', StudentsView, basename='')


urlpatterns = [
    path('', include(router.urls)),
    path('students/create/', StudentsView.as_view({'post': 'createStudent'}), name='createStudent'),
    # path('find/', StudentsView.as_view({'post': 'findFiles'}), name='findFiles'),
    path('upload/', StudentsView.as_view({'post': 'uploadFile'}), name='uploadFile'),
    path('students/create/', StudentsView.as_view({'post': 'createStudent'}), name='createStudent'),
    path('students/filter-students/<str:str>', StudentsView.as_view({'get': 'filter_students'}), name='filter_students'),
    path('student/list_student_virtual_account', StudentsView.as_view({'get': 'list_student_virtual_account'}),
         name='list_student_virtual_account'),


 ]
