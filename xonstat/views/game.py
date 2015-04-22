import datetime
import logging
import re
import time
from collections import OrderedDict
from pyramid.response import Response
from sqlalchemy import desc, func, over
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url
from xonstat.views.helpers import RecentGame, recent_games_q


log = logging.getLogger(__name__)


def _game_info_data(request):
    game_id = int(request.matchdict['id'])

    show_elo = False
    if request.params.has_key('show_elo'):
        show_elo = True

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

        # if at least one player has a valid latency, we'll show the column
        for pgstat in pgstats:
            if pgstat.avg_latency is not None:
                show_latency = True

        q = DBSession.query(TeamGameStat).\
                filter(TeamGameStat.game_id == game_id)
        if game.game_type_cd == 'ctf':
            q = q.order_by(TeamGameStat.caps.desc())
        elif game.game_type_cd == 'ca':
            q = q.order_by(TeamGameStat.rounds.desc())
        # dom -> ticks, rc -> laps, nb -> goals, as -> objectives

        q = q.order_by(TeamGameStat.score.desc())

        tgstats = q.all()

        stats_by_team = OrderedDict()
        for pgstat in pgstats:
            if pgstat.team not in stats_by_team.keys():
                stats_by_team[pgstat.team] = []
            stats_by_team[pgstat.team].append(pgstat)

        captimes = []
        if game.game_type_cd == 'ctf':
            for pgstat in pgstats:
                if pgstat.fastest is not None:
                    captimes.append(pgstat)
            captimes = sorted(captimes, key=lambda x:x.fastest)

        pwstats = {}
        for (pwstat, weapon) in DBSession.query(PlayerWeaponStat, Weapon).\
                filter(PlayerWeaponStat.game_id == game_id).\
                filter(PlayerWeaponStat.weapon_cd == Weapon.weapon_cd).\
                order_by(PlayerWeaponStat.actual.desc()).\
                all():
                    print pwstat
                    print pwstats
                    if pwstat.player_game_stat_id not in pwstats:
                        pwstats[pwstat.player_game_stat_id] = []

                    # NOTE adding pgstat to position 6 in order to display nick.
                    # You have to use a slice [0:5] to pass to the accuracy
                    # template
                    pwstats[pwstat.player_game_stat_id].append((weapon.descr,
                        weapon.weapon_cd, pwstat.actual, pwstat.max,
                        pwstat.hit, pwstat.fired, pwstat.frags))

    except Exception as inst:
        game = None
        server = None
        map = None
        gametype = None
        pgstats = None
        tgstats = None
        pwstats = None
        captimes = None
        show_elo = False
        show_latency = False
        stats_by_team = None
        raise inst

    return {'game':game,
            'server':server,
            'map':map,
            'gametype':gametype,
            'pgstats':pgstats,
            'tgstats':tgstats,
            'pwstats':pwstats,
            'captimes':captimes,
            'show_elo':show_elo,
            'show_latency':show_latency,
            'stats_by_team':stats_by_team,
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
    game_type_cd, start_game_id, end_game_id = None, None, None
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

    if request.params.has_key('start_game_id'):
        start_game_id = request.params['start_game_id']
        query['start_game_id'] = start_game_id

    if request.params.has_key('end_game_id'):
        end_game_id = request.params['end_game_id']
        query['end_game_id'] = end_game_id

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
            player_id=player_id, game_type_cd=game_type_cd,
            start_game_id=start_game_id, end_game_id=end_game_id)

    recent_games = [RecentGame(row) for row in rgs_q.limit(20).all()]
    
    if len(recent_games) > 0:
        query['start_game_id'] = recent_games[-1].game_id + 1

    # build the list of links for the stripe across the top
    game_type_links = []

    # clear out the game_id window
    gt_query = query.copy()
    if 'start_game_id' in gt_query:
        del gt_query['start_game_id']
    if 'end_game_id' in gt_query:
        del gt_query['end_game_id']

    for gt in ('overall','duel','ctf','dm','tdm','ca','kh','ft',
            'lms','as','dom','nb','cts','rc'):
        gt_query['type'] = gt
        url = request.route_url("game_index", _query=gt_query)
        game_type_links.append((gt, url))

    return {
            'recent_games':recent_games,
            'query':query,
            'game_type_cd':game_type_cd,
            'game_type_links':game_type_links,
           }

def game_finder(request):
    """
    Provide a list of recent games with an advanced filter.
    """
    return game_finder_data(request)
