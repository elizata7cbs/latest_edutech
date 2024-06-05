"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from django.conf import settings
from django.conf.urls.static import static
# from rest_framework_jwt import views as jwt_views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

schema_view = get_schema_view(
    openapi.Info(
        title="Encode Technologies",
        default_version='v1',

    ),
    public=False,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api-token-auth/', obtain_jwt_token),
    # path('api-token-refresh/', refresh_jwt_token),
    # path('api-token-verify/', verify_jwt_token),
    path("api/v1/parents/", include("parents.urls")),
    path("api/v1/suppliers/", include("suppliers.urls")),
    path("api/v1/supplierspayment/", include("supplierspayment.urls")),
    path("api/v1/feecollections/", include("feecollections.urls")),
    path("api/v1/auth/", include("authuser.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/expenses/", include("expenses.urls")),
    path("api/v1/expenses/", include("expenses.urls")),
    path("api/v1/expensetypes/", include("expensetypes.urls")),
    path("api/v1/students/", include("students.urls")),
    path("api/v1/studentsparents/", include("studentsparents.urls")),
    path("api/v1/studentsschools/", include("studentsschools.urls")),
    path("api/v1/paymentmodes/", include("paymentmodes.urls")),
    path("api/v1/usergroup/", include("usergroup.urls")),
    path("api/v1/schools/", include("schools.urls")),
    path("api/v1/feecategories/", include("feecategories.urls")),
    # path("api/v1/paymentgroups/", include("paymentgroups.urls")),
    path("api/v1/payfee/", include("payfee.urls")),
    path("api/v1/fee/", include("fee.urls")),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

# Serve files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
