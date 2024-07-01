from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Encode Technologies",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/account/', include('account.urls')),
    path('api/v1/expenses/', include('expenses.urls')),
    path('api/v1/expensetypes/', include('expensetypes.urls')),
    path('api/v1/expensepayment/', include('expensepayment.urls')),  # Add this line
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

# # Serve files
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
