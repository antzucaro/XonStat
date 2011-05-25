import datetime
import logging
import re
import time
from pyramid.response import Response
from sqlalchemy import desc
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url

log = logging.getLogger(__name__)


def game_index(request):
    """
    Provides a list of current games, with the associated game stats.
    These games are ordered by game_id, with the most current ones first.
    Paginated.
    """
    if 'page' in request.matchdict:
        current_page = request.matchdict['page']
    else:
        current_page = 1

    games_q = DBSession.query(Game, Server, Map).\
            filter(Game.server_id == Server.server_id).\
            filter(Game.map_id == Map.map_id).\
            order_by(Game.game_id.desc())

    games = Page(games_q, current_page, url=page_url)

    pgstats = {}
    for (game, server, map) in games:
        pgstats[game.game_id] = DBSession.query(PlayerGameStat).\
                filter(PlayerGameStat.game_id == game.game_id).\
                order_by(PlayerGameStat.rank).\
                order_by(PlayerGameStat.score).all()

    return {'games':games, 
            'pgstats':pgstats}


def game_info(request):
    """
    List the game stats (scoreboard) for a particular game. Paginated.
    """
    game_id = request.matchdict['id']
    try:
        notfound = False

        (start_dt, game_type_cd, server_id, server_name, map_id, map_name) = \
        DBSession.query("start_dt", "game_type_cd", "server_id", 
                "server_name", "map_id", "map_name").\
                from_statement("select g.start_dt, g.game_type_cd, "
                        "g.server_id, s.name as server_name, g.map_id, "
                        "m.name as map_name "
                        "from games g, servers s, maps m "
                        "where g.game_id = :game_id "
                        "and g.server_id = s.server_id "
                        "and g.map_id = m.map_id").\
                        params(game_id=game_id).one()

        player_game_stats = DBSession.query(PlayerGameStat).\
                from_statement("select * from player_game_stats "
                        "where game_id = :game_id "
                        "order by score desc").\
                            params(game_id=game_id).all()
    except Exception as inst:
        notfound = True
        start_dt = None
        game_type_cd = None
        server_id = None
        server_name = None
        map_id = None
        map_name = None
        player_game_stats = None

    return {'notfound':notfound,
            'start_dt':start_dt,
            'game_type_cd':game_type_cd,
            'server_id':server_id,
            'server_name':server_name,
            'map_id':map_id,
            'map_name':map_name,
            'player_game_stats':player_game_stats}
