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
