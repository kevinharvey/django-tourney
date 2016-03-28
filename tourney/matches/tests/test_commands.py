from unittest import mock
import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.management import call_command

from model_mommy import mommy

from matches.models import Bracket, Round, Match, MatchNotification
from players.models import Player


class SendCurrentMatchupsTestCase(TestCase):

    @mock.patch('matches.models.Match.notify_players')
    def test_sendcurrentmatchups(self, mock_notify_players):
        """
        Test that we call notify_players for any current matchups
        """
        bracket = mommy.make(Bracket)
        round_1 = mommy.make(Round, bracket=bracket,
                             start_datetime=timezone.now()-datetime.timedelta(days=8),
                             end_datetime=timezone.now()-datetime.timedelta(days=1))
        round_2 = mommy.make(Round, bracket=bracket,
                             start_datetime=timezone.now()-datetime.timedelta(days=1),
                             end_datetime=timezone.now()+datetime.timedelta(days=6))
        round_3 = mommy.make(Round, bracket=bracket,
                             start_datetime=timezone.now()+datetime.timedelta(days=6),
                             end_datetime=timezone.now()+datetime.timedelta(days=13))
        match_1 = mommy.make(Match, player_1_init=mommy.make(Player),
                             player_2_init=mommy.make(Player),
                             round=round_1)
        match_2 = mommy.make(Match, player_1_init=mommy.make(Player),
                             player_2_init=mommy.make(Player),
                             round=round_2)
        match_3 = mommy.make(Match, player_1_init=mommy.make(Player),
                             player_2_init=mommy.make(Player),
                             round=round_2)
        match_4 = mommy.make(Match, player_1_init=mommy.make(Player),
                             player_2_init=mommy.make(Player),
                             round=round_3)

        call_command('sendcurrentmatchups')

        self.assertEqual(mock_notify_players.call_count, 2)
