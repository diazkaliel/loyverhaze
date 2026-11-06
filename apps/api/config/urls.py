from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView

@ensure_csrf_cookie
def session(request):
    if request.user.is_authenticated:
        return JsonResponse({"authenticated": True, "username": request.user.get_username()})
    return JsonResponse({"authenticated": False, "username": None})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/session/", session),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/", include("modules.catalog.urls")),
]
