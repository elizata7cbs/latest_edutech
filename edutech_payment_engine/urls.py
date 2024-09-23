from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="Elimu Pay",
        default_version='v1',
        description="API documentation for Elimu Pay",
    ),
    public=True,
    permission_classes=[permissions.AllowAny]

)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/students/', include('students.urls')),
    path('api/v1/studentsparents/', include('studentsparents.urls')),
    path('api/v1/expenses/', include('expenses.urls')),
    path('api/v1/suppliers/', include('suppliers.urls')),
    path('api/v1/schools/', include('schools.urls')),
    path('api/v1/fee/', include('fee.urls')),
    path('api/v1/payfee/', include('payfee.urls')),
    path('api/v1/parents/', include('parents.urls')),
    path('api/v1/feecategories/', include('feecategories.urls')),
    path('api/v1/expensetypes/', include('expensetypes.urls')),
    path("api/v1/auth/", include("authuser.urls")),
    path("api/v1/fees/", include("allfees.urls")),
    path("api/v1/payfee/", include("payfee.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/inquiries/",include("inquiries.urls")),
    path("api/v1/usergroup/", include("usergroup.urls")),
    path("api/v1/mpesa/", include("mpesa.urls")),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),]

# # Serve files
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
