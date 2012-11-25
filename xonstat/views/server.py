import logging
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
import time
from datetime import datetime, timedelta
from sqlalchemy import desc
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url, html_colors
from xonstat.views.helpers import RecentGame, recent_games_q

log = logging.getLogger(__name__)

def _server_index_data(request):
    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    try:
        server_q = DBSession.query(Server).\
                order_by(Server.server_id.desc())

        servers = Page(server_q, current_page, items_per_page=10, url=page_url)

        
    except Exception as e:
        servers = None

    return {'servers':servers, }


def server_index(request):
    """
    Provides a list of all the current servers.
    """
    return _server_index_data(request)


def server_index_json(request):
    """
    Provides a list of all the current servers. JSON.
    """
    return [{'status':'not implemented'}]


def _server_info_data(request):
    server_id = request.matchdict['id']

    try: 
        leaderboard_lifetime = int(
                request.registry.settings['xonstat.leaderboard_lifetime'])
    except:
        leaderboard_lifetime = 30

    leaderboard_count = 10
    recent_games_count = 20

    try:
        server = DBSession.query(Server).filter_by(server_id=server_id).one()

        # top maps by total times played
        top_maps = DBSession.query(Game.map_id, Map.name, 
                func.count()).\
                filter(Map.map_id==Game.map_id).\
                filter(Game.server_id==server.server_id).\
                filter(Game.create_dt > 
                    (datetime.utcnow() - timedelta(days=leaderboard_lifetime))).\
                order_by(expr.desc(func.count())).\
                group_by(Game.map_id).\
                group_by(Map.name).all()[0:leaderboard_count]

        # top players by score
        top_scorers = DBSession.query(Player.player_id, Player.nick, 
                func.sum(PlayerGameStat.score)).\
                filter(Player.player_id == PlayerGameStat.player_id).\
                filter(Game.game_id == PlayerGameStat.game_id).\
                filter(Game.server_id == server.server_id).\
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
                filter(Game.server_id == server.server_id).\
                filter(Player.player_id > 2).\
                filter(PlayerGameStat.create_dt > 
                        (datetime.utcnow() - timedelta(days=leaderboard_lifetime))).\
                order_by(expr.desc(func.sum(PlayerGameStat.alivetime))).\
                group_by(Player.nick).\
                group_by(Player.player_id).all()[0:leaderboard_count]

        top_players = [(player_id, html_colors(nick), score) \
                for (player_id, nick, score) in top_players]

        # recent games played in descending order
        rgs = recent_games_q(server_id=server_id).limit(recent_games_count).all()
        recent_games = [RecentGame(row) for row in rgs]

    except Exception as e:
        server = None
        recent_games = None
        top_players = None
        raise e
    return {'server':server,
            'recent_games':recent_games,
            'top_players': top_players,
            'top_scorers': top_scorers,
            'top_maps': top_maps,
            }


def server_info(request):
    """
    List the stored information about a given server.
    """
    serverinfo_data =  _server_info_data(request)

    # FIXME: code clone, should get these from _server_info_data
    leaderboard_count = 10
    recent_games_count = 20

    for i in range(leaderboard_count-len(serverinfo_data['top_maps'])):
        serverinfo_data['top_maps'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(serverinfo_data['top_scorers'])):
        serverinfo_data['top_scorers'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(serverinfo_data['top_players'])):
        serverinfo_data['top_players'].append(('-', '-', '-'))

    return serverinfo_data


def server_info_json(request):
    """
    List the stored information about a given server. JSON.
    """
    return [{'status':'not implemented'}]


def _server_game_index_data(request):
    server_id = request.matchdict['server_id']
    current_page = request.matchdict['page']

    try:
        server = DBSession.query(Server).filter_by(server_id=server_id).one()

        games_q = DBSession.query(Game, Server, Map).\
                filter(Game.server_id == server_id).\
                filter(Game.server_id == Server.server_id).\
                filter(Game.map_id == Map.map_id).\
                order_by(Game.game_id.desc())

        games = Page(games_q, current_page, url=page_url)
    except Exception as e:
        server = None
        games = None
        raise e

    return {'games':games,
            'server':server}


def server_game_index(request):
    """
    List the games played on a given server. Paginated.
    """
    return _server_game_index_data(request)


def server_game_index_json(request):
    """
    List the games played on a given server. Paginated. JSON.
    """
    return [{'status':'not implemented'}]
