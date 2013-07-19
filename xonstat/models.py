import json
import logging
import math
import sqlalchemy
import sqlalchemy.sql.functions as sfunc
from calendar import timegm
from datetime import datetime as dt
from datetime import timedelta
from sqlalchemy.orm import mapper
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from xonstat.util import qfont_decode, strip_colors, html_colors, pretty_date

log = logging.getLogger(__name__)

DBSession = scoped_session(sessionmaker())
Base = declarative_base()

# define objects for all tables
class Player(object):
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
        return "<Player(%s, %s)>" % (self.player_id, self.nick.encode('utf-8'))

    def to_dict(self):
        return {'player_id':self.player_id, 'nick':self.nick,
            'joined':self.create_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'active_ind':self.active_ind, 'location':self.location,
            'stripped_nick':qfont_decode(self.stripped_nick)}

    def epoch(self):
        return timegm(self.create_dt.timetuple())


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


class Server(object):
    def __init__(self, name=None, hashkey=None, ip_addr=None):
        self.name = name
        self.hashkey = hashkey
        self.ip_addr = ip_addr
        self.create_dt = dt.utcnow()

    def __repr__(self):
        return "<Server(%s, %s)>" % (self.server_id, self.name.encode('utf-8'))

    def to_dict(self):
        return {'server_id':self.server_id, 'name':self.name,
            'ip_addr':self.ip_addr, 'location':self.location}

    def fuzzy_date(self):
        return pretty_date(self.create_dt)

    def epoch(self):
        return timegm(self.create_dt.timetuple())


class Map(object):
    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return "<Map(%s, %s, %s)>" % (self.map_id, self.name, self.version)

    def to_dict(self):
        return {'map_id':self.map_id, 'name':self.name, 'version':self.version,}

    def fuzzy_date(self):
        return pretty_date(self.create_dt)

    def epoch(self):
        return timegm(self.create_dt.timetuple())


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


class Achievement(object):
    def __repr__(self):
        return "<Achievement(%s, %s, %s)>" % (self.achievement_cd, self.descr, self.limit)

    def to_dict(self):
        return {'achievement_cd':self.achievement_cd, 'name':self.descr, 'limit':self.limit}


class PlayerAchievement(object):
    def __repr__(self):
        return "<PlayerAchievement(%s, %s)>" % (self.player_id, self.achievement_cd)

    def to_dict(self):
        return {'player_id':self.player_id, 'achievement_cd':self.achievement_cd}


class PlayerWeaponStat(object):
    def __init__(self):
        self.fired = 0
        self.max = 0
        self.hit = 0
        self.actual = 0
        self.frags = 0

    def __repr__(self):
        return "<PlayerWeaponStat(%s, %s, %s)>" % (self.player_weapon_stats_id, self.player_id, self.game_id)

    def to_dict(self):
        return {'player_weapon_stats_id':self.player_weapon_stats_id, 'player_id':self.player_id, 'game_id':self.game_id}


class Hashkey(object):
    def __init__(self, player_id=None, hashkey=None):
        self.player_id = player_id
        self.hashkey = hashkey

    def __repr__(self):
        return "<Hashkey(%s, %s)>" % (self.player_id, self.hashkey)

    def to_dict(self):
        return {'player_id':self.player_id, 'hashkey':self.hashkey}


class PlayerNick(object):
    def __repr__(self):
        return "<PlayerNick(%s, %s)>" % (self.player_id, qfont_decode(self.stripped_nick))

    def to_dict(self):
        return {'player_id':self.player_id, 'name':qfont_decode(self.stripped_nick)}


class PlayerElo(object):
    def __init__(self, player_id=None, game_type_cd=None, elo=None):

        self.player_id = player_id
        self.game_type_cd = game_type_cd
        self.elo = elo
        self.score = 0
        self.games = 0

    def __repr__(self):
        return "<PlayerElo(pid=%s, gametype=%s, elo=%s, games=%s)>" % (self.player_id, self.game_type_cd, self.elo, self.games)

    def to_dict(self):
        return {'player_id':self.player_id, 'game_type_cd':self.game_type_cd, 'elo':self.elo, 'games':self.games}


class PlayerRank(object):

    def nick_html_colors(self, limit=None):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return html_colors(self.nick, limit)

    def __repr__(self):
        return "<PlayerRank(pid=%s, gametype=%s, rank=%s)>" % (self.player_id, self.game_type_cd, self.rank)

    def to_dict(self):
        return {'player_id':self.player_id, 'game_type_cd':self.game_type_cd, 'rank':self.rank}


class PlayerCaptime(object):
    def __init__(self, player_id=None, game_id=None, map_id=None,
            fastest_cap=None):
        self.player_id = player_id
        self.game_id = game_id
        self.map_id = map_id
        self.fastest_cap = fastest_cap

    def __repr__(self):
        return "<PlayerCaptime(pid=%s, map_id=%s)>" % (self.player_id, self.map_id)


class SummaryStat(object):
    def __repr__(self):
        return "<SummaryStat(total_players=%s, total_games=%s, total_servers=%s)>" % (self.total_players, self.total_games, self.total_servers)


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


def initialize_db(engine=None):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    MetaData = sqlalchemy.MetaData(bind=engine, reflect=True)

    # assign all those tables to an object
    achievements_table = MetaData.tables['achievements']
    cd_achievement_table = MetaData.tables['cd_achievement']
    cd_game_type_table = MetaData.tables['cd_game_type']
    cd_weapon_table = MetaData.tables['cd_weapon']
    db_version_table = MetaData.tables['db_version']
    games_table = MetaData.tables['games']
    hashkeys_table = MetaData.tables['hashkeys']
    maps_table = MetaData.tables['maps']
    player_game_stats_table = MetaData.tables['player_game_stats']
    players_table = MetaData.tables['players']
    player_weapon_stats_table = MetaData.tables['player_weapon_stats']
    servers_table = MetaData.tables['servers']
    player_nicks_table = MetaData.tables['player_nicks']
    player_elos_table = MetaData.tables['player_elos']
    player_ranks_table = MetaData.tables['player_ranks']
    player_captimes_table = MetaData.tables['player_map_captimes']
    summary_stats_table = MetaData.tables['summary_stats']
    team_game_stats_table = MetaData.tables['team_game_stats']

    # now map the tables and the objects together
    mapper(PlayerAchievement, achievements_table)
    mapper(Achievement, cd_achievement_table)
    mapper(GameType, cd_game_type_table)
    mapper(Weapon, cd_weapon_table)
    mapper(Game, games_table)
    mapper(Hashkey, hashkeys_table)
    mapper(Map, maps_table)
    mapper(PlayerGameStat, player_game_stats_table)
    mapper(Player, players_table)
    mapper(PlayerWeaponStat, player_weapon_stats_table)
    mapper(Server, servers_table)
    mapper(PlayerNick, player_nicks_table)
    mapper(PlayerElo, player_elos_table)
    mapper(PlayerRank, player_ranks_table)
    mapper(PlayerCaptime, player_captimes_table)
    mapper(SummaryStat, summary_stats_table)
    mapper(TeamGameStat, team_game_stats_table)
