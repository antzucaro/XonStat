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

log = logging.getLogger(__name__)

def search_q(player_id=None, nick=None, server_id=None, server_name=None,
        map_id=None, map_name=None, game_id=None, create_dt=None):
    session     = DBSession()
    result_type = None
    results     = None

    # player-only searches
    if ((player_id or nick) and not server_id and not server_name and not
            map_id and not map_name and not game_id and not create_dt):
        result_type = "player"
        q = session.query(Player)
        if nick:
            q = q.filter(func.upper(Player.stripped_nick).like('%'+nick.upper()+'%'))
        if player_id:
            q = q.filter(Player.player_id==player_id)

    try:
        results = q.all()
    except:
        result_type = None
        results = None

    return (result_type, results)

def search(request):
    result_type = None
    results = None

    if request.params.has_key('form.submitted'):
        nick = request.params['nick']
        (result_type, results) = search_q(nick=nick)

    return {'result_type':result_type,
            'results':results,
            }
