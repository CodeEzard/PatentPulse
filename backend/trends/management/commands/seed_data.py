import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from trends.models import Patent


class Command(BaseCommand):
    help = "Load offline patent records from data/sample_patents.csv into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing Patent rows before loading.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            deleted, _ = Patent.objects.all().delete()
            self.stdout.write(f"Cleared {deleted} existing rows.")

        csv_path = Path(settings.BASE_DIR) / "data" / "sample_patents.csv"
        if not csv_path.exists():
            raise CommandError(f"Fixture file not found at {csv_path}")

        created = 0
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                Patent.objects.update_or_create(
                    title=row["title"],
                    filing_year=int(row["filing_year"]),
                    technology_domain=row["technology_domain"],
                    defaults={
                        "assignee": row["assignee"],
                        "citation_count": int(row["citation_count"]),
                        "keywords": row["keywords"],
                    },
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded {created} patent records."))
