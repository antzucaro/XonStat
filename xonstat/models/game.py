"""
Models related to games.
"""

from xonstat.models.mixins import FuzzyDateMixin, EpochMixin
from xonstat.util import strip_colors, html_colors


class Game(FuzzyDateMixin, EpochMixin):
    """
    An individual game.
    """

    def __init__(self, game_id=None, start_dt=None, game_type_cd=None, server_id=None, map_id=None,
                 winner=None):
        self.game_id = game_id
        self.start_dt = start_dt
        self.game_type_cd = game_type_cd
        self.server_id = server_id
        self.map_id = map_id
        self.winner = winner

    def __repr__(self):
        return "<Game({0.game_id}, {0.start_dt}, {0.game_type_cd}, {0.server_id})>".format(self)

    def to_dict(self):
        return {
            'game_id': self.game_id,
            'start': self.start_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'game_type_cd': self.game_type_cd,
            'server_id': self.server_id
        }


class PlayerGameStat(object):
    """
    The individual statistics a player has gained/lost during a game.
    """

    def __init__(self, player_game_stat_id=None, create_dt=None):
        self.player_game_stat_id = player_game_stat_id
        self.create_dt = create_dt

    def __repr__(self):
        return "<PlayerGameStat({0.player_id}, {0.game_id}, {0.create_dt})>".format(self)

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'game_id': self.game_id,
            'create_dt': self.create_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'alivetime': self.alivetime,
            'rank': self.rank,
            'score': self.score,
            'team': self.team
        }

    def nick_stripped(self):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return strip_colors(self.nick)

    def nick_html_colors(self, limit=None):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return html_colors(self.nick, limit)

    def team_html_color(self):
        if self.team == 5:
            return "red"
        if self.team == 14:
            return "blue"
        if self.team == 13:
            return "yellow"
        if self.team == 10:
            return "pink"


class PlayerWeaponStat(object):
    """
    The metrics for a single weapon in a game for a player.
    """

    def __init__(self, player_id=None, game_id=None, weapon_cd=None):
        self.player_id = player_id
        self.game_id = game_id
        self.weapon_cd = weapon_cd
        self.fired = 0
        self.max = 0
        self.hit = 0
        self.actual = 0
        self.frags = 0

    def __repr__(self):
        return ("<PlayerWeaponStat({0.player_weapon_stats_id}, {0.player_id}, {0.game_id})>"
                .format(self))

    def to_dict(self):
        return {
            'weapon_cd': self.weapon_cd,
            'player_weapon_stats_id': self.player_weapon_stats_id,
            'player_id': self.player_id,
            'game_id': self.game_id,
            'fired': self.fired,
            'max': self.max,
            'hit': self.hit,
            'actual': self.actual,
            'frags': self.frags,
        }


class TeamGameStat(object):
    """
    Team level metrics.
    """

    def __init__(self, team_game_stat_id=None, create_dt=None):
        self.team_game_stat_id = team_game_stat_id
        self.create_dt = create_dt

    def __repr__(self):
        return "<TeamGameStat({0.team_game_stat_id}, {0.game_id}, {0.team})>".format(self)

    def to_dict(self):
        return {
            'team_game_stat_id': self.team_game_stat_id,
            'game_id': self.game_id,
            'team': self.team,
            'score': self.score,
            'rounds': self.rounds,
            'caps': self.caps,
            'create_dt': self.create_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }

    # TODO: move this function to util
    def team_html_color(self):
        if self.team == 5:
            return "red"
        if self.team == 14:
            return "blue"
        if self.team == 13:
            return "yellow"
        if self.team == 10:
            return "pink"


class PlayerGameAnticheat(object):
    """
    Anticheat metrics sent by the server to identify odd patterns.
    """

    def __init__(self, player_id=None, game_id=None, key=None, value=None, create_dt=None):
        self.player_id = player_id
        self.game_id = game_id
        self.key = key
        self.value = value
        self.create_dt = create_dt

    def __repr__(self):
        return "<PlayerGameAnticheat({0.key}, {0.value})>".format(self)


class GameType(object):
    """
    A particular type of game.
    """

    def __repr__(self):
        return "<GameType({0.game_type_cd}, {0.descr}, {0.active_ind})>".format(self)

    def to_dict(self):
        return {
            'game_type_cd': self.game_type_cd,
            'name': self.descr,
            'active': self.active_ind,
        }


class Weapon(object):
    """
    A particular type of weapon.
    """

    def __repr__(self):
        return "<Weapon({0.weapon_cd}, {0.descr}, {0.active_ind})>".format(self)

    def to_dict(self):
        return {
            'weapon_cd': self.weapon_cd,
            'name': self.descr,
            'active': self.active_ind,
        }


class PlayerGameFragMatrix(object):
    """
    Frags made by an individual player in a single game.
    """

    def __init__(self, game_id, player_game_stat_id, player_id, player_index, matrix):
        self.game_id = game_id
        self.player_game_stat_id = player_game_stat_id
        self.player_id = player_id
        self.player_index = player_index
        self.matrix = matrix

    def __repr__(self):
        return "<PlayerGameFragMatrix({0.game_id}, {0.player_game_stat_id})>".format(self)
