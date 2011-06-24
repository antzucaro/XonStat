import datetime
import logging
import re
import time
from pyramid.response import Response
from sqlalchemy import desc
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url

log = logging.getLogger(__name__)


def player_index(request):
    """
    Provides a list of all the current players. 
    """
    players = DBSession.query(Player)

    return {'players':players}

def player_info(request):
    """
    Provides detailed information on a specific player
    """
    player_id = request.matchdict['id']
    try:
        player = DBSession.query(Player).filter_by(player_id=player_id).one()

        weapon_stats = DBSession.query("descr", "weapon_cd", "actual_total", 
                "max_total", "hit_total", "fired_total", "frags_total").\
                from_statement(
                    "select cw.descr, cw.weapon_cd, sum(actual) actual_total, "
                    "sum(max) max_total, sum(hit) hit_total, "
                    "sum(fired) fired_total, sum(frags) frags_total "
                    "from xonstat.player_weapon_stats ws, xonstat.cd_weapon cw "
                    "where ws.weapon_cd = cw.weapon_cd "
                    "and player_id = :player_id "
                    "group by descr, cw.weapon_cd "
                    "order by descr"
                ).params(player_id=player_id).all()

        recent_games = DBSession.query(PlayerGameStat, Game, Server, Map).\
                filter(PlayerGameStat.player_id == player_id).\
                filter(PlayerGameStat.game_id == Game.game_id).\
                filter(Game.server_id == Server.server_id).\
                filter(Game.map_id == Map.map_id).\
                order_by(Game.game_id.desc())[0:10]

        game_stats = {}
        (game_stats['avg_rank'], game_stats['total_kills'], 
                game_stats['total_deaths'], game_stats['total_suicides'], 
                game_stats['total_score'], game_stats['total_time'], 
                game_stats['total_held'], game_stats['total_captures'], 
                game_stats['total_pickups'],game_stats['total_drops'], 
                game_stats['total_returns'], game_stats['total_collects'], 
                game_stats['total_destroys'], game_stats['total_dhk'], 
                game_stats['total_pushes'], game_stats['total_pushed'], 
                game_stats['total_carrier_frags'], 
                game_stats['total_alivetime'],
                game_stats['total_games_played']) = DBSession.\
                        query("avg_rank", "total_kills", "total_deaths", 
                "total_suicides", "total_score", "total_time", "total_held",
                "total_captures", "total_pickups", "total_drops", 
                "total_returns", "total_collects", "total_destroys", 
                "total_dhk", "total_pushes", "total_pushed", 
                "total_carrier_frags", "total_alivetime", 
                "total_games_played").\
                from_statement(
                    "select round(avg(rank)) avg_rank, sum(kills) total_kills, "
                    "sum(deaths) total_deaths, sum(suicides) total_suicides, "
                    "sum(score) total_score, sum(time) total_time, "
                    "sum(held) total_held, sum(captures) total_captures, "
                    "sum(pickups) total_pickups, sum(drops) total_drops, "
                    "sum(returns) total_returns, sum(collects) total_collects, "
                    "sum(destroys) total_destroys, sum(destroys_holding_key) total_dhk, "
                    "sum(pushes) total_pushes, sum(pushed) total_pushed, "
                    "sum(carrier_frags) total_carrier_frags, "
                    "sum(alivetime) total_alivetime, count(*) total_games_played "
                    "from player_game_stats "
                    "where player_id=:player_id"
                ).params(player_id=player_id).one()

        for (key,value) in game_stats.items():
            if value == None:
                game_stats[key] = '-'

    except Exception as e:
        player = None
        weapon_stats = None
        game_stats = None
        recent_games = None
        raise e
    return {'player':player, 
            'recent_games':recent_games,
            'weapon_stats':weapon_stats,
            'game_stats':game_stats}


def player_game_index(request):
    """
    Provides an index of the games in which a particular
    player was involved. This is ordered by game_id, with
    the most recent game_ids first. Paginated.
    """
    player_id = request.matchdict['player_id']

    if 'page' in request.matchdict:
        current_page = request.matchdict['page']
    else:
        current_page = 1

    try:
        player = DBSession.query(Player).filter_by(player_id=player_id).one()

        games_q = DBSession.query(PlayerGameStat, Game, Server, Map).\
                filter(PlayerGameStat.player_id == player_id).\
                filter(PlayerGameStat.game_id == Game.game_id).\
                filter(Game.server_id == Server.server_id).\
                filter(Game.map_id == Map.map_id).\
                order_by(Game.game_id.desc())

        games = Page(games_q, current_page, url=page_url)

        
    except Exception as e:
        player = None
        games = None

    return {'player':player,
            'games':games}
