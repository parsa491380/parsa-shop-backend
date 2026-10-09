from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    """Populate Oscar's country table for the checkout flow."""

    help = "Populate Oscar shipping countries used by checkout."

    def handle(self, *args, **options):
        # Oscar provides this command and pycountry provides the country
        # dataset. Keeping it behind one project command makes first-time
        # setup simple for the store owner.
        call_command("oscar_populate_countries")
        self.stdout.write(
            self.style.SUCCESS(
                "Store bootstrap complete. Shipping countries are populated."
            )
        )
