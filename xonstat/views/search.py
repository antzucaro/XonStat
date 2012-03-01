import datetime
import logging
import pyramid.httpexceptions
import re
import time
from pyramid.response import Response
from sqlalchemy import desc
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy import func
from xonstat.models import *
from xonstat.util import strip_colors, qfont_decode
from xonstat.util import page_url, html_colors
from webhelpers.paginate import Page, PageURL

log = logging.getLogger(__name__)

def search_q(nick=None, server_name=None, map_name=None, create_dt=None,
        gametypes=[]):
    session     = DBSession()
    result_type = None
    q           = None

    # player-only searches
    if nick and not server_name and not map_name and not create_dt \
        and len(gametypes) < 1:
        result_type = "player"
        q = session.query(Player)
        if nick:
            q = q.filter(
                    func.upper(Player.stripped_nick).like('%'+nick.upper()+'%')).\
                    filter(Player.player_id > 2).\
                    filter(Player.active_ind == True).\
                    order_by(Player.player_id)

    # server-only searches
    elif server_name and not nick and not map_name and not create_dt \
        and len(gametypes) < 1:
        result_type = "server"
        q = session.query(Server)
        if server_name:
            q = q.filter(func.upper(Server.name).\
                    like('%'+server_name.upper()+'%')).\
                    order_by(Server.server_id)

    # map-only searches
    elif map_name and not nick and not server_name and not create_dt \
        and len(gametypes) < 1:
        result_type = "map"
        q = session.query(Map)
        if map_name:
            q = q.filter(func.upper(Map.name).\
                    like('%'+map_name.upper()+'%')).\
                    order_by(Map.map_id)

    # game searches (all else)
    else:
        result_type = "game"
        q = session.query(Game, Server, Map).\
                filter(Game.server_id == Server.server_id).\
                filter(Game.map_id == Map.map_id).\
                order_by(Game.game_id.desc())
        if len(gametypes) > 0:
            q = q.filter(Game.game_type_cd.in_(gametypes))
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
    gametypes = []
    result_type = None
    results = None
    query = None

    if 'page' in request.matchdict:
        current_page = request.matchdict['page']
    else:
        current_page = 1

    if request.params.has_key('fs'):
        query = {'fs':''}
        if request.params.has_key('nick'):
            if request.params['nick'] != '':
                nick = request.params['nick']
                query['nick'] = nick
        if request.params.has_key('server_name'):
            if request.params['server_name'] != '':
                server_name = request.params['server_name']
                query['server_name'] = server_name
        if request.params.has_key('map_name'):
            if request.params['map_name'] != '':
                map_name = request.params['map_name']
                query['map_name'] = map_name
        if request.params.has_key('dm'):
                gametypes.append('dm')
                query['dm'] = ''
        if request.params.has_key('duel'):
                gametypes.append('duel')
                query['duel'] = ''
        if request.params.has_key('ctf'):
                gametypes.append('ctf')
                query['ctf'] = ''
        if request.params.has_key('tdm'):
                gametypes.append('tdm')
                query['tdm'] = ''
        if request.params.has_key('stype') and request.params.has_key('sval'):
            stype = request.params['stype']
            sval = request.params['sval']
            if stype == "players":
                nick = sval
            if stype == "servers":
                server_name = sval
            if stype == "maps":
                map_name = sval

        (result_type, q) = search_q(nick=nick, server_name=server_name,
                map_name=map_name, gametypes=gametypes)

        try:
            if q != None:
                results = Page(q, current_page, url=page_url)
        except Exception as e:
            raise e
            result_type = None
            results = None

    return {'result_type':result_type,
            'results':results,
            'query':query,
            }
