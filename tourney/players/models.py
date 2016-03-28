from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()


class Pool(models.Model):
    tournament = models.ForeignKey('matches.Tournament')
    players = models.ManyToManyField('players.Player')
