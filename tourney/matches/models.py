from random import shuffle
import json

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from players.models import Player


class Tournament(models.Model):
    name = models.CharField(max_length=100, help_text='The public name of the tournament')
    slug = models.SlugField(max_length=100)
    players = models.ManyToManyField(Player)

    def save(self, *args, **kwargs):
        """
        Make a slug from Tournament.name
        """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Bracket(models.Model):
    name = models.CharField(max_length=100, help_text='The public name for the bracket')
    slug = models.SlugField(max_length=100)

    def save(self, *args, **kwargs):
        """
        Make a slug from Bracket.name
        """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def _generate_matches(self, players):
        """
        Generate matches for a list of players
        """
        shuffle(players)

        initial_matches = []
        i = 0
        while i < len(players):
            match = Match(
                player_1_init=players.pop(),
                player_2_init=players.pop(),
                bracket=self,
                round=1,
                round_index=int(i/2)
            )
            match.save()
            initial_matches.append(match)

        def recurse(matches, round):
            """
            Make downstream matches recursively
            """
            new_matches = []
            i = 0
            while i < len(matches):
                match = Match(
                    previous_match_1=matches.pop(),
                    previous_match_2=matches.pop(),
                    bracket=self,
                    round=round,
                    round_index=int(i/2)
                )
                match.save()
                new_matches.append(match)

            if len(new_matches) > 1:
                recurse(matches=new_matches, round=round+1)

        recurse(matches=initial_matches, round=2)

    def to_json(self):
        """
        Generate JSON for consumption by jQuery Bracket
        (http://www.aropupu.fi/bracket/)
        """
        data = {'teams':[], 'results':[[]]}
        matches = Match.objects.filter(bracket=self).order_by('round', 'round_index')

        for match in matches:
            if match.round == 1:
                data['teams'].append([match.player_1.name, match.player_2.name])

            if len(data['results'][0]) < match.round:
                data['results'][0].append([])

            result = []
            if (match.player_1_score is not None) and (match.player_2_score is not None):
                result = [match.player_1_score, match.player_2_score]

            data['results'][0][match.round-1].append(result)

        return json.dumps(data)


class Match(models.Model):
    bracket = models.ForeignKey(Bracket)
    player_1_init = models.ForeignKey(Player, blank=True, null=True,
                                      related_name='home_game_match',
                                      help_text='Set for first round matches')
    player_2_init = models.ForeignKey(Player, blank=True, null=True,
                                      related_name='away_game_match',
                                      help_text='Set for first round matches')
    previous_match_1 = models.ForeignKey('Match', blank=True, null=True,
                                         related_name='subsequent_match_1')
    previous_match_2 = models.ForeignKey('Match', blank=True, null=True,
                                         related_name='subsequent_match_2')
    player_1_score = models.PositiveIntegerField(blank=True, null=True)
    player_2_score = models.PositiveIntegerField(blank=True, null=True)
    round = models.PositiveIntegerField()
    round_index = models.PositiveIntegerField(
        help_text='The order of this match in the round (used for positioning).'
    )

    @property
    def player_1(self):
        """
        Return player_1_init or the winner of previous_match_1
        """
        return self.player_1_init or self.previous_match_1.winner()

    @property
    def player_2(self):
        """
        Return player_2_init or the winner of previous_match_2
        """
        return self.player_2_init or self.previous_match_2.winner()

    def winner(self):
        """
        Return the player with the highest score for the match
        """
        if not self.player_1_score or not self.player_2_score:
            return

        if self.player_1_score > self.player_2_score:
            return self.player_1
        if self.player_2_score > self.player_1_score:
            return self.player_2

    def save(self, *args, **kwargs):
        """
        Confirm that either both player fields or both match fields are set
        """
        player_error = False

        if (self.player_1_init and not self.player_2_init) or (self.player_2_init and not self.player_1_init):
            player_error = True

        if (self.previous_match_1 and not self.previous_match_2) or (self.previous_match_2 and not self.previous_match_1):
            player_error = True

        if (not self.player_1_init and not self.player_2_init) and (not self.previous_match_1 and not self.previous_match_2):
            player_error = True

        if (self.player_1_init or self.player_2_init) and (self.previous_match_1 or self.previous_match_2):
            player_error = True

        if player_error:
            raise ValidationError('Either both player fields or both match fields must be set.')

        super().save(*args, **kwargs)
