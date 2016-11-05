"""
Models related to players.
"""

from calendar import timegm

from xonstat.models.mixins import FuzzyDateMixin, EpochMixin, NickColorsMixin
from xonstat.util import strip_colors, pretty_date, qfont_decode


class Player(EpochMixin, NickColorsMixin):
    """
    A player, which can represent either a human or a bot.
    """

    def nick_strip_colors(self):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return strip_colors(self.nick)

    # TODO: use FuzzyDateMixin instead, but change the method calls
    def joined_pretty_date(self):
        return pretty_date(self.create_dt)

    def __repr__(self):
        return "<Player({}, {})>".format(self.player_id, self.nick.encode('utf-8'))

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'nick': self.nick,
            'joined': self.create_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'active_ind': self.active_ind,
            'location': self.location,
            'stripped_nick': qfont_decode(self.stripped_nick),
        }


class Achievement(object):
    """
    A type of achievement. Referenced implicitly in PlayerAchievement.
    """

    def __repr__(self):
        return "<Achievement({0.achievement_cd}, {0.descr}, {0.limit})>".format(self)

    def to_dict(self):
        return {
            'achievement_cd': self.achievement_cd,
            'name': self.descr,
            'limit':self.limit,
        }


class PlayerAchievement(object):
    """
    Achievements a player has earned.
    """

    def __repr__(self):
        return "<PlayerAchievement({0.player_id}, {0.achievement_cd})>".format(self)

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'achievement_cd': self.achievement_cd,
        }


class Hashkey(object):
    """
    A player's identifying key from the d0_blind_id library.
    """

    def __init__(self, player_id=None, hashkey=None):
        self.player_id = player_id
        self.hashkey = hashkey

    def __repr__(self):
        return "<Hashkey({0.player_id}, {0.hashkey})>".format(self)

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'hashkey': self.hashkey
        }


class PlayerNick(object):
    """
    A single nickname a player has used in a game.
    """

    def __repr__(self):
        return "<PlayerNick({0.player_id}, {0.stripped_nick})>".format(self)

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'name': qfont_decode(self.stripped_nick),
        }


class PlayerElo(object):
    """
    A player's skill for a particular game type, as determined by a modified Elo algorithm.
    """

    def __init__(self, player_id=None, game_type_cd=None, elo=None):
        self.player_id = player_id
        self.game_type_cd = game_type_cd
        self.elo = elo
        self.score = 0
        self.games = 0

    def __repr__(self):
        return ("<PlayerElo(pid={0.player_id}, gametype={0.game_type_cd}, elo={0.elo}, "
                "games={0.games})>".format(self))

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'game_type_cd': self.game_type_cd,
            'elo': self.elo,
            'games': self.games,
        }


class PlayerRank(NickColorsMixin):
    """
    A player's rank for a given game type.
    """

    def __repr__(self):
        return ("<PlayerRank(pid={0.player_id}, gametype={0.game_type_cd}, rank={0.rank})>"
                .format(self))

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'game_type_cd': self.game_type_cd,
            'rank': self.rank
        }


class PlayerCaptime(FuzzyDateMixin, EpochMixin):
    """
    A flag capture time for a player on a given map.
    """

    def __init__(self, player_id=None, game_id=None, map_id=None, fastest_cap=None, mod=None):
        self.player_id = player_id
        self.game_id = game_id
        self.map_id = map_id
        self.fastest_cap = fastest_cap
        self.mod = mod

    def __repr__(self):
        return "<PlayerCaptime(pid={0.player_id}, map_id={0.map_id}, mod={0.mod})>".format(self)


class PlayerGroups(object):
    """
    An authorization group a player belongs to. Used to control access.
    """

    def __init__(self, player_id=None, group_name=None):
        self.player_id  = player_id
        self.group_name = group_name

    def __repr__(self):
        return "<PlayerGroups({0.player_id}, {0.group_name})>".format(self)


# TODO: determine if this is a real model (it is very similar to PlayerCaptime from above)
class PlayerCapTime(object):
    """
    Fastest flag capture times per player.
    """

    def __init__(self, row):
        self.fastest_cap = row.fastest_cap
        self.create_dt = row.create_dt
        self.create_dt_epoch = timegm(row.create_dt.timetuple())
        self.create_dt_fuzzy = pretty_date(row.create_dt)
        self.player_id = row.player_id
        self.game_id = row.game_id
        self.map_id = row.map_id
        self.map_name = row.map_name
        self.server_id = row.server_id
        self.server_name = row.server_name

    def to_dict(self):
        return {
            "fastest_cap" : self.fastest_cap.total_seconds(),
            "create_dt_epoch": self.create_dt_epoch,
            "create_dt_fuzzy": self.create_dt_fuzzy,
            "game_id":self.game_id,
            "map_id": self.map_id,
            "map_name": self.map_name,
            "server_id": self.server_id,
            "server_name": self.server_name,
        }


class PlayerMedal(object):
    """
    A medal a player has earned in a large tournament.
    """

    def __repr__(self):
        return "<PlayerRank(pid={0.player_id}, place={0.place}, alt={0.alt})>".format(self)
