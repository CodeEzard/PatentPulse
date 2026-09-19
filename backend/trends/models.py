from django.db import models


class Patent(models.Model):
    """Patent record for technology trend analysis."""

    title = models.CharField(max_length=255)
    technology_domain = models.CharField(max_length=100, db_index=True)
    assignee = models.CharField(max_length=150)
    filing_year = models.PositiveIntegerField(db_index=True)
    citation_count = models.PositiveIntegerField(default=0)
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords")

    class Meta:
        ordering = ["-filing_year", "-citation_count"]
        indexes = [
            models.Index(fields=["technology_domain", "filing_year"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.filing_year})"
