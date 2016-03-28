from django.test import TestCase

from model_mommy import mommy

from players.models import Player, Pool
from matches.models import Tournament


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
