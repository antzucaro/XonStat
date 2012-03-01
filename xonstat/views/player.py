import datetime
import logging
import re
import sqlalchemy as sa
import time
from pyramid.response import Response
from pyramid.url import current_route_url
from sqlalchemy import desc
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url

log = logging.getLogger(__name__)


def player_index(request):
    """
    Provides a list of all the current players. 
    """
    if 'page' in request.matchdict:
        current_page = int(request.matchdict['page'])
    else:
        current_page = 1

    try:
        player_q = DBSession.query(Player).\
                filter(Player.player_id > 2).\
                filter(Player.active_ind == True).\
                filter(sa.not_(Player.nick.like('Anonymous Player%'))).\
                order_by(Player.player_id.desc())

        players = Page(player_q, current_page, items_per_page=10, url=page_url)

        last_linked_page = current_page + 4
        if last_linked_page > players.last_page:
            last_linked_page = players.last_page

        pages_to_link = range(current_page+1, last_linked_page+1)

    except Exception as e:
        players = None
        raise e

    return {'players':players,
            'pages_to_link':pages_to_link,
            }


def player_info(request):
    """
    Provides detailed information on a specific player
    """
    player_id = int(request.matchdict['id'])
    if player_id <= 2:
        player_id = -1;
        
    try:
        player = DBSession.query(Player).filter_by(player_id=player_id).\
                filter(Player.active_ind == True).one()

        weapon_stats = DBSession.query("descr", "weapon_cd", "actual_total", 
                "max_total", "hit_total", "fired_total", "frags_total").\
                from_statement(
                    "select cw.descr, cw.weapon_cd, sum(actual) actual_total, "
                    "sum(max) max_total, sum(hit) hit_total, "
                    "sum(fired) fired_total, sum(frags) frags_total "
                    "from player_weapon_stats ws, cd_weapon cw "
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
        games_q = DBSession.query(Game, Server, Map).\
            filter(PlayerGameStat.game_id == Game.game_id).\
            filter(PlayerGameStat.player_id == player_id).\
            filter(Game.server_id == Server.server_id).\
            filter(Game.map_id == Map.map_id).\
            order_by(Game.game_id.desc())

        games = Page(games_q, current_page, url=page_url)

        pgstats = {}
        for (game, server, map) in games:
            pgstats[game.game_id] = DBSession.query(PlayerGameStat).\
                    filter(PlayerGameStat.game_id == game.game_id).\
                    order_by(PlayerGameStat.rank).\
                    order_by(PlayerGameStat.score).all()

    except Exception as e:
        player = None
        games = None

    return {'player_id':player_id,
            'games':games,
            'pgstats':pgstats}
