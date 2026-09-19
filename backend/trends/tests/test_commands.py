import os
from unittest.mock import patch, MagicMock
from django.core.management import call_command, CommandError
from django.test import TestCase

from trends.models import Patent


class SeedDataCommandTests(TestCase):
    def test_seed_data_loads_records(self):
        call_command("seed_data", clear=True)
        self.assertGreater(Patent.objects.count(), 0)
        first = Patent.objects.first()
        self.assertIsNotNone(first.title)
        self.assertIsNotNone(first.technology_domain)


class FetchPatentsCommandTests(TestCase):
    def test_missing_api_key_raises_command_error(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CommandError) as ctx:
                call_command("fetch_patents")
            self.assertIn("PATENTSVIEW_API_KEY", str(ctx.exception))

    @patch("trends.management.commands.fetch_patents.requests.get")
    def test_fetch_patents_with_mocked_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "patents": [
                {
                    "patent_id": "US12345678",
                    "patent_title": "Deep Neural Network Processor",
                    "patent_date": "2023-08-15",
                    "patent_year": 2023,
                    "num_times_cited_by_us_patents": 15,
                    "assignees": [
                        {
                            "assignee_organization": "DeepTech Innovations Inc.",
                            "assignee_name_first": None,
                            "assignee_name_last": None,
                        }
                    ],
                    "applications": [
                        {"filing_date": "2021-04-10"}
                    ],
                    "cpc_current": [
                        {
                            "cpc_subclass_id": "G06N",
                            "cpc_group_id": "G06N3/06",
                            "cpc_group_title": "physical realization of neural networks",
                            "cpc_subgroup_title": "circuits using neural models",
                        }
                    ],
                }
            ],
            "total_patent_count": 1,
            "count": 1,
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"PATENTSVIEW_API_KEY": "test-key-123"}):
            call_command("fetch_patents", limit_per_domain=1, page_size=1, clear=True)

        self.assertEqual(mock_get.call_count, 5)

        first_call = mock_get.call_args_list[0]
        url = first_call[0][0]
        headers = first_call[1]["headers"]
        self.assertEqual(url, "https://search.patentsview.org/api/v1/patent/")
        self.assertEqual(headers["X-Api-Key"], "test-key-123")

        self.assertEqual(Patent.objects.count(), 5)
        patent = Patent.objects.filter(technology_domain="AI/ML").first()
        self.assertIsNotNone(patent)
        self.assertEqual(patent.title, "Deep Neural Network Processor")
        self.assertEqual(patent.assignee, "DeepTech Innovations Inc.")
        self.assertEqual(patent.filing_year, 2021)
        self.assertEqual(patent.citation_count, 15)
        self.assertTrue(len(patent.keywords) > 0)

    @patch("trends.management.commands.fetch_patents.requests.get")
    def test_fetch_patents_clear_flag(self, mock_get):
        Patent.objects.create(
            title="Pre-existing patent",
            technology_domain="AI/ML",
            assignee="Old Corp",
            filing_year=2018,
            citation_count=2,
            keywords="old,patent",
        )
        self.assertEqual(Patent.objects.count(), 1)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "patents": [],
            "count": 0,
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"PATENTSVIEW_API_KEY": "test-key-123"}):
            call_command("fetch_patents", clear=True, limit_per_domain=1)

        self.assertEqual(Patent.objects.count(), 0)
