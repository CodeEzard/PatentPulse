from django.test import TestCase

from trends.models import Patent


class PatentModelTests(TestCase):
    def test_str_representation(self):
        patent = Patent.objects.create(
            title="Test invention",
            technology_domain="AI/ML",
            assignee="Acme",
            filing_year=2022,
            citation_count=5,
            keywords="test,invention",
        )
        self.assertEqual(str(patent), "Test invention (2022)")

    def test_default_ordering_is_newest_and_most_cited_first(self):
        older = Patent.objects.create(
            title="Older", technology_domain="IoT", assignee="A",
            filing_year=2019, citation_count=100,
        )
        newer = Patent.objects.create(
            title="Newer", technology_domain="IoT", assignee="A",
            filing_year=2023, citation_count=1,
        )
        self.assertEqual(list(Patent.objects.all()), [newer, older])
