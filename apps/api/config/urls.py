from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView
from .auth_views import session, sign_in, sign_out
from modules.organization.views import choose_organization

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/session/", session),
    path("api/login/", sign_in),
    path("api/logout/", sign_out),
    path("api/organization/select/", choose_organization),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/", include("modules.catalog.urls")),
]
