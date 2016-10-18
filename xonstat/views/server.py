import logging
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
from datetime import datetime, timedelta
from pyramid.httpexceptions import HTTPNotFound
from webhelpers.paginate import Page
from xonstat.models import DBSession, Player, Server, Map, Game, PlayerGameStat
from xonstat.util import page_url, html_colors
from xonstat.views.helpers import RecentGame, recent_games_q

log = logging.getLogger(__name__)


# Defaults
LEADERBOARD_LIFETIME = 30
LEADERBOARD_COUNT = 10
RECENT_GAMES_COUNT = 20


class ServerIndex(object):
    """Returns a list of servers."""

    def __init__(self, request):
        """Common parameter parsing."""
        self.request = request
        self.page = request.params.get("page", 1)
        self.servers = self.raw()

    def raw(self):
        """Returns the raw data shared by all renderers."""
        try:
            server_q = DBSession.query(Server).order_by(Server.server_id.desc())
            servers = Page(server_q, self.page, items_per_page=25, url=page_url)

        except:
            servers = None

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

    def __init__(self, request):
        """Common parameter parsing."""
        self.request = request
        self.server_id = request.matchdict.get("id", None)

        raw_lifetime = request.registry.settings.get('xonstat.leaderboard_lifetime',
                                                     LEADERBOARD_LIFETIME)
        self.lifetime = int(raw_lifetime)

        self.now = datetime.utcnow()


class ServerTopMaps(ServerInfoBase):
    """Returns the top maps played on a given server."""

    def __init__(self, request):
        """Common parameter parsing."""
        super(ServerTopMaps, self).__init__(request)
        self.top_maps = self.raw()

    def raw(self):
        """Returns the raw data shared by all renderers."""
        try:
            top_maps = DBSession.query(Game.map_id, Map.name, func.count())\
                .filter(Map.map_id==Game.map_id)\
                .filter(Game.server_id==self.server_id)\
                .filter(Game.create_dt > (self.now - timedelta(days=self.lifetime)))\
                .group_by(Game.map_id)\
                .group_by(Map.name) \
                .order_by(expr.desc(func.count()))\
                .limit(LEADERBOARD_COUNT)\
                .all()
        except:
            top_maps = None

        return top_maps

    def json(self):
        """For rendering this data using JSON."""
        top_maps = [{
            "map_id": tm.map_id,
            "map_name": tm.name,
            "times_played": tm[2],
        } for tm in self.top_maps]

        return top_maps


class ServerTopScorers(ServerInfoBase):
    """Returns the top scorers on a given server."""

    def __init__(self, request):
        """Common parameter parsing."""

        super(ServerTopScorers, self).__init__(request)
        self.top_scorers = self.raw()

    def raw(self):
        """Top scorers on this server by total score."""
        try:
            top_scorers = DBSession.query(Player.player_id, Player.nick,
                                          func.sum(PlayerGameStat.score))\
                .filter(Player.player_id == PlayerGameStat.player_id)\
                .filter(Game.game_id == PlayerGameStat.game_id)\
                .filter(Game.server_id == self.server_id)\
                .filter(Player.player_id > 2)\
                .filter(PlayerGameStat.create_dt >
                        (self.now - timedelta(days=LEADERBOARD_LIFETIME)))\
                .order_by(expr.desc(func.sum(PlayerGameStat.score)))\
                .group_by(Player.nick)\
                .group_by(Player.player_id)\
                .limit(LEADERBOARD_COUNT)

        except:
            top_scorers = None

        return top_scorers

    def json(self):
        """For rendering this data using JSON."""
        top_scorers = [{
            "player_id": ts.player_id,
            "nick": ts.nick,
            "score": ts[2],
        } for ts in self.top_scorers]

        return top_scorers


class ServerTopPlayers(ServerInfoBase):
    """Returns the top players by playing time on a given server."""

    def __init__(self, request):
        """Common parameter parsing."""

        super(ServerTopPlayers, self).__init__(request)
        self.top_players = self.raw()

    def raw(self):
        """Top players on this server by total playing time."""
        try:
            top_players = DBSession.query(Player.player_id, Player.nick,
                                          func.sum(PlayerGameStat.alivetime))\
                .filter(Player.player_id == PlayerGameStat.player_id)\
                .filter(Game.game_id == PlayerGameStat.game_id)\
                .filter(Game.server_id == self.server_id)\
                .filter(Player.player_id > 2)\
                .filter(PlayerGameStat.create_dt > (self.now - timedelta(days=self.lifetime)))\
                .order_by(expr.desc(func.sum(PlayerGameStat.alivetime)))\
                .group_by(Player.nick)\
                .group_by(Player.player_id)\
                .limit(LEADERBOARD_COUNT)

        except:
            top_players = None

        return top_players

    def json(self):
        """For rendering this data using JSON."""
        top_players = [{
            "player_id": ts.player_id,
            "nick": ts.nick,
            "time": ts[2].total_seconds(),
        } for ts in self.top_players]

        return top_players


class ServerInfo(ServerInfoBase):
    """Returns detailed information about a particular server."""

    def __init__(self, request):
        """Common parameter parsing."""

        super(ServerInfo, self).__init__(request)
        self.server_info = self.raw()

    def raw(self):
        """Returns the raw data shared by all renderers."""
        try:
            server = DBSession.query(Server).filter_by(server_id=self.server_id).one()

            top_maps = ServerTopMaps(self.request).top_maps

            top_scorers_raw = ServerTopScorers(self.request).top_scorers
            top_scorers = [(player_id, html_colors(nick), score)
                           for (player_id, nick, score) in top_scorers_raw]

            top_players_raw = ServerTopPlayers(self.request).top_players
            top_players = [(player_id, html_colors(nick), score)
                           for (player_id, nick, score) in top_players_raw]

            rgs = recent_games_q(server_id=self.server_id).limit(RECENT_GAMES_COUNT).all()
            recent_games = [RecentGame(row) for row in rgs]
        except:
            raise HTTPNotFound

        return {
            'server': server,
            'recent_games': recent_games,
            'top_players': top_players,
            'top_scorers': top_scorers,
            'top_maps': top_maps,
        }

    def html(self):
        """For rendering this data using something HTML-based."""
        return self.server_info

    def json(self):
        """For rendering this data using JSON."""
        return {"status": "Not implemented"}
