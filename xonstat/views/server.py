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
        self.servers = self._data()

    def _data(self):
        """Returns the data shared by all renderers."""
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


class ServerInfo(object):
    """Returns detailed information about a particular server."""

    def __init__(self, request):
        """Common parameter parsing."""
        self.request = request
        self.server_id = request.matchdict.get("id", None)

        raw_lifetime = request.registry.settings.get('xonstat.leaderboard_lifetime',
                                                     LEADERBOARD_LIFETIME)
        self.lifetime = int(raw_lifetime)

        self.now = datetime.utcnow()
        self.server_info = self._data()

    def _top_maps(self):
        """Top maps on this server by total times played."""
        try:
            top_maps = DBSession.query(Game.map_id, Map.name, func.count())\
                .filter(Map.map_id==Game.map_id)\
                .filter(Game.server_id==self.server_id)\
                .filter(Game.create_dt > (self.now - timedelta(days=self.lifetime)))\
                .group_by(Game.map_id)\
                .group_by(Map.name) \
                .order_by(expr.desc(func.count()))\
                .limit(LEADERBOARD_COUNT)
        except:
            top_maps = None

        return top_maps

    def _top_scorers(self):
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

            # We can't call a Python function directly in our query, so we have to convert
            # it out-of-band.
            top_scorers = [(player_id, html_colors(nick), score)
                           for (player_id, nick, score) in top_scorers]
        except:
            top_scorers = None

        return top_scorers

    def _top_players(self):
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

            # We can't call a Python function directly in our query, so we have to convert
            # it out-of-band.
            top_players = [(player_id, html_colors(nick), score) \
                    for (player_id, nick, score) in top_players]

        except:
            top_players = None

        return top_players

    def _data(self):
        """Returns the data shared by all renderers."""
        try:
            server = DBSession.query(Server).filter_by(server_id=self.server_id).one()

            top_maps = self._top_maps()
            top_scorers = self._top_scorers()
            top_players = self._top_players()

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
        return {"status":"Not implemented"}
