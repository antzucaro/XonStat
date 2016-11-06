import logging
from collections import namedtuple
from datetime import datetime, timedelta

import sqlalchemy.sql.expression as expr
import sqlalchemy.sql.functions as func
from pyramid import httpexceptions
from webhelpers.paginate import Page
from xonstat.models import DBSession, Server, Map, Game, PlayerGameStat, Player, PlayerCaptime
from xonstat.models.map import MapCapTime
from xonstat.util import page_url, html_colors
from xonstat.views.helpers import RecentGame, recent_games_q

log = logging.getLogger(__name__)

def _map_index_data(request):
    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    try:
        map_q = DBSession.query(Map).\
                order_by(Map.map_id.desc())

        maps = Page(map_q, current_page, items_per_page=25, url=page_url)

    except Exception as e:
        maps = None

    return {'maps':maps, }


def map_index(request):
    """
    Provides a list of all the current maps.
    """
    return _map_index_data(request)


def map_index_json(request):
    """
    Provides a JSON-serialized list of all the current maps.
    """
    view_data = _map_index_data(request)

    maps = [m.to_dict() for m in view_data['maps']]

    return maps


def _map_info_data(request):
    map_id = int(request.matchdict['id'])

    try:
        leaderboard_lifetime = int(
                request.registry.settings['xonstat.leaderboard_lifetime'])
    except:
        leaderboard_lifetime = 30

    leaderboard_count = 10
    recent_games_count = 20

    # captime tuples
    Captime = namedtuple('Captime', ['player_id', 'nick_html_colors',
        'fastest_cap', 'game_id'])

    try:
        gmap = DBSession.query(Map).filter_by(map_id=map_id).one()

        # recent games played in descending order
        rgs = recent_games_q(map_id=map_id).limit(recent_games_count).all()
        recent_games = [RecentGame(row) for row in rgs]

        # top players by score
        top_scorers = DBSession.query(Player.player_id, Player.nick,
                func.sum(PlayerGameStat.score)).\
                filter(Player.player_id == PlayerGameStat.player_id).\
                filter(Game.game_id == PlayerGameStat.game_id).\
                filter(Game.map_id == map_id).\
                filter(Player.player_id > 2).\
                filter(PlayerGameStat.create_dt >
                        (datetime.utcnow() - timedelta(days=leaderboard_lifetime))).\
                order_by(expr.desc(func.sum(PlayerGameStat.score))).\
                group_by(Player.nick).\
                group_by(Player.player_id).all()[0:leaderboard_count]

        top_scorers = [(player_id, html_colors(nick), score) \
                for (player_id, nick, score) in top_scorers]

        # top players by playing time
        top_players = DBSession.query(Player.player_id, Player.nick,
                func.sum(PlayerGameStat.alivetime)).\
                filter(Player.player_id == PlayerGameStat.player_id).\
                filter(Game.game_id == PlayerGameStat.game_id).\
                filter(Game.map_id == map_id).\
                filter(Player.player_id > 2).\
                filter(PlayerGameStat.create_dt >
                        (datetime.utcnow() - timedelta(days=leaderboard_lifetime))).\
                order_by(expr.desc(func.sum(PlayerGameStat.alivetime))).\
                group_by(Player.nick).\
                group_by(Player.player_id).all()[0:leaderboard_count]

        top_players = [(player_id, html_colors(nick), score) \
                for (player_id, nick, score) in top_players]

        # top servers using/playing this map
        top_servers = DBSession.query(Server.server_id, Server.name,
                func.count(Game.game_id)).\
                filter(Game.server_id == Server.server_id).\
                filter(Game.map_id == map_id).\
                filter(Game.create_dt >
                        (datetime.utcnow() - timedelta(days=leaderboard_lifetime))).\
                order_by(expr.desc(func.count(Game.game_id))).\
                group_by(Server.name).\
                group_by(Server.server_id).all()[0:leaderboard_count]

        # TODO make this a configuration parameter to be set in the settings
        # top captimes
        captimes_raw = DBSession.query(Player.player_id, Player.nick,
            PlayerCaptime.fastest_cap, PlayerCaptime.game_id).\
                filter(PlayerCaptime.map_id == map_id).\
                filter(Player.player_id == PlayerCaptime.player_id).\
                order_by(PlayerCaptime.fastest_cap).\
                limit(10).\
                all()

        captimes = [Captime(c.player_id, html_colors(c.nick),
            c.fastest_cap, c.game_id) for c in captimes_raw]

    except Exception as e:
        gmap = None
    return {'gmap':gmap,
            'recent_games':recent_games,
            'top_scorers':top_scorers,
            'top_players':top_players,
            'top_servers':top_servers,
            'captimes':captimes,
            }


def map_info(request):
    """
    List the information stored about a given map.
    """
    mapinfo_data =  _map_info_data(request)

    # FIXME: code clone, should get these from _map_info_data
    leaderboard_count = 10
    recent_games_count = 20

    for i in range(leaderboard_count-len(mapinfo_data['top_scorers'])):
        mapinfo_data['top_scorers'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(mapinfo_data['top_players'])):
        mapinfo_data['top_players'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(mapinfo_data['top_servers'])):
        mapinfo_data['top_servers'].append(('-', '-', '-'))

    return mapinfo_data


def map_info_json(request):
    """
    List the information stored about a given map. JSON.
    """
    return [{'status':'not implemented'}]


def map_captimes_data(request):
    map_id = int(request.matchdict['id'])

    current_page = request.params.get('page', 1)

    try:
        mmap = DBSession.query(Map).filter_by(map_id=map_id).one()

        mct_q = DBSession.query(PlayerCaptime.fastest_cap, PlayerCaptime.create_dt,
                PlayerCaptime.player_id, PlayerCaptime.game_id,
                Game.server_id, Server.name.label('server_name'),
                PlayerGameStat.nick.label('player_nick')).\
                filter(PlayerCaptime.map_id==map_id).\
                filter(PlayerCaptime.game_id==Game.game_id).\
                filter(PlayerCaptime.map_id==Map.map_id).\
                filter(Game.server_id==Server.server_id).\
                filter(PlayerCaptime.player_id==PlayerGameStat.player_id).\
                filter(PlayerCaptime.game_id==PlayerGameStat.game_id).\
                order_by(expr.asc(PlayerCaptime.fastest_cap))

    except Exception as e:
        raise httpexceptions.HTTPNotFound

    map_captimes = Page(mct_q, current_page, items_per_page=20, url=page_url)

    map_captimes.items = [MapCapTime(row) for row in map_captimes.items]

    return {
            'map_id':map_id,
            'map':mmap,
            'captimes':map_captimes,
        }

def map_captimes(request):
    return map_captimes_data(request)

def map_captimes_json(request):
    current_page = request.params.get('page', 1)
    data = map_captimes_data(request)

    return {
            "map": data["map"].to_dict(),
            "captimes": [e.to_dict() for e in data["captimes"].items],
            "page": current_page,
            }
