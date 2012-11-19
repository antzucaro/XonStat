import logging
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
from datetime import datetime, timedelta
from pyramid.response import Response
from xonstat.models import *
from xonstat.util import *
from xonstat.views.helpers import RecentGame, recent_games_q


log = logging.getLogger(__name__)


def _main_index_data(request):
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
            limit(leaderboard_count).all()

    duel_ranks = [(player_id, html_colors(nick), elo) \
            for (player_id, nick, elo) in duel_ranks]

    # top ranked CTF-ers
    ctf_ranks = DBSession.query(PlayerRank.player_id, PlayerRank.nick, 
            PlayerRank.elo).\
            filter(PlayerRank.game_type_cd=='ctf').\
            order_by(PlayerRank.rank).\
            limit(leaderboard_count).all()

    ctf_ranks = [(player_id, html_colors(nick), elo) \
            for (player_id, nick, elo) in ctf_ranks]

    # top ranked DM-ers
    dm_ranks = DBSession.query(PlayerRank.player_id, PlayerRank.nick, 
            PlayerRank.elo).\
            filter(PlayerRank.game_type_cd=='dm').\
            order_by(PlayerRank.rank).\
            limit(leaderboard_count).all()

    dm_ranks = [(player_id, html_colors(nick), elo) \
            for (player_id, nick, elo) in dm_ranks]

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
            group_by(Player.player_id).limit(leaderboard_count).all()

    top_players = [(player_id, html_colors(nick), score) \
            for (player_id, nick, score) in top_players]

    # top servers by number of total players played
    top_servers = DBSession.query(Server.server_id, Server.name, 
            func.count()).\
            filter(Game.server_id==Server.server_id).\
            filter(expr.between(Game.create_dt, back_then, right_now)).\
            order_by(expr.desc(func.count(Game.game_id))).\
            group_by(Server.server_id).\
            group_by(Server.name).limit(leaderboard_count).all()

    # top maps by total times played
    top_maps = DBSession.query(Game.map_id, Map.name, 
            func.count()).\
            filter(Map.map_id==Game.map_id).\
            filter(expr.between(Game.create_dt, back_then, right_now)).\
            order_by(expr.desc(func.count())).\
            group_by(Game.map_id).\
            group_by(Map.name).limit(leaderboard_count).all()

    # recent games played in descending order
    #rgs = recent_games_q(cutoff=back_then).limit(recent_games_count).all()
    #recent_games = [RecentGame(row) for row in rgs]
    recent_games = [RecentGame(row) for row in recent_games_q(cutoff=back_then).limit(recent_games_count).all()]
    return {'top_players':top_players,
            'top_servers':top_servers,
            'top_maps':top_maps,
            'recent_games':recent_games,
            'duel_ranks':duel_ranks,
            'ctf_ranks':ctf_ranks,
            'dm_ranks':dm_ranks,
            }


def main_index(request):
    """
    Display the main page information.
    """
    mainindex_data =  _main_index_data(request)

    # FIXME: code clone, should get these from _main_index_data
    leaderboard_count = 10
    recent_games_count = 20

    for i in range(leaderboard_count-len(mainindex_data['duel_ranks'])):
        mainindex_data['duel_ranks'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(mainindex_data['ctf_ranks'])):
        mainindex_data['ctf_ranks'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(mainindex_data['dm_ranks'])):
        mainindex_data['dm_ranks'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(mainindex_data['top_players'])):
        mainindex_data['top_players'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(mainindex_data['top_servers'])):
        mainindex_data['top_servers'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(mainindex_data['top_maps'])):
        mainindex_data['top_maps'].append(('-', '-', '-'))

    for i in range(recent_games_count-len(mainindex_data['recent_games'])):
        mainindex_data['recent_games'].append(('-', '-', '-', '-'))

    return mainindex_data


def main_index_json(request):
    """
    JSON output of the main page information.
    """
    return [{'status':'not implemented'}]
