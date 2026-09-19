from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from trends.models import Patent


class PatentApiTests(APITestCase):
    def setUp(self):
        Patent.objects.create(
            title="Solid-state electrolyte composition",
            technology_domain="Energy Storage",
            assignee="Voltify Inc",
            filing_year=2021,
            citation_count=40,
            keywords="solid-state,battery,electrolyte",
        )
        Patent.objects.create(
            title="Transformer attention sparsification",
            technology_domain="AI/ML",
            assignee="Northwind AI",
            filing_year=2022,
            citation_count=72,
            keywords="transformer,attention,sparsity",
        )
        Patent.objects.create(
            title="Fast-charging control circuit",
            technology_domain="Energy Storage",
            assignee="Acme Motors",
            filing_year=2022,
            citation_count=18,
            keywords="charging,circuit,ev",
        )

    def test_list_returns_all_patents(self):
        url = reverse("patent-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]) if "results" in response.data else len(response.data), 3)

    def test_filter_by_domain(self):
        url = reverse("patent-list")
        response = self.client.get(url, {"domain": "AI/ML"})
        payload = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["title"], "Transformer attention sparsification")

    def test_filter_by_year_range(self):
        url = reverse("patent-list")
        response = self.client.get(url, {"year_from": 2022, "year_to": 2022})
        payload = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(payload), 2)

    def test_search_matches_keywords(self):
        url = reverse("patent-list")
        response = self.client.get(url, {"search": "battery"})
        payload = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["assignee"], "Voltify Inc")

    def test_keyword_list_is_parsed_from_keywords_field(self):
        url = reverse("patent-list")
        response = self.client.get(url, {"domain": "AI/ML"})
        payload = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(payload[0]["keyword_list"], ["transformer", "attention", "sparsity"])

    def test_patent_url_is_generated_for_google_patents(self):
        url = reverse("patent-list")
        response = self.client.get(url, {"domain": "AI/ML"})
        payload = response.data["results"] if "results" in response.data else response.data
        self.assertIn("patent_url", payload[0])
        self.assertTrue(payload[0]["patent_url"].startswith("https://patents.google.com/?q="))
        self.assertIn("Transformer+attention+sparsification", payload[0]["patent_url"])
        self.assertIn("Northwind+AI", payload[0]["patent_url"])


class TrendSummaryApiTests(APITestCase):
    def setUp(self):
        Patent.objects.create(
            title="A", technology_domain="AI/ML", assignee="X",
            filing_year=2021, citation_count=10,
        )
        Patent.objects.create(
            title="B", technology_domain="AI/ML", assignee="Y",
            filing_year=2021, citation_count=20,
        )
        Patent.objects.create(
            title="C", technology_domain="IoT", assignee="Z",
            filing_year=2021, citation_count=5,
        )

    def test_summary_aggregates_by_year_and_domain(self):
        url = reverse("trend-summary")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        by_domain = {row["technology_domain"]: row for row in response.data}
        self.assertEqual(by_domain["AI/ML"]["filing_count"], 2)
        self.assertEqual(by_domain["AI/ML"]["total_citations"], 30)
        self.assertEqual(by_domain["IoT"]["filing_count"], 1)

    def test_summary_can_be_scoped_to_one_domain(self):
        url = reverse("trend-summary")
        response = self.client.get(url, {"domain": "IoT"})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["technology_domain"], "IoT")

    def test_domains_endpoint_lists_distinct_domains(self):
        url = reverse("trend-domains")
        response = self.client.get(url)
        self.assertEqual(sorted(response.data), ["AI/ML", "IoT"])
