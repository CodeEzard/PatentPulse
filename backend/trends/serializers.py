from urllib.parse import quote_plus

from rest_framework import serializers

from .models import Patent


class PatentSerializer(serializers.ModelSerializer):
    keyword_list = serializers.SerializerMethodField()
    patent_url = serializers.SerializerMethodField()

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
            "patent_url",
        ]

    def get_keyword_list(self, obj):
        if not obj.keywords:
            return []
        return [k.strip() for k in obj.keywords.split(",") if k.strip()]

    def get_patent_url(self, obj):
        query = f"{obj.title} {obj.assignee}".strip()
        return f"https://patents.google.com/?q={quote_plus(query)}"


class TrendPointSerializer(serializers.Serializer):
    """One (year, domain) bucket in the aggregated trend series."""

    filing_year = serializers.IntegerField()
    technology_domain = serializers.CharField()
    filing_count = serializers.IntegerField()
    total_citations = serializers.IntegerField()
