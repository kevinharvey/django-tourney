from django.contrib import admin

from matches.models import Tournament, Bracket, Round, Match, MatchNotification


class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'round',)
    list_filter = ('round__pool', 'round__number',)

admin.site.register(Tournament)
admin.site.register(Bracket)
admin.site.register(Round)
admin.site.register(Match, MatchAdmin)
admin.site.register(MatchNotification)
