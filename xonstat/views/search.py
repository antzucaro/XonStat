import datetime
import logging
import pyramid.httpexceptions
import re
import time
from pyramid.response import Response
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.sql import func
from xonstat.models import *
from xonstat.util import strip_colors, qfont_decode
from xonstat.util import page_url, html_colors
from webhelpers.paginate import Page, PageURL

log = logging.getLogger(__name__)

def search_q(player_id=None, nick=None, server_id=None, server_name=None,
        map_id=None, map_name=None, game_id=None, create_dt=None):
    session     = DBSession()
    result_type = None
    q           = None

    # player-only searches
    if ((player_id or nick) and not server_id and not server_name and not
            map_id and not map_name and not game_id and not create_dt):
        result_type = "player"
        q = session.query(Player)
        if nick:
            q = q.filter(func.upper(Player.stripped_nick).like('%'+nick.upper()+'%'))
        if player_id:
            q = q.filter(Player.player_id==player_id)
    # server-only searches
    elif ((server_id or server_name) and not player_id and not nick and not
            map_id and not map_name and not game_id and not create_dt):
        result_type = "server"
        q = session.query(Server)
        if server_name:
            q = q.filter(func.upper(Server.name).\
                    like('%'+server_name.upper()+'%'))
        if server_id:
            q = q.filter(Server.server_id==server_id)
    # map-only searches
    elif ((map_id or map_name) and not player_id and not nick and not
            server_id and not server_name and not game_id and not create_dt):
        result_type = "map"
        q = session.query(Map)
        if map_name:
            q = q.filter(func.upper(Map.name).\
                    like('%'+map_name.upper()+'%'))
        if map_id:
            q = q.filter(Map.map_id==map_id)

    return (result_type, q)

def search(request):
    form_submitted = None
    nick = None
    server_name = None
    map_name = None
    result_type = None
    results = None

    if request.params.has_key('form_submitted'):
        nick = request.params['nick']
        server_name = request.params['server_name']
        map_name = request.params['map_name']
        (result_type, q) = search_q(nick=nick, server_name=server_name,
                map_name=map_name)
        log.debug(q)

        try:
            if q != None:
                results = q.all()
        except Exception as e:
            raise e
            result_type = None
            results = None

    return {'result_type':result_type,
            'results':results,
            }
