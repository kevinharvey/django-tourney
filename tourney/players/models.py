from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return '{} ({})'.format(self.name, self.email)


class Pool(models.Model):
    tournament = models.ForeignKey('matches.Tournament')
    players = models.ManyToManyField('players.Player')

    def __str__(self):
        return '{} - Pool {}'.format(self.tournament.name, self.id)

    def _generate_matches(self):
        """
        Create a match for each set of 2 players in the pool, and rounds to hold
        them
        """
        from matches.models import Match, Round

        rounds = {}
        players = [player for player in self.players.all()]

        if len(players) % 2 != 0: players.append(None)

        iterator = list(range(len(players)))
        for x in iterator:
            if x == 0: continue
            round = Round(pool=self, number=x)
            round.save()
            rounds[round] = []

        for x in iterator:
            if not players[x]: continue

            others_iterator = iterator.copy()
            others_iterator.remove(x)

            for y in others_iterator:
                if not players[y]: continue

                match_exists = Match.objects.filter(player_1_init=players[x], player_2_init=players[y]).exists()
                inverse_match_exists = Match.objects.filter(player_1_init=players[y], player_2_init=players[x]).exists()

                if match_exists or inverse_match_exists:
                    continue

                for scheduled_round, players_in_round in rounds.items():
                    if (players[x] not in players_in_round) and (players[y] not in players_in_round):
                        break

                match = Match(
                    player_1_init=players[x],
                    player_2_init=players[y],
                    round=scheduled_round,
                    round_index=0
                )
                match.save()
                rounds[scheduled_round] += [players[x], players[y]]

    def get_player_standings(self):
        """
        Return a list of dictionaries describing the standings (player name and
        win/loss record)
        """
        records = []
        rounds = self.round_set.all()

        for round_object in rounds:
            for match in round_object.match_set.all():
                if not any(d['name'] == match.player_1.name for d in records):
                    records.append({'name': match.player_1.name, 'wins': 0, 'losses': 0})
                if not any(d['name'] == match.player_2.name for d in records):
                    records.append({'name': match.player_2.name, 'wins': 0, 'losses': 0})

                player_1_record = next((record for record in records if record['name'] == match.player_1.name), None)
                player_2_record = next((record for record in records if record['name'] == match.player_2.name), None)

                if match.winner() == match.player_1:
                    player_1_record['wins'] += 1
                    player_2_record['losses'] += 1

                if match.winner() == match.player_2:
                    player_2_record['wins'] += 1
                    player_1_record['losses'] += 1

        records_by_losses = sorted(records, key=lambda k: k['losses'])
        records_by_wins = sorted(records, key=lambda k: k['wins'], reverse=True)

        return records_by_wins
