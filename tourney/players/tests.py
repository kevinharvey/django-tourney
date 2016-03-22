from django.test import TestCase

from model_mommy import mommy

from players.models import Player


class PlayerTestCase(TestCase):

    def test_basics(self):
        """
        Test the basic funcionality of Player
        """
        player = mommy.make(Player)

        self.assertIsNotNone(player.name)
        self.assertIsNotNone(player.email)
