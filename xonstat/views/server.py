import datetime
import logging
import time
from pyramid.response import Response
from sqlalchemy import desc
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url

log = logging.getLogger(__name__)


def server_info(request):
    """
    List the stored information about a given server.
    """
    server_id = request.matchdict['id']
    try:
        server = DBSession.query(Server).filter_by(server_id=server_id).one()
        recent_games = DBSession.query(Game, Server, Map).\
                filter(Game.server_id == server_id).\
                filter(Game.server_id == Server.server_id).\
                filter(Game.map_id == Map.map_id).\
                order_by(Game.game_id.desc())[0:10]

    except Exception as e:
        server = None
        recent_games = None
    return {'server':server,
            'recent_games':recent_games}


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
