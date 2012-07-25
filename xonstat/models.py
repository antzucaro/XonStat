import json
import logging
import math
import sqlalchemy
import sqlalchemy.sql.functions as sfunc
from datetime import timedelta
from sqlalchemy.orm import mapper
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from xonstat.elo import ELOPARMS, KREDUCTION
from xonstat.util import strip_colors, html_colors, pretty_date

log = logging.getLogger(__name__)

DBSession = scoped_session(sessionmaker())
Base = declarative_base()

# define objects for all tables
class Player(object):
    def nick_html_colors(self):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return html_colors(self.nick)

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
        return {'player_id':self.player_id, 'name':self.nick.encode('utf-8')}


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

    def __repr__(self):
        return "<Server(%s, %s)>" % (self.server_id, self.name.encode('utf-8'))

    def to_dict(self):
        return {'server_id':self.server_id, 'name':self.name.encode('utf-8')}


class Map(object):
    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return "<Map(%s, %s, %s)>" % (self.map_id, self.name, self.version)

    def to_dict(self):
        return {'map_id':self.map_id, 'name':self.name, 'version':self.version}


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
        return {'game_id':self.game_id, 'start':self.start_dt.strftime('%Y-%m-%dT%H:%M:%SZ'), 'game_type_cd':self.game_type_cd, 'server_id':self.server_id}

    def fuzzy_date(self):
        return pretty_date(self.start_dt)

    def process_elos(self, session, game_type_cd=None):
        if game_type_cd is None:
            game_type_cd = self.game_type_cd

        # we do not have the actual duration of the game, so use the 
        # maximum alivetime of the players instead
        duration = 0
        for d in session.query(sfunc.max(PlayerGameStat.alivetime)).\
                    filter(PlayerGameStat.game_id==self.game_id).\
                    one():
            duration = d.seconds

        scores = {}
        alivetimes = {}
        winners = []
        losers = []
        for (p,s,a,r,t) in session.query(PlayerGameStat.player_id, 
                PlayerGameStat.score, PlayerGameStat.alivetime,
                PlayerGameStat.rank, PlayerGameStat.team).\
                filter(PlayerGameStat.game_id==self.game_id).\
                filter(PlayerGameStat.alivetime > timedelta(seconds=0)).\
                filter(PlayerGameStat.player_id > 2).\
                all():
                    # scores are per second
                    scores[p] = s/float(a.seconds)
                    alivetimes[p] = a.seconds

                    # winners are either rank 1 or on the winning team
                    # team games are where the team is set (duh)
                    if r == 1 or (t == self.winner and t is not None):
                        winners.append(p)
                    else:
                        losers.append(p)

        player_ids = scores.keys()

        elos = {}
        for e in session.query(PlayerElo).\
                filter(PlayerElo.player_id.in_(player_ids)).\
                filter(PlayerElo.game_type_cd==game_type_cd).all():
                    elos[e.player_id] = e

        # ensure that all player_ids have an elo record
        for pid in player_ids:
            if pid not in elos.keys():
                elos[pid] = PlayerElo(pid, game_type_cd)

        for pid in player_ids:
            elos[pid].k = KREDUCTION.eval(elos[pid].games, alivetimes[pid],
                    duration)
            if elos[pid].k == 0:
                del(elos[pid])
                del(scores[pid])
                del(alivetimes[pid])

                if pid in winners:
                    winners.remove(pid)
                else:
                    losers.remove(pid)

        elos = self.update_elos(session, elos, scores, winners, losers, ELOPARMS)

        # add the elos to the session for committing
        for e in elos:
            session.add(elos[e])

    def update_elos(self, session, elos, scores, winners, losers, ep):
        if len(elos) < 2 or len(winners) == 0 or len(losers) == 0:
            return elos

        pids = elos.keys()

        elo_deltas = {}
        for w_pid in winners:
            w_elo = elos[w_pid]
            for l_pid in losers:
                l_elo = elos[l_pid]

                w_q = math.pow(10, float(w_elo.elo)/400.0)
                l_q = math.pow(10, float(l_elo.elo)/400.0)

                w_delta = w_elo.k * ELOPARMS.global_K * (1 - w_q/(w_q + l_q))
                l_delta = l_elo.k * ELOPARMS.global_K * (0 - l_q/(l_q + w_q))

                elo_deltas[w_pid] = (elo_deltas.get(w_pid, 0.0) + w_delta)
                elo_deltas[l_pid] = (elo_deltas.get(l_pid, 0.0) + l_delta)

                log.debug("Winner {0}'s elo_delta vs Loser {1}: {2}".format(w_pid,
                    l_pid, w_delta))

                log.debug("Loser {0}'s elo_delta vs Winner {1}: {2}".format(l_pid,
                    w_pid, l_delta))

                log.debug("w_elo: {0}, w_k: {1}, w_q: {2}, l_elo: {3}, l_k: {4}, l_q: {5}".\
                        format(w_elo.elo, w_elo.k, l_q, l_elo.elo, l_elo.k, l_q))

        for pid in pids:
            # average the elo gain for team games
            if pid in winners:
                elo_deltas[pid] = elo_deltas.get(pid, 0.0) / len(losers)
            else:
                elo_deltas[pid] = elo_deltas.get(pid, 0.0) / len(winners)

            old_elo = float(elos[pid].elo)
            new_elo = max(float(elos[pid].elo) + elo_deltas[pid], ep.floor)

            # in case we've set a different delta from the above
            elo_deltas[pid] = new_elo - old_elo

            elos[pid].elo = new_elo
            elos[pid].games += 1
            log.debug("Setting Player {0}'s Elo delta to {1}. Elo is now {2} (was {3}).".\
                    format(pid, elo_deltas[pid], new_elo, old_elo))

        self.save_elo_deltas(session, elo_deltas)

        return elos


    def save_elo_deltas(self, session, elo_deltas):
        """
        Saves the amount by which each player's Elo goes up or down
        in a given game in the PlayerGameStat row, allowing for scoreboard display.

        elo_deltas is a dictionary such that elo_deltas[player_id] is the elo_delta
        for that player_id.
        """
        pgstats = {}
        for pgstat in session.query(PlayerGameStat).\
                filter(PlayerGameStat.game_id == self.game_id).\
                all():
                    pgstats[pgstat.player_id] = pgstat

        for pid in elo_deltas.keys():
            try:
                pgstats[pid].elo_delta = elo_deltas[pid]
                session.add(pgstats[pid])
            except:
                log.debug("Unable to save Elo delta value for player_id {0}".format(pid))




class PlayerGameStat(object):
    def __init__(self, player_game_stat_id=None, create_dt=None):
        self.player_game_stat_id = player_game_stat_id
        self.create_dt = create_dt

    def __repr__(self):
        return "<PlayerGameStat(%s, %s, %s)>" % (self.player_id, self.game_id, self.create_dt)

    def to_dict(self):
        return {'player_id':self.player_id, 'game_id':self.game_id, 'create_dt':self.create_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}

    def nick_stripped(self):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return strip_colors(self.nick)

    def nick_html_colors(self):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return html_colors(self.nick)

    def team_html_color(self):
        # blue
        if self.team == 5:
            return "red"
        # red
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
        return "<PlayerNick(%s, %s)>" % (self.player_id, self.stripped_nick)

    def to_dict(self):
        return {'player_id':self.player_id, 'name':self.stripped_nick}


class PlayerElo(object):
    def __init__(self, player_id=None, game_type_cd=None):

        self.player_id = player_id
        self.game_type_cd = game_type_cd
        self.score = 0
        self.games = 0
        self.elo = ELOPARMS.initial

    def __repr__(self):
        return "<PlayerElo(pid=%s, gametype=%s, elo=%s)>" % (self.player_id, self.game_type_cd, self.elo)

    def to_dict(self):
        return {'player_id':self.player_id, 'game_type_cd':self.game_type_cd, 'elo':self.elo}


class PlayerRank(object):

    def nick_html_colors(self):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return html_colors(self.nick)

    def __repr__(self):
        return "<PlayerRank(pid=%s, gametype=%s, rank=%s)>" % (self.player_id, self.game_type_cd, self.rank)

    def to_dict(self):
        return {'player_id':self.player_id, 'game_type_cd':self.game_type_cd, 'rank':self.rank}


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
