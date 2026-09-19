import json
import os
import re
import requests
from django.core.management.base import BaseCommand, CommandError

from trends.models import Patent

API_URL = "https://search.patentsview.org/api/v1/patent/"

DOMAIN_CONFIG = {
    "AI/ML": {
        "_eq": {"cpc_current.cpc_subclass_id": "G06N"},
    },
    "Biotech": {
        "_or": [
            {"_eq": {"cpc_current.cpc_subclass_id": "A61K"}},
            {"_eq": {"cpc_current.cpc_subclass_id": "C12N"}},
        ],
    },
    "Energy Storage": {
        "_eq": {"cpc_current.cpc_subclass_id": "H01M"},
    },
    "IoT": {
        "_or": [
            {"_eq": {"cpc_current.cpc_subclass_id": "H04W"}},
            {"_eq": {"cpc_current.cpc_subclass_id": "H04L"}},
        ],
    },
    "Cybersecurity": {
        "_or": [
            {"_begins": {"cpc_current.cpc_group_id": "H04L9"}},
            {"_begins": {"cpc_current.cpc_group_id": "G06F21"}},
        ],
    },
}

REQUEST_FIELDS = [
    "patent_id",
    "patent_title",
    "patent_date",
    "patent_year",
    "num_times_cited_by_us_patents",
    "patent_num_cited_by_us_patents",
    "assignees.assignee_organization",
    "assignees.assignee_name_first",
    "assignees.assignee_name_last",
    "applications.filing_date",
    "cpc_current.cpc_subclass_id",
    "cpc_current.cpc_group_id",
    "cpc_current.cpc_group_title",
    "cpc_current.cpc_subgroup_title",
]

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "for", "in", "on", "with", "by", "to",
    "method", "system", "apparatus", "device", "composition", "process",
    "thereof", "using", "based", "use", "methods", "systems", "devices",
}


def derive_keywords(patent_data):
    """Extract descriptive keyword terms from CPC group titles and patent title."""
    keywords = []
    seen = set()

    cpc_list = patent_data.get("cpc_current") or []
    for cpc in cpc_list:
        title = cpc.get("cpc_group_title") or cpc.get("cpc_subgroup_title") or ""
        if title:
            cleaned = re.sub(r"[^\w\s-]", " ", title.lower()).strip()
            for part in re.split(r"\s{2,}|\s*;\s*|\s*,\s*", cleaned):
                part = part.strip()
                if part and len(part) > 2 and part not in seen and part not in STOPWORDS:
                    seen.add(part)
                    keywords.append(part)
                if len(keywords) >= 5:
                    break
        if len(keywords) >= 5:
            break

    if len(keywords) < 3:
        title = patent_data.get("patent_title") or ""
        words = re.findall(r"\b[a-zA-Z]{3,}\b", title.lower())
        for w in words:
            if w not in STOPWORDS and w not in seen:
                seen.add(w)
                keywords.append(w)
            if len(keywords) >= 5:
                break

    return ", ".join(keywords[:5])


def parse_assignee(patent_data):
    """Extract assignee organization or person name from API response."""
    assignees = patent_data.get("assignees") or []
    for assignee in assignees:
        org = assignee.get("assignee_organization")
        if org and org.strip():
            return org.strip()[:150]
        first = assignee.get("assignee_name_first") or ""
        last = assignee.get("assignee_name_last") or ""
        full = f"{first} {last}".strip()
        if full:
            return full[:150]
    return "Unassigned"


def parse_filing_year(patent_data):
    """Extract filing year from applications or fallback to patent grant year."""
    applications = patent_data.get("applications") or []
    for app in applications:
        filing_date = app.get("filing_date") or ""
        if len(filing_date) >= 4 and filing_date[:4].isdigit():
            year = int(filing_date[:4])
            if 1900 <= year <= 2100:
                return year

    patent_year = patent_data.get("patent_year")
    if patent_year:
        try:
            year = int(patent_year)
            if 1900 <= year <= 2100:
                return year
        except (ValueError, TypeError):
            pass

    patent_date = patent_data.get("patent_date") or ""
    if len(patent_date) >= 4 and patent_date[:4].isdigit():
        year = int(patent_date[:4])
        if 1900 <= year <= 2100:
            return year

    return 2022


def parse_citations(patent_data):
    """Extract citation count from response fields."""
    count = (
        patent_data.get("num_times_cited_by_us_patents")
        or patent_data.get("patent_num_cited_by_us_patents")
        or 0
    )
    try:
        return max(0, int(count))
    except (ValueError, TypeError):
        return 0


class Command(BaseCommand):
    help = (
        "Fetch patent records from PatentsView Search API v1 "
        "and load them into the database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing Patent rows before fetching.",
        )
        parser.add_argument(
            "--limit-per-domain",
            type=int,
            default=60,
            help="Maximum number of patents to fetch per domain (default: 60).",
        )
        parser.add_argument(
            "--page-size",
            type=int,
            default=50,
            help="Page size for PatentsView API requests (default: 50).",
        )

    def handle(self, *args, **options):
        api_key = os.environ.get("PATENTSVIEW_API_KEY")
        if not api_key:
            raise CommandError(
                "PATENTSVIEW_API_KEY environment variable is not set. "
                "Get a free API key at https://search.patentsview.org/ and set "
                "PATENTSVIEW_API_KEY before running fetch_patents."
            )

        if options["clear"]:
            deleted, _ = Patent.objects.all().delete()
            self.stdout.write(f"Cleared {deleted} existing patent records.")

        limit_per_domain = options["limit_per_domain"]
        page_size = min(options["page_size"], 100)
        headers = {
            "X-Api-Key": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        total_saved = 0

        for domain, query_clause in DOMAIN_CONFIG.items():
            self.stdout.write(f"Fetching patents for domain: {domain}...")
            domain_saved = 0
            page = 1

            while domain_saved < limit_per_domain:
                current_size = min(page_size, limit_per_domain - domain_saved)
                params = {
                    "q": json.dumps(query_clause),
                    "f": json.dumps(REQUEST_FIELDS),
                    "o": json.dumps({"page": page, "size": current_size}),
                }

                try:
                    response = requests.get(
                        API_URL,
                        headers=headers,
                        params=params,
                        timeout=30,
                    )
                except requests.RequestException as exc:
                    raise CommandError(
                        f"Failed to connect to PatentsView API for domain {domain}: {exc}"
                    )

                if response.status_code != 200:
                    raise CommandError(
                        f"PatentsView API error (status {response.status_code}): {response.text}"
                    )

                data = response.json()
                patents = data.get("patents") or []
                if not patents:
                    break

                for item in patents:
                    title = (item.get("patent_title") or f"Patent {item.get('patent_id', '')}").strip()[:255]
                    assignee = parse_assignee(item)
                    filing_year = parse_filing_year(item)
                    citation_count = parse_citations(item)
                    keywords = derive_keywords(item)

                    Patent.objects.update_or_create(
                        title=title,
                        filing_year=filing_year,
                        technology_domain=domain,
                        defaults={
                            "assignee": assignee,
                            "citation_count": citation_count,
                            "keywords": keywords,
                        },
                    )
                    domain_saved += 1
                    if domain_saved >= limit_per_domain:
                        break

                if len(patents) < current_size:
                    break

                page += 1

            self.stdout.write(f"  Loaded {domain_saved} patents for {domain}.")
            total_saved += domain_saved

        self.stdout.write(
            self.style.SUCCESS(f"Successfully loaded {total_saved} patents across all domains.")
        )
