import datetime
import logging
import pyramid.httpexceptions
import re
import time
from pyramid.response import Response
from sqlalchemy import desc
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.sql import func
from xonstat.models import *
from xonstat.util import strip_colors, qfont_decode
from xonstat.util import page_url, html_colors
from webhelpers.paginate import Page, PageURL

log = logging.getLogger(__name__)

def search_q(nick=None, server_name=None, map_name=None, create_dt=None):
    session     = DBSession()
    result_type = None
    q           = None

    # player-only searches
    if nick and not server_name and not map_name and not create_dt:
        result_type = "player"
        q = session.query(Player)
        if nick:
            q = q.filter(
                    func.upper(Player.stripped_nick).like('%'+nick.upper()+'%'))

    # server-only searches
    elif server_name and not nick and not map_name and not create_dt:
        result_type = "server"
        q = session.query(Server)
        if server_name:
            q = q.filter(func.upper(Server.name).\
                    like('%'+server_name.upper()+'%'))

    # map-only searches
    elif map_name and not nick and not server_name and not create_dt:
        result_type = "map"
        q = session.query(Map)
        if map_name:
            q = q.filter(func.upper(Map.name).\
                    like('%'+map_name.upper()+'%'))

    # game searches (all else)
    else:
        result_type = "game"
        q = session.query(Game, Server, Map).\
                filter(Game.server_id == Server.server_id).\
                filter(Game.map_id == Map.map_id).\
                order_by(Game.game_id.desc())
        if nick:
            q = q.filter(func.upper(PlayerGameStat.stripped_nick).\
                    like('%'+nick.upper()+'%')).\
                filter(PlayerGameStat.game_id == Game.game_id)
        if map_name:
            q = q.filter(func.upper(Map.name).\
                    like('%'+map_name.upper()+'%'))
        if server_name:
            q = q.filter(func.upper(Server.name).\
                    like('%'+server_name.upper()+'%'))

    return (result_type, q)

def search(request):
    fs = None
    nick = None
    server_name = None
    map_name = None
    result_type = None
    results = None

    current_page = 1

    if request.params.has_key('fs'):
        if request.params.has_key('nick'):
            nick = request.params['nick']
        if request.params.has_key('server_name'):
            server_name = request.params['server_name']
        if request.params.has_key('map_name'):
            map_name = request.params['map_name']
        (result_type, q) = search_q(nick=nick, server_name=server_name,
                map_name=map_name)
        log.debug(q)

        try:
            if q != None:
                results = Page(q, current_page, url=page_url)
                log.debug(len(results))
        except Exception as e:
            raise e
            result_type = None
            results = None

    return {'result_type':result_type,
            'results':results,
            }
