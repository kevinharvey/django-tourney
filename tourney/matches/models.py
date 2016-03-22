from django.db import models
from django.core.exceptions import ValidationError

from players.models import Player


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
