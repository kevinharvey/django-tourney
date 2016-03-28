from django.core.management.base import BaseCommand
from django.utils import timezone

from matches.models import Match


class Command(BaseCommand):
    help = 'Send eamil notifications to the players in the current round of matches'

    def handle(self, *args, **options):
        matches = Match.objects.filter(round__start_datetime__lte=timezone.now(),
                                       round__end_datetime__gte=timezone.now())

        for match in matches:
            match.notify_players()
