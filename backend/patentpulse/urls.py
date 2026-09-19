from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def root_health_view(request):
    return JsonResponse(
        {
            "service": "PatentPulse API",
            "status": "healthy",
            "endpoints": {
                "patents": "/api/patents/",
                "trend_summary": "/api/trends/summary/",
                "domains": "/api/trends/domains/",
                "admin": "/admin/",
            },
        }
    )


urlpatterns = [
    path("", root_health_view, name="api-root-health"),
    path("admin/", admin.site.urls),
    path("api/", include("trends.urls")),
]
