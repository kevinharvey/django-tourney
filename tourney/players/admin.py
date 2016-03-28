from django.contrib import admin
from django import forms

from players.models import Pool, Player


class PoolAdmin(admin.ModelAdmin):
    filter_horizontal = ('players',)


admin.site.register(Pool, PoolAdmin)
admin.site.register(Player)
