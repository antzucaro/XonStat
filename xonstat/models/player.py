"""
Models related to players.
"""

from calendar import timegm

from xonstat.util import html_colors, strip_colors, pretty_date, qfont_decode


class Player(object):
    """
    A player, which can represent either a human or a bot.
    """

    def nick_html_colors(self, limit=None):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return html_colors(self.nick, limit)

    def nick_strip_colors(self):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return strip_colors(self.nick)

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

    def epoch(self):
        return timegm(self.create_dt.timetuple())


class Achievement(object):
    """
    A type of achievement. Referenced implicitly in PlayerAchievement.
    """

    def __repr__(self):
        return "<Achievement({}, {}, {})>".format(self.achievement_cd, self.descr, self.limit)

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
        return "<PlayerAchievement({}, {})>".format(self.player_id, self.achievement_cd)

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
        return "<Hashkey({}, {})>".format(self.player_id, self.hashkey)

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
        return "<PlayerNick({}, {})>".format(self.player_id, qfont_decode(self.stripped_nick))

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
        return ("<PlayerElo(pid={}, gametype={}, elo={}, games={})>"
                .format(self.player_id, self.game_type_cd, self.elo, self.games))

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'game_type_cd': self.game_type_cd,
            'elo': self.elo,
            'games': self.games,
        }


class PlayerRank(object):
    """
    A player's rank for a given game type.
    """

    def nick_html_colors(self, limit=None):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return html_colors(self.nick, limit)

    def __repr__(self):
        return ("<PlayerRank(pid={}, gametype={}, rank={})>"
                .format(self.player_id, self.game_type_cd, self.rank))

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'game_type_cd': self.game_type_cd,
            'rank': self.rank
        }


class PlayerCaptime(object):
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
        return ("<PlayerCaptime(pid={}, map_id={}, mod={})>"
                .format(self.player_id, self.map_id, self.mod))

    def fuzzy_date(self):
        return pretty_date(self.create_dt)

    def epoch(self):
        return timegm(self.create_dt.timetuple())


class PlayerGroups(object):
    """
    An authorization group a player belongs to. Used to control access.
    """

    def __init__(self, player_id=None, group_name=None):
        self.player_id  = player_id
        self.group_name = group_name

    def __repr__(self):
        return "<PlayerGroups({}, {})>".format(self.player_id, self.group_name)


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
        return "<PlayerRank(pid={}, place={}, alt={})>".format(self.player_id, self.place, self.alt)
