from django.contrib import admin
from django.urls import path, re_path
from django.http import JsonResponse

def health(_request):
    return JsonResponse({"status": "ok", "app": "ERPShipping", "version": "0.0.1"})

urlpatterns = [
    path("admin/", admin.site.urls),
    # matches /api/v1/health and /api/v1/health/
    re_path(r"^api/v1/health/?$", health, name="health"),
]
