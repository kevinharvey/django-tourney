from django.views.generic import DetailView

from matches.models import Tournament


class TournamentDetailView(DetailView):
    model = Tournament
