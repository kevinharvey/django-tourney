from random import shuffle
import json

import pytz

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils import timezone
from django.utils.text import slugify

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

    def __str__(self):
        return self.name


class Bracket(models.Model):
    name = models.CharField(max_length=100, help_text='The public name for the bracket')
    slug = models.SlugField(max_length=100)
    tournament = models.ForeignKey(Tournament)

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
            round, created = Round.objects.get_or_create(
                bracket=self,
                number=1
            )
            match = Match(
                player_1_init=players.pop(),
                player_2_init=players.pop(),
                round=round,
                round_index=int(i/2)
            )
            match.save()
            initial_matches.append(match)

        def recurse(matches, round_number):
            """
            Make downstream matches recursively
            """
            new_round, created = Round.objects.get_or_create(
                bracket=self,
                number=round_number
            )

            new_matches = []
            i = 0
            while i < len(matches):
                match = Match(
                    previous_match_1=matches.pop(),
                    previous_match_2=matches.pop(),
                    round=new_round,
                    round_index=int(i/2)
                )
                match.save()
                new_matches.append(match)

            if len(new_matches) > 1:
                recurse(matches=new_matches, round_number=round_number+1)

        recurse(matches=initial_matches, round_number=2)

    def to_json(self):
        """
        Generate JSON for consumption by jQuery Bracket
        (http://www.aropupu.fi/bracket/)
        """
        data = {'teams':[], 'results':[[]]}
        matches = Match.objects.filter(round__bracket=self).order_by('round__number', 'round_index')

        for match in matches:
            if match.round.number == 1:
                data['teams'].append([match.player_1.name, match.player_2.name])

            if len(data['results'][0]) < match.round.number:
                data['results'][0].append([])

            result = []
            if (match.player_1_score is not None) and (match.player_2_score is not None):
                result = [match.player_1_score, match.player_2_score]

            data['results'][0][match.round.number-1].append(result)

        return json.dumps(data)


class Round(models.Model):
    bracket_pool_help_text = 'Set either the bracket or pool field'
    number = models.PositiveIntegerField()
    bracket = models.ForeignKey(Bracket, blank=True, null=True,
                                help_text=bracket_pool_help_text)
    pool = models.ForeignKey('players.Pool', blank=True, null=True,
                             help_text=bracket_pool_help_text)
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Disallow the bracket and pool fields to be set simultaneously
        """
        error_message = 'A round must be part of a single Pool or a single Bracket'
        if self.bracket and self.pool:
            raise ValidationError(error_message)

        if (not self.bracket) and (not self.pool):
            raise ValidationError(error_message)

        super().save(*args, **kwargs)

    def __str__(self):
        representation = 'Round {}'.format(self.number)

        if self.start_datetime:
            representation = '{} ({} - {})'.format(representation, self.number, self.start_datetime.strftime('%b %d'), self.end_datetime.strftime('%b %d'))

        if self.pool:
            representation = 'Pool {} {}'.format(self.pool.id, representation)

        if self.bracket:
            representation = '{} {}'.format(self.bracket.name, representation)

        return representation


class Match(models.Model):
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
    round = models.ForeignKey(Round, blank=True, null=True)
    round_index = models.PositiveIntegerField(
        help_text='The order of this match in the round (used for positioning).'
    )

    def __str__(self):
        return '{} vs. {}'.format(self.player_1, self.player_2)

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

    def notify_players(self):
        """
        Send an email to the players in a match, notifying of their partner and
        when they need to complete their match
        """
        if self.notifications.count():
            return 'The players in match {} have already been notified'.format(self.id)

        user_time_zone = pytz.timezone(settings.DEFAULT_USER_TIME_ZONE)

        template = get_template('matches/notify_players.txt')
        message = template.render({
            'player_1_name': self.player_1.name,
            'player_2_name': self.player_2.name,
            'round_end_datetime': self.round.end_datetime.astimezone(user_time_zone).strftime('%A, %B %d at %I:%M %p %Z'),
            'organizer_email': settings.DEFAULT_ORGANIZER_EMAIL
        })

        email = EmailMessage(
            to=[self.player_1.email, self.player_2.email],
            from_email=settings.DEFAULT_FROM_EMAIL,
            bcc=[settings.DEFAULT_ORGANIZER_EMAIL],
            subject='Your Next Matchup',
            reply_to=[self.player_1.email, self.player_2.email],
            body=message
        )
        email.send()

        notification = MatchNotification(match=self, sent=timezone.now())
        notification.save()


class MatchNotification(models.Model):
    match = models.ForeignKey(Match, related_name='notifications')
    sent = models.DateTimeField()
