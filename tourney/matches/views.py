from django.views.generic import DetailView

from matches.models import Tournament, Bracket


class TournamentDetailView(DetailView):
    model = Tournament

    def get_bracket_json(self):
        if Bracket.objects.filter(tournament=self.object):
            return Bracket.objects.get(tournament=self.object).to_json()

        return None
