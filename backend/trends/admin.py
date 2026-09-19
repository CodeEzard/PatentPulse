from django.contrib import admin

from .models import Patent


@admin.register(Patent)
class PatentAdmin(admin.ModelAdmin):
    list_display = ("title", "technology_domain", "filing_year", "assignee", "citation_count")
    list_filter = ("technology_domain", "filing_year")
    search_fields = ("title", "assignee", "keywords")
