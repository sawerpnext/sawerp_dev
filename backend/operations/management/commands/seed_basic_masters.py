from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Deprecated: thin wrapper around seed_coa. Prefer 'python manage.py seed_coa'."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Pass-through to seed_coa --reset.",
        )

    def handle(self, *args, **options):
        reset = options.get("reset") or False

        self.stdout.write(self.style.WARNING(
            "seed_basic_masters is now a wrapper around seed_coa. "
            "Prefer using 'python manage.py seed_coa' directly."
        ))

        if reset:
            call_command("seed_coa", reset=True)
        else:
            call_command("seed_coa")
