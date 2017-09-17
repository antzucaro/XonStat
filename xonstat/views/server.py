import logging
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
from collections import namedtuple
from datetime import datetime, timedelta
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import func as fg
from webhelpers.paginate import Page
from xonstat.models import DBSession, Player, Server, Map, Game, PlayerGameStat
from xonstat.util import page_url, html_colors
from xonstat.views.helpers import RecentGame, recent_games_q

log = logging.getLogger(__name__)


# Defaults
LEADERBOARD_LIFETIME = 30
LEADERBOARD_COUNT = 10
INDEX_COUNT = 20
RECENT_GAMES_COUNT = 20


class ServerIndex(object):
    """Returns a list of servers."""

    def __init__(self, request):
        """Common parameter parsing."""
        self.request = request
        self.page = request.params.get("page", 1)
        self.servers = self.server_index()

    def server_index(self):
        """Returns the raw data shared by all renderers."""
        try:
            server_q = DBSession.query(Server)\
                .filter(Server.active_ind)\
                .order_by(Server.server_id.desc())
            servers = Page(server_q, self.page, items_per_page=25, url=page_url)

        except Exception as e:
            log.debug(e)
            raise HTTPNotFound

        return servers

    def html(self):
        """For rendering this data using something HTML-based."""
        return {
            'servers': self.servers,
        }

    def json(self):
        """For rendering this data using JSON."""
        return {
            'servers': [s.to_dict() for s in self.servers],
        }


class ServerInfoBase(object):
    """Baseline parameter parsing for Server URLs with a server_id in them."""

    def __init__(self, request, limit=None, last=None):
        """Common parameter parsing."""
        self.request = request
        self.server_id = request.matchdict.get("id", None)

        raw_lifetime = LEADERBOARD_LIFETIME

        self.lifetime = int(raw_lifetime)

        self.limit = request.params.get("limit", limit)
        self.last = request.params.get("last", last)
        self.now = datetime.utcnow()


class ServerTopMaps(ServerInfoBase):
    """Returns the top maps played on a given server."""

    def __init__(self, request, limit=INDEX_COUNT, last=None):
        """Common parameter parsing."""
        super(ServerTopMaps, self).__init__(request, limit, last)

        self.top_maps = self.top_maps()

    def top_maps(self):
        """Returns the raw data shared by all renderers."""
        try:
            top_maps_q = DBSession.query(
                fg.row_number().over(order_by=expr.desc(func.count())).label("rank"),
                Game.map_id, Map.name, func.count().label("times_played"))\
                .filter(Map.map_id == Game.map_id)\
                .filter(Game.server_id == self.server_id)\
                .filter(Game.create_dt > (self.now - timedelta(days=self.lifetime)))\
                .group_by(Game.map_id)\
                .group_by(Map.name) \
                .order_by(expr.desc(func.count()))

            if self.last:
                top_maps_q = top_maps_q.offset(self.last)

            if self.limit:
                top_maps_q = top_maps_q.limit(self.limit)

            top_maps = top_maps_q.all()
        except Exception as e:
            log.debug(e)
            raise HTTPNotFound

        return top_maps

    def html(self):
        """Returns the HTML-ready representation."""

        # build the query string
        query = {}
        if len(self.top_maps) > 1:
            query['last'] = self.top_maps[-1].rank

        return {
            "server_id": self.server_id,
            "top_maps": self.top_maps,
            "lifetime": self.lifetime,
            "query": query,
        }

    def json(self):
        """For rendering this data using JSON."""
        top_maps = [{
            "rank": tm.rank,
            "map_id": tm.map_id,
            "map_name": tm.name,
            "times_played": tm.times_played,
        } for tm in self.top_maps]

        return {
            "server_id": self.server_id,
            "top_maps": top_maps,
        }


class ServerTopScorers(ServerInfoBase):
    """Returns the top scorers on a given server."""

    def __init__(self, request, limit=INDEX_COUNT, last=None):
        """Common parameter parsing."""
        super(ServerTopScorers, self).__init__(request, limit, last)
        self.top_scorers = self.top_scorers()

    def top_scorers(self):
        """Top scorers on this server by total score."""
        try:
            top_scorers_q = DBSession.query(
                fg.row_number().over(
                    order_by=expr.desc(func.sum(PlayerGameStat.score))).label("rank"),
                Player.player_id, Player.nick,
                func.sum(PlayerGameStat.score).label("total_score"))\
                .filter(Player.player_id == PlayerGameStat.player_id)\
                .filter(Game.game_id == PlayerGameStat.game_id)\
                .filter(Game.server_id == self.server_id)\
                .filter(Player.player_id > 2)\
                .filter(PlayerGameStat.create_dt >
                        (self.now - timedelta(days=self.lifetime)))\
                .order_by(expr.desc(func.sum(PlayerGameStat.score)))\
                .group_by(Player.nick)\
                .group_by(Player.player_id)

            if self.last:
                top_scorers_q = top_scorers_q.offset(self.last)

            if self.limit:
                top_scorers_q = top_scorers_q.limit(self.limit)

            top_scorers = top_scorers_q.all()

        except Exception as e:
            log.debug(e)
            raise HTTPNotFound

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
            "server_id": self.server_id,
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
            "server_id": self.server_id,
            "top_scorers": top_scorers,
        }


class ServerTopPlayers(ServerInfoBase):
    """Returns the top players by playing time on a given server."""

    def __init__(self, request, limit=INDEX_COUNT, last=None):
        """Common parameter parsing."""
        super(ServerTopPlayers, self).__init__(request, limit, last)
        self.top_players = self.top_players()

    def top_players(self):
        """Top players on this server by total playing time."""
        try:
            top_players_q = DBSession.query(
                fg.row_number().over(
                    order_by=expr.desc(func.sum(PlayerGameStat.alivetime))).label("rank"),
                Player.player_id, Player.nick,
                func.sum(PlayerGameStat.alivetime).label("alivetime"))\
                .filter(Player.player_id == PlayerGameStat.player_id)\
                .filter(Game.game_id == PlayerGameStat.game_id)\
                .filter(Game.server_id == self.server_id)\
                .filter(Player.player_id > 2)\
                .filter(PlayerGameStat.create_dt > (self.now - timedelta(days=self.lifetime)))\
                .order_by(expr.desc(func.sum(PlayerGameStat.alivetime)))\
                .group_by(Player.nick)\
                .group_by(Player.player_id)

            if self.last:
                top_players_q = top_players_q.offset(self.last)

            if self.limit:
                top_players_q = top_players_q.limit(self.limit)

            top_players = top_players_q.all()

        except Exception as e:
            log.debug(e)
            raise HTTPNotFound

        return top_players

    def html(self):
        """Returns the HTML-ready representation."""
        TopPlayer = namedtuple("TopPlayer", ["rank", "player_id", "nick", "alivetime"])

        top_players = [TopPlayer(tp.rank, tp.player_id, html_colors(tp.nick), tp.alivetime)
                       for tp in self.top_players]

        # build the query string
        query = {}
        if len(top_players) > 1:
            query['last'] = top_players[-1].rank

        return {
            "server_id": self.server_id,
            "top_players": top_players,
            "lifetime": self.lifetime,
            "query": query,
        }

    def json(self):
        """For rendering this data using JSON."""
        top_players = [{
            "rank": ts.rank,
            "player_id": ts.player_id,
            "nick": ts.nick,
            "time": ts.alivetime.total_seconds(),
        } for ts in self.top_players]

        return {
            "server_id": self.server_id,
            "top_players": top_players,
        }


class ServerInfo(ServerInfoBase):
    """Returns detailed information about a particular server."""

    def __init__(self, request):
        """Common data and parameters."""
        super(ServerInfo, self).__init__(request)

        # this view uses data from other views, so we'll save the data at that level
        try:
            self.server = DBSession.query(Server)\
                .filter(Server.active_ind)\
                .filter(Server.server_id == self.server_id)\
                .one()

            self.top_maps_v = ServerTopMaps(self.request, limit=LEADERBOARD_COUNT)
            self.top_scorers_v = ServerTopScorers(self.request, limit=LEADERBOARD_COUNT)
            self.top_players_v = ServerTopPlayers(self.request, limit=LEADERBOARD_COUNT)

            rgs = recent_games_q(server_id=self.server_id).limit(RECENT_GAMES_COUNT).all()
            self.recent_games = [RecentGame(row) for row in rgs]
        except:
            raise HTTPNotFound

    def html(self):
        """For rendering this data using something HTML-based."""
        return {
            'server': self.server,
            'top_players': self.top_players_v.html().get("top_players", None),
            'top_scorers': self.top_scorers_v.html().get("top_scorers", None),
            'top_maps': self.top_maps_v.html().get("top_maps", None),
            'recent_games': self.recent_games,
            'lifetime': self.lifetime,
        }

    def json(self):
        """For rendering this data using JSON."""
        return {
            'server': self.server.to_dict(),
            'top_players': self.top_players_v.json(),
            'top_scorers': self.top_scorers_v.json(),
            'top_maps': self.top_maps_v.json(),
            'recent_games': [rg.to_dict() for rg in self.recent_games],
        }
