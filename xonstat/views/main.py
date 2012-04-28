import logging
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
from datetime import datetime, timedelta
from pyramid.response import Response
from xonstat.models import *
from xonstat.util import *

log = logging.getLogger(__name__)

def main_index(request):
    try: 
        leaderboard_lifetime = int(
                request.registry.settings['xonstat.leaderboard_lifetime'])
    except:
        leaderboard_lifetime = 30

    leaderboard_count = 10
    recent_games_count = 20

    # top ranked duelers
    duel_ranks = DBSession.query(PlayerRank.player_id, PlayerRank.nick, 
            PlayerRank.elo).\
            filter(PlayerRank.game_type_cd=='duel').\
            order_by(PlayerRank.rank).\
            limit(10).all()

    duel_ranks = [(player_id, html_colors(nick), elo) \
            for (player_id, nick, elo) in duel_ranks]

    for i in range(leaderboard_count-len(duel_ranks)):
        duel_ranks.append(('-', '-', '-'))

    # top ranked CTF-ers
    ctf_ranks = DBSession.query(PlayerRank.player_id, PlayerRank.nick, 
            PlayerRank.elo).\
            filter(PlayerRank.game_type_cd=='ctf').\
            order_by(PlayerRank.rank).\
            limit(10).all()

    ctf_ranks = [(player_id, html_colors(nick), elo) \
            for (player_id, nick, elo) in ctf_ranks]

    for i in range(leaderboard_count-len(ctf_ranks)):
        ctf_ranks.append(('-', '-', '-'))

    # top ranked DM-ers
    dm_ranks = DBSession.query(PlayerRank.player_id, PlayerRank.nick, 
            PlayerRank.elo).\
            filter(PlayerRank.game_type_cd=='dm').\
            order_by(PlayerRank.rank).\
            limit(10).all()

    dm_ranks = [(player_id, html_colors(nick), elo) \
            for (player_id, nick, elo) in dm_ranks]

    for i in range(leaderboard_count-len(dm_ranks)):
        dm_ranks.append(('-', '-', '-'))

    right_now = datetime.utcnow()
    back_then = datetime.utcnow() - timedelta(days=leaderboard_lifetime)

    # top players by playing time
    top_players = DBSession.query(Player.player_id, Player.nick, 
            func.sum(PlayerGameStat.alivetime)).\
            filter(Player.player_id == PlayerGameStat.player_id).\
            filter(Player.player_id > 2).\
            filter(expr.between(PlayerGameStat.create_dt, back_then, right_now)).\
            order_by(expr.desc(func.sum(PlayerGameStat.alivetime))).\
            group_by(Player.nick).\
            group_by(Player.player_id).limit(10).all()

    top_players = [(player_id, html_colors(nick), score) \
            for (player_id, nick, score) in top_players]

    for i in range(leaderboard_count-len(top_players)):
        top_players.append(('-', '-', '-'))

    # top servers by number of total players played
    top_servers = DBSession.query(Server.server_id, Server.name, 
            func.count()).\
            filter(Game.server_id==Server.server_id).\
            filter(expr.between(Game.create_dt, back_then, right_now)).\
            order_by(expr.desc(func.count(Game.game_id))).\
            group_by(Server.server_id).\
            group_by(Server.name).limit(10).all()

    for i in range(leaderboard_count-len(top_servers)):
        top_servers.append(('-', '-', '-'))

    # top maps by total times played
    top_maps = DBSession.query(Game.map_id, Map.name, 
            func.count()).\
            filter(Map.map_id==Game.map_id).\
            filter(expr.between(Game.create_dt, back_then, right_now)).\
            order_by(expr.desc(func.count())).\
            group_by(Game.map_id).\
            group_by(Map.name).limit(10).all()

    for i in range(leaderboard_count-len(top_maps)):
        top_maps.append(('-', '-', '-'))

    # recent games played in descending order
    recent_games = DBSession.query(Game, Server, Map, PlayerGameStat).\
            filter(Game.server_id==Server.server_id).\
            filter(Game.map_id==Map.map_id).\
            filter(PlayerGameStat.game_id==Game.game_id).\
            filter(PlayerGameStat.rank==1).\
            filter(expr.between(Game.create_dt, back_then, right_now)).\
            order_by(expr.desc(Game.start_dt)).limit(recent_games_count).all()

    for i in range(recent_games_count-len(recent_games)):
        recent_games.append(('-', '-', '-', '-'))

    return {'top_players':top_players,
            'top_servers':top_servers,
            'top_maps':top_maps,
            'recent_games':recent_games,
            'duel_ranks':duel_ranks,
            'ctf_ranks':ctf_ranks,
            'dm_ranks':dm_ranks,
            }
