from calendar import timegm

from xonstat.util import pretty_date, strip_colors, html_colors


class Game(object):
    def __init__(self, game_id=None, start_dt=None, game_type_cd=None,
            server_id=None, map_id=None, winner=None):
        self.game_id = game_id
        self.start_dt = start_dt
        self.game_type_cd = game_type_cd
        self.server_id = server_id
        self.map_id = map_id
        self.winner = winner

    def __repr__(self):
        return "<Game(%s, %s, %s, %s)>" % (self.game_id, self.start_dt, self.game_type_cd, self.server_id)

    def to_dict(self):
        return {'game_id':self.game_id, 'start':self.start_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'game_type_cd':self.game_type_cd, 'server_id':self.server_id}

    def fuzzy_date(self):
        return pretty_date(self.start_dt)

    def epoch(self):
        return timegm(self.start_dt.timetuple())


class PlayerGameStat(object):
    def __init__(self, player_game_stat_id=None, create_dt=None):
        self.player_game_stat_id = player_game_stat_id
        self.create_dt = create_dt

    def __repr__(self):
        return "<PlayerGameStat(%s, %s, %s)>" % (self.player_id, self.game_id, self.create_dt)

    def to_dict(self):
        return {'player_id':self.player_id, 'game_id':self.game_id,
            'create_dt':self.create_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'alivetime':self.alivetime, 'rank':self.rank, 'score':self.score, 'team':self.team}

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
        return "<PlayerWeaponStat(%s, %s, %s)>" % (self.player_weapon_stats_id, self.player_id, self.game_id)

    def to_dict(self):
        return {
            'weapon_cd':self.weapon_cd,
            'player_weapon_stats_id':self.player_weapon_stats_id,
            'player_id':self.player_id,
            'game_id':self.game_id,
            'fired':self.fired,
            'max':self.max,
            'hit':self.hit,
            'actual':self.actual,
            'frags':self.frags,
        }


class TeamGameStat(object):
    def __init__(self, team_game_stat_id=None, create_dt=None):
        self.team_game_stat_id = team_game_stat_id
        self.create_dt = create_dt

    def __repr__(self):
        return "<TeamGameStat(%s, %s, %s)>" % (self.team_game_stat_id, self.game_id, self.team)

    def to_dict(self):
        return {
            'team_game_stat_id':self.team_game_stat_id,
            'game_id':self.game_id,
            'team':self.team,
            'score':self.score,
            'rounds':self.rounds,
            'caps':self.caps,
            'create_dt':self.create_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }

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
    def __init__(self, player_id=None, game_id=None, key=None,
            value=None, create_dt=None):
        self.player_id                = player_id
        self.game_id                  = game_id
        self.key                      = key
        self.value                    = value
        self.create_dt                = create_dt

    def __repr__(self):
        return "<PlayerGameAnticheat(%s, %d)>" % (self.key, self.value)


class GameType(object):
    def __repr__(self):
        return "<GameType(%s, %s, %s)>" % (self.game_type_cd, self.descr, self.active_ind)

    def to_dict(self):
        return {'game_type_cd':self.game_type_cd, 'name':self.descr, 'active':self.active_ind}


class Weapon(object):
    def __repr__(self):
        return "<Weapon(%s, %s, %s)>" % (self.weapon_cd, self.descr, self.active_ind)

    def to_dict(self):
        return {'weapon_cd':self.weapon_cd, 'name':self.descr, 'active':self.active_ind}