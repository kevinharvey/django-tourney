from django.test import TestCase, RequestFactory

from model_mommy import mommy

from matches.models import Tournament
from players.models import Pool
from matches.views import TournamentDetailView


class TournamentDetailViewTestCase(TestCase):

    def setUp(self, *args, **kwargs):
        self.factory = RequestFactory()

        self.tournament = mommy.make(Tournament)
        self.pools = mommy.make(Pool, tournament=self.tournament, _quantity=4)

    def test_tournament_detail_view(self):
        """
        Test that we get the correct context for a Tournament
        """
        request = self.factory.get('/{}/'.format(self.tournament.slug))

        response = TournamentDetailView.as_view()(request, slug=self.tournament.slug)

        self.assertEqual(response.context_data['object'], self.tournament)
        with self.assertNumQueries(1):
            response.render()
