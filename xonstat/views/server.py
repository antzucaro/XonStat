import logging
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
import time
from datetime import datetime, timedelta
from pyramid.config import get_current_registry
from pyramid.response import Response
from sqlalchemy import desc
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url, html_colors

log = logging.getLogger(__name__)

def server_index(request):
    """
    Provides a list of all the current servers. 
    """
    if 'page' in request.matchdict:
        current_page = request.matchdict['page']
    else:
        current_page = 1

    try:
        server_q = DBSession.query(Server).\
                order_by(Server.name)

        servers = Page(server_q, current_page, url=page_url)

        
    except Exception as e:
        servers = None

    return {'servers':servers, }


def server_info(request):
    """
    List the stored information about a given server.
    """
    server_id = request.matchdict['id']

    # get settings specific to this view
    settings = get_current_registry().settings
    try: 
        leaderboard_lifetime = int(
                settings['xonstat.leaderboard_lifetime'])
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
                    (datetime.now() - timedelta(days=leaderboard_lifetime))).\
                order_by(expr.desc(func.count())).\
                group_by(Game.map_id).\
                group_by(Map.name).all()[0:10]

        for i in range(leaderboard_count-len(top_maps)):
            top_maps.append(('-', '-', '-'))

        # top players by score
        top_scorers = DBSession.query(Player.player_id, Player.nick, 
                func.sum(PlayerGameStat.score)).\
                filter(Player.player_id == PlayerGameStat.player_id).\
                filter(Game.game_id == PlayerGameStat.game_id).\
                filter(Game.server_id == server.server_id).\
                filter(Player.player_id > 2).\
                filter(PlayerGameStat.create_dt > 
                        (datetime.now() - timedelta(days=leaderboard_lifetime))).\
                order_by(expr.desc(func.sum(PlayerGameStat.score))).\
                group_by(Player.nick).\
                group_by(Player.player_id).all()[0:10]

        top_scorers = [(player_id, html_colors(nick), score) \
                for (player_id, nick, score) in top_scorers]

        for i in range(leaderboard_count-len(top_scorers)):
            top_scorers.append(('-', '-', '-'))

        # top players by playing time
        top_players = DBSession.query(Player.player_id, Player.nick, 
                func.sum(PlayerGameStat.alivetime)).\
                filter(Player.player_id == PlayerGameStat.player_id).\
                filter(Game.game_id == PlayerGameStat.game_id).\
                filter(Game.server_id == server.server_id).\
                filter(Player.player_id > 2).\
                filter(PlayerGameStat.create_dt > 
                        (datetime.now() - timedelta(days=leaderboard_lifetime))).\
                order_by(expr.desc(func.sum(PlayerGameStat.alivetime))).\
                group_by(Player.nick).\
                group_by(Player.player_id).all()[0:10]

        top_players = [(player_id, html_colors(nick), score) \
                for (player_id, nick, score) in top_players]

        for i in range(leaderboard_count-len(top_players)):
            top_players.append(('-', '-', '-'))

        # recent games played in descending order
        recent_games = DBSession.query(Game, Server, Map, PlayerGameStat).\
            filter(Game.server_id==Server.server_id).\
            filter(Game.map_id==Map.map_id).\
            filter(PlayerGameStat.game_id==Game.game_id).\
            filter(PlayerGameStat.rank==1).\
            filter(Server.server_id==server.server_id).\
            order_by(expr.desc(Game.start_dt)).all()[0:recent_games_count]

        for i in range(recent_games_count-len(recent_games)):
            recent_games.append(('-', '-', '-', '-'))

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


def server_game_index(request):
    """
    List the games played on a given server. Paginated.
    """
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
