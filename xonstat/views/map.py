import logging
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
from datetime import datetime, timedelta
from pyramid.response import Response
from sqlalchemy import desc
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url

log = logging.getLogger(__name__)

def _map_index_data(request):
    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    try:
        map_q = DBSession.query(Map).\
                order_by(Map.map_id.desc())

        maps = Page(map_q, current_page, items_per_page=10, url=page_url)

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
    map_id = request.matchdict['id']

    try: 
        leaderboard_lifetime = int(
                request.registry.settings['xonstat.leaderboard_lifetime'])
    except:
        leaderboard_lifetime = 30

    leaderboard_count = 10
    recent_games_count = 20

    try:
        gmap = DBSession.query(Map).filter_by(map_id=map_id).one()

        # recent games on this map
        recent_games = DBSession.query(Game, Server, Map, PlayerGameStat).\
            filter(Game.server_id==Server.server_id).\
            filter(Game.map_id==Map.map_id).\
            filter(Game.map_id==map_id).\
            filter(PlayerGameStat.game_id==Game.game_id).\
            filter(PlayerGameStat.rank==1).\
            order_by(expr.desc(Game.start_dt)).all()[0:recent_games_count]

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

    except Exception as e:
        gmap = None
    return {'gmap':gmap,
            'recent_games':recent_games,
            'top_scorers':top_scorers,
            'top_players':top_players,
            'top_servers':top_servers,
            }


def map_info(request):
    """
    List the information stored about a given map.
    """
    mapinfo_data =  _map_info_data(request)

    # FIXME: code clone, should get these from _map_info_data
    leaderboard_count = 10
    recent_games_count = 20

    for i in range(recent_games_count-len(mapinfo_data['recent_games'])):
        mapinfo_data['recent_games'].append(('-', '-', '-', '-'))

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
