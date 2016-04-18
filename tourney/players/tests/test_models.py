from unittest import skip

from django.test import TestCase

from model_mommy import mommy

from players.models import Player, Pool
from matches.models import Tournament, Round, Match


class PlayerTestCase(TestCase):

    def test_basics(self):
        """
        Test the basic funcionality of Player
        """
        player = mommy.make(Player)

        self.assertIsNotNone(player.name)
        self.assertIsNotNone(player.email)


class PoolTestCase(TestCase):

    def setUp(self, *args, **kwargs):
        self.pool = mommy.make(Pool)

    def test_basics(self):
        """
        Test the basic functionality of Pool
        """
        self.pool.players.add(mommy.make(Player))
        self.pool.players.add(mommy.make(Player))

        self.assertIsInstance(self.pool.tournament, Tournament)
        self.assertEqual(self.pool.players.count(), 2)

    def test__generate_matches(self):
        """
        Test that we can generate all the matches for a pool
        """
        for player in mommy.make(Player, _quantity=8):
            self.pool.players.add(player)

        self.pool._generate_matches()

        self.assertEqual(Round.objects.count(), 7)
        self.assertEqual(Match.objects.count(), 28)

        with self.subTest():
            for x in range(1,8):
                self.assertEqual(Match.objects.filter(round__number=x).count(), 4)

    def test__generate_matches_odd_number(self):
        """
        Test that we can generate matches for an odd number in a Pool
        """
        for player in mommy.make(Player, _quantity=3):
            self.pool.players.add(player)

        self.pool._generate_matches()

        self.assertEqual(Round.objects.count(), 3)
        self.assertEqual(Match.objects.count(), 3)

        with self.subTest():
            for x in range(1,3):
                self.assertEqual(Match.objects.filter(round__number=x).count(), 1)

    @skip('_generate_matches does not efficiently schedule 5 players')
    def test__generate_matches_five_players(self):
        """
        Test that we can generate matches for an odd number over 3 in a Pool
        """
        for player in mommy.make(Player, _quantity=5):
            self.pool.players.add(player)

        self.pool._generate_matches()

        self.assertEqual(Round.objects.count(), 5)
        self.assertEqual(Match.objects.count(), 10)

        with self.subTest():
            for x in range(1,5):
                self.assertEqual(Match.objects.filter(round__number=x).count(), 2)

    def test_get_player_standings(self):
        """
        Test that we can get a list of standings for a pool
        """
        player_1 = mommy.make(Player, name='player_1')
        player_2 = mommy.make(Player, name='player_2')
        player_3 = mommy.make(Player, name='player_3')
        player_4 = mommy.make(Player, name='player_4')
        self.pool.players.add(player_1, player_2, player_3, player_4)
        round_1 = mommy.make(Round, pool=self.pool)
        round_2 = mommy.make(Round, pool=self.pool)
        round_3 = mommy.make(Round, pool=self.pool)
        match_1 = mommy.make(Match, player_1_init=player_1, player_2_init=player_2,
                                    player_1_score=0, player_2_score=2, round=round_1)
        match_2 = mommy.make(Match, player_1_init=player_1, player_2_init=player_3,
                                    player_1_score=2, player_2_score=0, round=round_2)
        match_3 = mommy.make(Match, player_1_init=player_1, player_2_init=player_4,
                                    player_1_score=2, player_2_score=0, round=round_3)
        match_4 = mommy.make(Match, player_1_init=player_2, player_2_init=player_3,
                                    player_1_score=2, player_2_score=0, round=round_3)
        match_5 = mommy.make(Match, player_1_init=player_2, player_2_init=player_4,
                                    player_1_score=2, player_2_score=0, round=round_2)
        match_6 = mommy.make(Match, player_1_init=player_3, player_2_init=player_4,
                                    player_1_score=0, player_2_score=2, round=round_1)

        standings_list = self.pool.get_player_standings()

        self.assertEqual(standings_list[0], {'name': 'player_2', 'wins': 3, 'losses': 0})
        self.assertEqual(standings_list[1], {'name': 'player_1', 'wins': 2, 'losses': 1})
        self.assertEqual(standings_list[2], {'name': 'player_4', 'wins': 1, 'losses': 2})
        self.assertEqual(standings_list[3], {'name': 'player_3', 'wins': 0, 'losses': 3})
