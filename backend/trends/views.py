from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters
from rest_framework import viewsets, generics
from rest_framework.response import Response

from .models import Patent
from .serializers import PatentSerializer, TrendPointSerializer


class PatentFilter(filters.FilterSet):
    domain = filters.CharFilter(field_name="technology_domain", lookup_expr="iexact")
    year = filters.NumberFilter(field_name="filing_year")
    year_from = filters.NumberFilter(field_name="filing_year", lookup_expr="gte")
    year_to = filters.NumberFilter(field_name="filing_year", lookup_expr="lte")
    search = filters.CharFilter(method="filter_search")

    class Meta:
        model = Patent
        fields = ["domain", "year", "year_from", "year_to", "search"]

    def filter_search(self, queryset, name, value):
        val = value.strip() if value else ""
        if not val:
            return queryset
        return queryset.filter(
            Q(title__icontains=val)
            | Q(keywords__icontains=val)
            | Q(assignee__icontains=val)
        )


class PatentViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only, filterable, searchable list of patent records."""

    queryset = Patent.objects.all()
    serializer_class = PatentSerializer
    filterset_class = PatentFilter


class TrendSummaryView(generics.GenericAPIView):
    """Aggregated (year, domain) filing counts and citation totals."""

    serializer_class = TrendPointSerializer

    def get(self, request):
        domain = request.query_params.get("domain")
        qs = Patent.objects.all()
        if domain:
            qs = qs.filter(technology_domain__iexact=domain)

        rows = (
            qs.values("filing_year", "technology_domain")
            .annotate(
                filing_count=Count("id"),
                total_citations=Coalesce(Sum("citation_count"), 0),
            )
            .order_by("filing_year", "technology_domain")
        )
        serializer = self.get_serializer(rows, many=True)
        return Response(serializer.data)


class DomainListView(generics.GenericAPIView):
    """Return distinct technology domains."""

    def get(self, request):
        domains = (
            Patent.objects.values_list("technology_domain", flat=True)
            .distinct()
            .order_by("technology_domain")
        )
        return Response(list(domains))
