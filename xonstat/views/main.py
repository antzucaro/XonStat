import logging
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
from datetime import datetime, timedelta
from pyramid.config import get_current_registry
from pyramid.response import Response
from xonstat.models import *
from xonstat.util import *

log = logging.getLogger(__name__)

def main_index(request):
    settings = get_current_registry().settings
    try: 
        leaderboard_lifetime = int(
                settings['xonstat.leaderboard_lifetime'])
    except:
        leaderboard_lifetime = 30

    leaderboard_count = 10
    recent_games_count = 20

    # top players by score
    top_players = DBSession.query(Player.player_id, Player.nick, 
            func.sum(PlayerGameStat.score)).\
            filter(Player.player_id == PlayerGameStat.player_id).\
            filter(Player.player_id > 2).\
            filter(PlayerGameStat.create_dt > 
                    (datetime.now() - timedelta(days=leaderboard_lifetime))).\
            order_by(expr.desc(func.sum(PlayerGameStat.score))).\
            group_by(Player.nick).\
            group_by(Player.player_id).all()[0:10]

    top_players = [(player_id, html_colors(nick), score) \
            for (player_id, nick, score) in top_players]

    for i in range(leaderboard_count-len(top_players)):
        top_players.append(('-', '-', '-'))

    # top servers by number of total players played
    top_servers = DBSession.query(Server.server_id, Server.name, 
            func.count()).\
            filter(Game.server_id==Server.server_id).\
            filter(Game.create_dt > 
                (datetime.now() - timedelta(days=leaderboard_lifetime))).\
            order_by(expr.desc(func.count(Game.game_id))).\
            group_by(Server.server_id).\
            group_by(Server.name).all()[0:10]

    for i in range(leaderboard_count-len(top_servers)):
        top_servers.append(('-', '-', '-'))

    # top maps by total times played
    top_maps = DBSession.query(Game.map_id, Map.name, 
            func.count()).\
            filter(Map.map_id==Game.map_id).\
            filter(Game.create_dt > 
                (datetime.now() - timedelta(days=leaderboard_lifetime))).\
            order_by(expr.desc(func.count())).\
            group_by(Game.map_id).\
            group_by(Map.name).all()[0:10]

    for i in range(leaderboard_count-len(top_maps)):
        top_maps.append(('-', '-', '-'))

    # recent games played in descending order
    recent_games = DBSession.query(Game, Server, Map, PlayerGameStat).\
            filter(Game.server_id==Server.server_id).\
            filter(Game.map_id==Map.map_id).\
            filter(PlayerGameStat.game_id==Game.game_id).\
            filter(PlayerGameStat.rank==1).\
            order_by(expr.desc(Game.start_dt)).all()[0:recent_games_count]

    for i in range(recent_games_count-len(recent_games)):
        recent_games.append(('-', '-', '-', '-'))

    return {'top_players':top_players,
            'top_servers':top_servers,
            'top_maps':top_maps,
            'recent_games':recent_games,
            }
