from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PatentViewSet, TrendSummaryView, DomainListView

router = DefaultRouter()
router.register(r"patents", PatentViewSet, basename="patent")

urlpatterns = [
    path("trends/summary/", TrendSummaryView.as_view(), name="trend-summary"),
    path("trends/domains/", DomainListView.as_view(), name="trend-domains"),
    path("", include(router.urls)),
]
