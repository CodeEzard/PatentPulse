from rest_framework import serializers

from .models import Patent


class PatentSerializer(serializers.ModelSerializer):
    keyword_list = serializers.SerializerMethodField()

    class Meta:
        model = Patent
        fields = [
            "id",
            "title",
            "technology_domain",
            "assignee",
            "filing_year",
            "citation_count",
            "keywords",
            "keyword_list",
        ]

    def get_keyword_list(self, obj):
        if not obj.keywords:
            return []
        return [k.strip() for k in obj.keywords.split(",") if k.strip()]


class TrendPointSerializer(serializers.Serializer):
    """One (year, domain) bucket in the aggregated trend series."""

    filing_year = serializers.IntegerField()
    technology_domain = serializers.CharField()
    filing_count = serializers.IntegerField()
    total_citations = serializers.IntegerField()
