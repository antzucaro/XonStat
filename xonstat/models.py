import datetime
import logging
import sqlahelper
import sqlalchemy
import transaction

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import mapper
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

Engine=sqlahelper.get_engine()
DBSession = scoped_session(sessionmaker())
Base = declarative_base()

# setup logging
log = logging.getLogger(__name__)

# reflect all the tables 
MetaData = sqlalchemy.MetaData(bind=Engine, reflect=True)

# assign all those tables to an object
achievements_table = MetaData.tables['achievements']
cd_achievement_table = MetaData.tables['cd_achievement']
cd_game_type_table = MetaData.tables['cd_game_type']
cd_mutator_table = MetaData.tables['cd_mutator']
cd_weapon_table = MetaData.tables['cd_weapon']
db_version_table = MetaData.tables['db_version']
game_mutators_table = MetaData.tables['game_mutators']
games_table = MetaData.tables['games']
hashkeys_table = MetaData.tables['hashkeys']
map_game_types_table = MetaData.tables['map_game_types']
maps_table = MetaData.tables['maps']
player_game_stats_table = MetaData.tables['player_game_stats']
players_table = MetaData.tables['players']
player_weapon_stats_table = MetaData.tables['player_weapon_stats']
servers_table = MetaData.tables['servers']

# define objects for all tables
class Player(object):
    def __init__(self, player_id=None, nick=None, create_dt=datetime.datetime.now(), 
            location = None):
        self.player_id = player_id
        self.nick = nick
        self.create_dt = create_dt
        self.location = location

    def __repr__(self):
        return "<Player(%s, %s, %s, %s)>" % (self.player_id, self.nick, 
                self.create_dt, self.location)

class Mutator(object):
    def __init__(self, mutator_cd, name=None, descr=None, active_ind='Y'):
        self.mutator_cd = mutator_cd
        self.name = name
        self.descr = descr
        self.active_ind = active_ind

    def __repr__(self):
        return "<Mutator(%s, %s, %s, %s)>" % (self.mutator_cd, self.name, 
                self.descr, self.active_ind)

class GameType(object):
    def __init__(self, game_type_cd, descr=None, active_ind='Y'):
        self.game_type_cd = game_type_cd
        self.descr = descr
        self.active_ind = active_ind

    def __repr__(self):
        return "<GameType(%s, %s, %s)>" % (self.game_type_cd, self.descr, 
                self.active_ind)

class Weapon(object):
    def __init__(self, weapon_cd=None, descr=None, active_ind='Y'):
        self.weapon_cd = weapon_cd
        self.descr = descr
        self.active_ind = active_ind

    def __repr__(self):
        return "<Weapon(%s, %s, %s)>" % (self.weapon_cd, self.descr, 
                self.active_ind)

class Server(object):
    def __init__(self, server_id=None, name=None, location=None, ip_addr=None,
            max_players=None, create_dt=datetime.datetime.now(), 
            pure_ind='Y', active_ind='Y'):
        self.server_id = server_id
        self.name = name
        self.location = location
        self.ip_addr = ip_addr
        self.max_players = max_players
        self.create_dt = create_dt
        self.pure_ind = pure_ind
        self.active_ind = active_ind

    def __repr__(self):
        return "<Server(%s, %s, %s)>" % (self.server_id, self.name, 
                self.ip_addr)

class Map(object):
    def __init__(self, map_id=None, name=None, version=None, pk3_name=None,
            curl_url=None):
        self.map_id = map_id
        self.name = name
        self.version = version
        self.pk3_name = pk3_name
        self.curl_url = curl_url

    def __repr__(self):
        return "<Map(%s, %s, %s)>" % (self.map_id, self.name, self.version)

class MapGameType(object):
    def __init__(self, map_id=None, game_type_cd=None):
        self.map_id = map_id
        self.game_type_cd = game_type_cd

    def __repr__(self):
        return "<MapGameType(%s, %s)>" % (self.map_id, self.game_type_cd)

class Game(object):
    def __init__(self, game_id=None, start_dt=datetime.datetime.now(),
            game_type_cd=None, server_id=None, map_id=None, duration=None,
            winner=None, create_dt=datetime.datetime.now()):
        self.game_id = game_id
        self.start_dt = start_dt
        self.game_type_cd = game_type_cd
        self.server_id = server_id
        self.map_id = map_id
        self.duration = duration
        self.winner = winner
        self.create_dt = create_dt

    def __repr__(self):
        return "<Game(%s, %s, %s, %s)>" % (self.game_id, self.start_dt, 
                self.game_type_cd, self.server_id)

class PlayerGameStat(object):
    def __init__(self, player_id=None, game_id=None, create_dt=None, 
            stat_type=None, team=None, kills=None, deaths=None, suicides=None, 
            score=None, time=None, held=None, captures=None, pickups=None, 
            carrier_frags=None, drops=None, returns=None, collects=None, 
            destroys=None, destroys_holding_key=None, pushes=None, 
            pushed=None, nick=None):
        self.player_id = player_id
        self.game_id = game_id
        self.create_dt = create_dt
        self.stat_type = stat_type
        self.nick = nick
        self.team = team
        self.kills = kills
        self.deaths = deaths
        self.suicides = suicides
        self.score = score
        self.time = time
        self.held = held
        self.captures = captures
        self.pickups = pickups
        self.carrier_frags = carrier_frags
        self.drops = drops
        self.returns = returns
        self.collects = collects
        self.destroys = destroys
        self.destroys_holding_key = destroys_holding_key
        self.pushes = pushes
        self.pushed = pushed

    def __repr__(self):
        return "<PlayerGameStat(%s, %s, %s, %s)>" \
        % (self.player_id, self.game_id, self.create_dt, self.stat_type)

class GameMutator(object):
    def __init__(self, game_id=None, mutator_cd=None):
        self.game_id = game_id
        self.mutator_cd = mutator_cd

    def __repr__(self):
        return "<GameMutator(%s, %s)>" % (self.game_id, self.mutator_cd)

class Achievement(object):
    def __init__(self, achievement_cd=None, descr=None, limit=None, active_ind='Y'):
        self.achievement_cd = achievement_cd
        self.descr = descr
        self.limit = limit
        self.active_ind = active_ind

    def __repr__(self):
        return "<Achievement(%s, %s, %s)>" % (self.achievement_cd, self.descr, self.limit)

class PlayerAchievement(object):
    def __init__(self, achievement_id=None, achievement_cd=None, 
            player_id=None, create_dt=datetime.datetime.now()):
        self.achievement_id = achievement_id
        self.achievement_cd = achievement_cd
        self.player_id = player_id
        self.create_dt = create_dt

    def __repr__(self):
        return "<PlayerAchievement(%s, %s)>" % (self.player_id, self.achievement_cd)

class PlayerWeaponStat(object):
    def __init__(self, player_weapon_stat_id=None, 
            create_dt=datetime.datetime.now(), player_id=None,
            game_id=None, weapon_cd=None, actual=None, max=None, frags=None):
        self.player_weapon_stat_id = player_weapon_stat_id
        self.create_dt = create_dt
        self.player_id = player_id
        self.game_id = game_id
        self.weapon_cd = weapon_cd
        self.actual = actual
        self.max = max
        self.frags = frags

    def __repr__(self):
        return "<PlayerWeaponStat(%s, %s, %s)>" % (self.player_weapon_stat_id,
                self.player_id, self.game_id)

class Hashkey(object):
    def __init__(self, player_id=None, hashkey=None, active_ind='Y',
            create_dt=datetime.datetime.now()):
        self.player_id = player_id
        self.hashkey = hashkey
        self.active_ind = active_ind

    def __repr__(self):
        return "<Hashkey(%s, %s)>" % (self.player_id, self.hashkey)

# now map the tables and the objects together
mapper(PlayerAchievement, achievements_table)
mapper(Achievement, cd_achievement_table)
mapper(GameType, cd_game_type_table)
mapper(Mutator, cd_mutator_table)
mapper(Weapon, cd_weapon_table)
mapper(GameMutator, game_mutators_table)
mapper(Game, games_table)
mapper(Hashkey, hashkeys_table)
mapper(MapGameType, map_game_types_table)
mapper(Map, maps_table)
mapper(PlayerGameStat, player_game_stats_table)
mapper(Player, players_table)
mapper(PlayerWeaponStat, player_weapon_stats_table)
mapper(Server, servers_table)

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

