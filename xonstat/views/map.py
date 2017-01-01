import logging
from collections import namedtuple
from datetime import datetime, timedelta

import sqlalchemy.sql.expression as expr
import sqlalchemy.sql.functions as func
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import func as fg
from webhelpers.paginate import Page
from xonstat.models import DBSession, Server, Map, Game, PlayerGameStat, Player, PlayerCaptime
from xonstat.models.map import MapCapTime
from xonstat.util import page_url, html_colors
from xonstat.views.helpers import RecentGame, recent_games_q

log = logging.getLogger(__name__)

# Defaults
INDEX_COUNT = 20
LEADERBOARD_LIFETIME = 30


class MapIndex(object):
    """Returns a list of maps."""

    def __init__(self, request):
        """Common parameter parsing."""
        self.request = request
        self.page = request.params.get("page", 1)
        self.last = request.params.get("last", None)

        # all views share this data, so we'll pre-calculate
        self.maps = self.map_index()

    def map_index(self):
        """Returns the raw data shared by all renderers."""
        try:
            map_q = DBSession.query(Map)

            if self.last:
                map_q = map_q.filter(Map.map_id < self.last)

            map_q = map_q.order_by(Map.map_id.desc()).limit(INDEX_COUNT)
            maps = map_q.all()

        except Exception as e:
            log.debug(e)
            raise HTTPNotFound

        return maps

    def html(self):
        """For rendering this data using something HTML-based."""
        # build the query string
        query = {}
        if len(self.maps) > 1:
            query['last'] = self.maps[-1].map_id

        return {
            'maps': self.maps,
            'query': query,
        }

    def json(self):
        """For rendering this data using JSON."""
        return {
            'maps': [m.to_dict() for m in self.maps],
            'last': self.last,
        }


class MapInfoBase(object):
    """Base class for all map-based views with a map_id parameter in them."""

    def __init__(self, request, limit=None, last=None):
        """Common parameter parsing."""
        self.request = request
        self.map_id = request.matchdict.get("id", None)

        raw_lifetime = request.registry.settings.get('xonstat.leaderboard_lifetime',
                                                     LEADERBOARD_LIFETIME)
        self.lifetime = int(raw_lifetime)

        self.limit = request.params.get("limit", limit)
        self.last = request.params.get("last", last)
        self.now = datetime.utcnow()


class MapTopScorers(MapInfoBase):
    """Returns the top scorers on a given map."""

    def __init__(self, request, limit=INDEX_COUNT, last=None):
        """Common parameter parsing."""
        super(MapTopScorers, self).__init__(request, limit, last)
        self.top_scorers = self.get_top_scorers()

    def get_top_scorers(self):
        """Top players by score. Shared by all renderers."""
        cutoff = self.now - timedelta(days=self.lifetime)

        top_scorers_q = DBSession.query(
            fg.row_number().over(order_by=expr.desc(func.sum(PlayerGameStat.score))).label("rank"),
            Player.player_id, Player.nick, func.sum(PlayerGameStat.score).label("total_score"))\
            .filter(Player.player_id == PlayerGameStat.player_id)\
            .filter(Game.game_id == PlayerGameStat.game_id)\
            .filter(Game.map_id == self.map_id)\
            .filter(Player.player_id > 2)\
            .filter(PlayerGameStat.create_dt > cutoff)\
            .order_by(expr.desc(func.sum(PlayerGameStat.score)))\
            .group_by(Player.nick)\
            .group_by(Player.player_id)

        if self.last:
            top_scorers_q = top_scorers_q.offset(self.last)

        if self.limit:
            top_scorers_q = top_scorers_q.limit(self.limit)

        top_scorers = top_scorers_q.all()

        return top_scorers

    def html(self):
        """Returns an HTML-ready representation."""
        TopScorer = namedtuple("TopScorer", ["rank", "player_id", "nick", "total_score"])

        top_scorers = [TopScorer(ts.rank, ts.player_id, html_colors(ts.nick), ts.total_score)
                       for ts in self.top_scorers]

        # build the query string
        query = {}
        if len(top_scorers) > 1:
            query['last'] = top_scorers[-1].rank

        return {
            "map_id": self.map_id,
            "top_scorers": top_scorers,
            "lifetime": self.lifetime,
            "query": query,
        }

    def json(self):
        """For rendering this data using JSON."""
        top_scorers = [{
            "rank": ts.rank,
            "player_id": ts.player_id,
            "nick": ts.nick,
            "score": ts.total_score,
        } for ts in self.top_scorers]

        return {
            "map_id": self.map_id,
            "top_scorers": top_scorers,
        }


class MapTopPlayers(MapInfoBase):
    """Returns the top players on a given map, by playing time."""

    def __init__(self, request, limit=INDEX_COUNT, last=None):
        """Common parameter parsing."""
        super(MapTopPlayers, self).__init__(request, limit, last)
        self.top_players = self.get_top_players()

    def get_top_players(self):
        """Top players by playing time. Shared by all renderers."""
        cutoff = self.now - timedelta(days=self.lifetime)

        top_players_q = DBSession.query(fg.row_number().over(
            order_by=expr.desc(func.sum(PlayerGameStat.alivetime))).label("rank"),
            Player.player_id, Player.nick, func.sum(PlayerGameStat.alivetime).label("alivetime"))\
            .filter(Player.player_id == PlayerGameStat.player_id)\
            .filter(Game.game_id == PlayerGameStat.game_id)\
            .filter(Game.map_id == self.map_id)\
            .filter(Player.player_id > 2) \
            .filter(PlayerGameStat.create_dt > cutoff).\
            order_by(expr.desc(func.sum(PlayerGameStat.alivetime))).\
            group_by(Player.nick).\
            group_by(Player.player_id)

        if self.last:
            top_players_q = top_players_q.offset(self.last)

        if self.limit:
            top_players_q = top_players_q.limit(self.limit)

        top_players = top_players_q.all()

        return top_players

    def html(self):
        """Returns an HTML-ready representation."""
        TopPlayer = namedtuple("TopPlayer", ["rank", "player_id", "nick", "alivetime"])

        top_players = [TopPlayer(tp.rank, tp.player_id, html_colors(tp.nick), tp.alivetime)
                       for tp in self.top_players]

        # build the query string
        query = {}
        if len(top_players) > 1:
            query['last'] = top_players[-1].rank

        return {
            "map_id": self.map_id,
            "top_players": top_players,
            "lifetime": self.lifetime,
            "query": query,
        }

    def json(self):
        """For rendering this data using JSON."""
        top_players = [{
            "rank": tp.rank,
            "player_id": tp.player_id,
            "nick": tp.nick,
            "alivetime": tp.alivetime.total_seconds(),
        } for tp in self.top_players]

        return {
            "map_id": self.map_id,
            "top_scorers": top_players,
        }


def _map_info_data(request):
    map_id = int(request.matchdict['id'])

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

        # TODO make this a configuration parameter to be set in the settings
        # top captimes
        captimes_raw = DBSession.query(Player.player_id, Player.nick,
            PlayerCaptime.fastest_cap, PlayerCaptime.game_id).\
                filter(PlayerCaptime.map_id == map_id).\
                filter(Player.player_id == PlayerCaptime.player_id).\
                order_by(PlayerCaptime.fastest_cap).\
                limit(10).\
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

    current_page = request.params.get('page', 1)

    try:
        mmap = DBSession.query(Map).filter_by(map_id=map_id).one()

        mct_q = DBSession.query(PlayerCaptime.fastest_cap, PlayerCaptime.create_dt,
                PlayerCaptime.player_id, PlayerCaptime.game_id,
                Game.server_id, Server.name.label('server_name'),
                PlayerGameStat.nick.label('player_nick')).\
                filter(PlayerCaptime.map_id==map_id).\
                filter(PlayerCaptime.game_id==Game.game_id).\
                filter(PlayerCaptime.map_id==Map.map_id).\
                filter(Game.server_id==Server.server_id).\
                filter(PlayerCaptime.player_id==PlayerGameStat.player_id).\
                filter(PlayerCaptime.game_id==PlayerGameStat.game_id).\
                order_by(expr.asc(PlayerCaptime.fastest_cap))

    except Exception as e:
        raise HTTPNotFound

    map_captimes = Page(mct_q, current_page, items_per_page=20, url=page_url)

    map_captimes.items = [MapCapTime(row) for row in map_captimes.items]

    return {
            'map_id':map_id,
            'map':mmap,
            'captimes':map_captimes,
        }

def map_captimes(request):
    return map_captimes_data(request)

def map_captimes_json(request):
    current_page = request.params.get('page', 1)
    data = map_captimes_data(request)

    return {
            "map": data["map"].to_dict(),
            "captimes": [e.to_dict() for e in data["captimes"].items],
            "page": current_page,
            }
