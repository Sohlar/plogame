from django.core.management.base import BaseCommand
from decision_tree.models import PotType, Position, Player, FlopTexture, BetSize, BetFrequency

class Command(BaseCommand):
    help = 'Display poker data from the database'

    def handle(self, *args, **options):
        self.stdout.write("PotTypes:")
        for pt in PotType.objects.all():
            self.stdout.write(f"- {pt.name}")

        self.stdout.write("\nBetSizes:")
        for bs in BetSize.objects.all():
            self.stdout.write(f"- {bs}")

        self.stdout.write("\nBetFrequencies:")
        for bf in BetFrequency.objects.all():
            self.stdout.write(f"- {bf}")