import logging
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
from collections import namedtuple
from datetime import datetime, timedelta
from webhelpers.paginate import Page
from xonstat.models import *
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
    map_id = request.matchdict['id']

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

        # top captimes
        captimes_raw = DBSession.query(Player.player_id, Player.nick,
            PlayerCaptime.fastest_cap, PlayerCaptime.game_id).\
                filter(PlayerCaptime.map_id == map_id).\
                filter(Player.player_id == PlayerCaptime.player_id).\
                order_by(PlayerCaptime.fastest_cap).\
                limit(25).\
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
        
    MapCaptimes = namedtuple('PlayerCaptimes', ['fastest_cap', 'create_dt', 'create_dt_epoch', 'create_dt_fuzzy',
        'player_id', 'player_nick', 'player_nick_stripped', 'player_nick_html',
        'game_id', 'server_id', 'server_name'])

    dbquery = DBSession.query('fastest_cap', 'create_dt', 'player_id', 'game_id',
                'server_id', 'server_name', 'player_nick').\
            from_statement(
                "SELECT ct.fastest_cap, "
                       "ct.create_dt, "
                       "ct.player_id, "
                       "ct.game_id, "
                       "g.server_id, "
                       "s.name server_name, "
                       "pgs.nick player_nick "
                "FROM   player_map_captimes ct, "
                       "games g, "
                       "maps m, "
                       "servers s, "
                       "player_game_stats pgs "
                "WHERE  ct.map_id = :map_id "
                  "AND  g.game_id = ct.game_id "
                  "AND  g.server_id = s.server_id "
                  "AND  m.map_id = ct.map_id "
                  "AND  pgs.player_id = ct.player_id "
                  "AND  pgs.game_id = ct.game_id "
                "ORDER  BY ct.fastest_cap "
                "LIMIT  25"
            ).params(map_id=map_id).all()

    mmap = DBSession.query(Map).filter_by(map_id=map_id).one()

    map_captimes = []
    for row in dbquery:
        map_captimes.append(MapCaptimes(
                fastest_cap=row.fastest_cap,
                create_dt=row.create_dt,
                create_dt_epoch=timegm(row.create_dt.timetuple()),
                create_dt_fuzzy=pretty_date(row.create_dt),
                player_id=row.player_id,
                player_nick=row.player_nick,
                player_nick_stripped=strip_colors(row.player_nick),
                player_nick_html=html_colors(row.player_nick),
                game_id=row.game_id,
                server_id=row.server_id,
                server_name=row.server_name,
            ))

    return {
            'captimes':map_captimes,
            'map_id':map_id,
            'map_url':request.route_url('map_info', id=map_id),
            'map':mmap,
        }

def map_captimes(request):
    return map_captimes_data(request)

def map_captimes_json(request):
    return map_captimes_data(request)
