import datetime
import logging
import re
import time
from pyramid.response import Response
from sqlalchemy import desc, func, over
from collections import namedtuple
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url
from xonstat.views.helpers import RecentGame, recent_games_q

import random

log = logging.getLogger(__name__)


# DEPRECATED
def _game_index_data(request):
    game_type_cd = None
    game_type_descr = None

    if request.params.has_key('game_type_cd'):
        game_type_cd = request.params['game_type_cd']
        try:
            game_type_descr = DBSession.query(GameType.descr).\
                filter(GameType.game_type_cd == game_type_cd).\
                one()[0]
        except Exception as e:
            game_type_cd = None

    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    try:
        rgs_q = recent_games_q(game_type_cd=game_type_cd)

        games = Page(rgs_q, current_page, items_per_page=10, url=page_url)

        # replace the items in the canned pagination class with more rich ones
        games.items = [RecentGame(row) for row in games.items]

        pgstats = {}
        for game in games.items:
            pgstats[game.game_id] = DBSession.query(PlayerGameStat).\
                    filter(PlayerGameStat.game_id == game.game_id).\
                    order_by(PlayerGameStat.scoreboardpos).\
                    order_by(PlayerGameStat.score).all()

    except Exception as e:
        games           = None
        pgstats         = None
        game_type_cd    = None
        game_type_descr = None

    return {'games':games,
            'pgstats':pgstats,
            'game_type_cd':game_type_cd,
            'game_type_descr':game_type_descr,
            }


def game_index(request):
    """
    Provides a list of current games, with the associated game stats.
    These games are ordered by game_id, with the most current ones first.
    Paginated.
    """
    return _game_index_data(request)


def game_index_json(request):
    """
    Provides a list of current games, with the associated game stats.
    These games are ordered by game_id, with the most current ones first.
    Paginated. JSON.
    """
    return [{'status':'not implemented'}]


def _game_info_data(request):
    game_id = request.matchdict['id']

    if request.params.has_key('show_elo'):
        show_elo = True
    else:
        show_elo = False

    if request.params.has_key('show_latency'):
        show_latency = True
    else:
        show_latency = False

    try:
        notfound = False

        (game, server, map, gametype) = DBSession.query(Game, Server, Map, GameType).\
                filter(Game.game_id == game_id).\
                filter(Game.server_id == Server.server_id).\
                filter(Game.map_id == Map.map_id).\
                filter(Game.game_type_cd == GameType.game_type_cd).one()

        pgstats = DBSession.query(PlayerGameStat).\
                filter(PlayerGameStat.game_id == game_id).\
                order_by(PlayerGameStat.scoreboardpos).\
                order_by(PlayerGameStat.score).\
                all()

        captimes = []
        if game.game_type_cd == 'ctf':
            for pgstat in pgstats:
                if pgstat.fastest is not None:
                    captimes.append(pgstat)

            captimes = sorted(captimes, key=lambda x:x.fastest)

        teamscores = {}
        for pgstat in pgstats:
            if pgstat.team in [5,14,13,10]:
                team = pgstat.team_html_color()
                if pgstat.teamscore is not None:
                    if not teamscores.has_key(team):
                        teamscores[team] = pgstat.teamscore
                    else:
                        if teamscores[team] != pgstat.teamscore:  # this should not happen!
                            teamscores[team] = None
        if len(teamscores) == 0:
            teamscores = None
            
        ### RANDOM SCORES FOR TESTING
        teams = ["red","blue","yellow","pink"]
        random.shuffle(teams)
        teamscores = {}
        for k in range(random.randint(2,4)):
            team = teams[k-1]
            teamscores[team] = random.randint(-5,150)
        ### END
        
        #TeamInfo = namedtuple('TeamInfo', ['team','scoreboardpos','playercount','teamscore'])
        #
        #teams = {}
        #last_pgs = pgstats[0]
        #for pgstat in pgstats:
        #    if pgstat.team != last_pgs.team:
        #        teams[last_pgs.scoreboardpos] = TeamInfo(
        #                team=last_pgs.team,
        #                scoreboardpos=last_pgs.scoreboardpos,
        #                playercount=pgstat.scoreboardpos-last_pgs.scoreboardpos,
        #                teamscore=last_pgs.teamscore)
        #        last_pgs = pgstat
        #teams[last_pgs.scoreboardpos] = TeamInfo(
        #        team=last_pgs.team,
        #        scoreboardpos=last_pgs.scoreboardpos,
        #        playercount=pgstat.scoreboardpos-last_pgs.scoreboardpos,
        #        teamscore=last_pgs.teamscore)
        #print teams

        pwstats = {}
        for (pwstat, pgstat, weapon) in DBSession.query(PlayerWeaponStat, PlayerGameStat, Weapon).\
                filter(PlayerWeaponStat.game_id == game_id).\
                filter(PlayerWeaponStat.weapon_cd == Weapon.weapon_cd).\
                filter(PlayerWeaponStat.player_game_stat_id == \
                    PlayerGameStat.player_game_stat_id).\
                order_by(PlayerGameStat.scoreboardpos).\
                order_by(PlayerGameStat.score).\
                order_by(Weapon.descr).\
                all():
                    if pgstat.player_game_stat_id not in pwstats:
                        pwstats[pgstat.player_game_stat_id] = []

                    # NOTE adding pgstat to position 6 in order to display nick.
                    # You have to use a slice [0:5] to pass to the accuracy
                    # template
                    pwstats[pgstat.player_game_stat_id].append((weapon.descr,
                        weapon.weapon_cd, pwstat.actual, pwstat.max,
                        pwstat.hit, pwstat.fired, pgstat))

    except Exception as inst:
        game = None
        server = None
        map = None
        gametype = None
        pgstats = None
        pwstats = None
        captimes = None
        teams = None
        show_elo = False
        show_latency = False
        raise inst

    return {'game':game,
            'server':server,
            'map':map,
            'gametype':gametype,
            'pgstats':pgstats,
            'pwstats':pwstats,
            'captimes':captimes,
            'teams':teams,
            'teamscores':teamscores,
            'show_elo':show_elo,
            'show_latency':show_latency,
            }


def game_info(request):
    """
    List the game stats (scoreboard) for a particular game. Paginated.
    """
    return _game_info_data(request)


def game_info_json(request):
    """
    List the game stats (scoreboard) for a particular game. Paginated. JSON.
    """
    return [{'status':'not implemented'}]


def _rank_index_data(request):
    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    game_type_cd = request.matchdict['game_type_cd']

    ranks_q = DBSession.query(PlayerRank).\
            filter(PlayerRank.game_type_cd==game_type_cd).\
            order_by(PlayerRank.rank)

    ranks = Page(ranks_q, current_page, url=page_url)

    if len(ranks) == 0:
        ranks = None

    return {
            'ranks':ranks,
            'game_type_cd':game_type_cd,
           }


def rank_index(request):
    """
    Provide a list of gametype ranks, paginated.
    """
    return _rank_index_data(request)


def rank_index_json(request):
    """
    Provide a list of gametype ranks, paginated. JSON.
    """
    return [{'status':'not implemented'}]


def game_finder_data(request):
    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    query = {}

    server_id, map_id, player_id = None, None, None
    range_start, range_end, game_type_cd = None, None, None
    game_type_descr = None

    # these become WHERE clauses when present
    if request.params.has_key('server_id'):
        server_id = request.params['server_id']
        query['server_id'] = server_id

    if request.params.has_key('map_id'):
        map_id = request.params['map_id']
        query['map_id'] = map_id

    if request.params.has_key('player_id'):
        player_id = request.params['player_id']
        query['player_id'] = player_id

    if request.params.has_key('range_start'):
        range_start = request.params['range_start']
        query['range_start'] = range_start

    if request.params.has_key('range_end'):
        range_end = request.params['range_end']
        query['range_end'] = range_end

    if request.params.has_key('type'):
        game_type_cd = request.params['type']
        query['type'] = game_type_cd
        try:
            game_type_descr = DBSession.query(GameType.descr).\
                filter(GameType.game_type_cd == game_type_cd).\
                one()[0]
        except Exception as e:
            game_type_cd = None

    rgs_q = recent_games_q(server_id=server_id, map_id=map_id,
            player_id=player_id, game_type_cd=game_type_cd)

    recent_games = Page(rgs_q, current_page, url=page_url)

    recent_games.items = [RecentGame(row) for row in recent_games.items]

    return {
            'recent_games':recent_games,
            'query':query,
            'game_type_cd':game_type_cd,
           }

def game_finder(request):
    """
    Provide a list of recent games with an advanced filter.
    """
    return game_finder_data(request)
