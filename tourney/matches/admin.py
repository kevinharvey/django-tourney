from django.contrib import admin

from matches.models import Tournament, Bracket, Round, Match, MatchNotification


admin.site.register(Tournament)
admin.site.register(Bracket)
admin.site.register(Round)
admin.site.register(Match)
admin.site.register(MatchNotification)
