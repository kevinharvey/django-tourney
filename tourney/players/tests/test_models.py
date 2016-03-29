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

    def test_basics(self):
        """
        Test the basic functionality of Pool
        """
        pool = mommy.make(Pool)
        pool.players.add(mommy.make(Player))
        pool.players.add(mommy.make(Player))

        self.assertIsInstance(pool.tournament, Tournament)
        self.assertEqual(pool.players.count(), 2)

    def test__generate_matches(self):
        """
        Test that we can generate all the matches for a pool
        """
        pool = mommy.make(Pool)
        for player in mommy.make(Player, _quantity=8):
            pool.players.add(player)

        pool._generate_matches()

        self.assertEqual(Round.objects.count(), 7)
        self.assertEqual(Match.objects.count(), 28)

        with self.subTest():
            for x in range(1,8):
                self.assertEqual(Match.objects.filter(round__number=x).count(), 4)
