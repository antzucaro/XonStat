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

    log.debug("testing logging; entered PlayerHandler.index()")
    return {'players':players}

def player_info(request):
    """
    Provides detailed information on a specific player
    """
    player_id = request.matchdict['id']
    try:
        player = DBSession.query(Player).filter_by(player_id=player_id).one()

        weapon_stats = DBSession.query("descr", "actual_total", 
                "max_total", "hit_total", "fired_total", "frags_total").\
                from_statement(
                    "select cw.descr, sum(actual) actual_total, "
                    "sum(max) max_total, sum(hit) hit_total, "
                    "sum(fired) fired_total, sum(frags) frags_total "
                    "from xonstat.player_weapon_stats ws, xonstat.cd_weapon cw "
                    "where ws.weapon_cd = cw.weapon_cd "
                    "and player_id = :player_id "
                    "group by descr "
                    "order by descr"
                ).params(player_id=player_id).all()

        log.debug(weapon_stats)

        recent_games = DBSession.query(PlayerGameStat, Game, Server, Map).\
                filter(PlayerGameStat.player_id == player_id).\
                filter(PlayerGameStat.game_id == Game.game_id).\
                filter(Game.server_id == Server.server_id).\
                filter(Game.map_id == Map.map_id).\
                order_by(Game.game_id.desc())[0:10]

    except Exception as e:
        player = None
        weapon_stats = None
        recent_games = None
    return {'player':player, 
            'recent_games':recent_games,
            'weapon_stats':weapon_stats}


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
        raise e

    return {'player':player,
            'games':games}


def player_weapon_stats(request):
    """
    List the accuracy statistics for the given player_id in a particular
    game.
    """
    game_id = request.matchdict['game_id']
    pgstat_id = request.matchdict['pgstat_id']
    try:
        pwstats = DBSession.query(PlayerWeaponStat, Weapon).\
                filter(PlayerWeaponStat.weapon_cd==Weapon.weapon_cd).\
                filter_by(game_id=game_id).\
                filter_by(player_game_stat_id=pgstat_id).\
                order_by(Weapon.descr).\
                all()

        pgstat = DBSession.query(PlayerGameStat).\
                filter_by(player_game_stat_id=pgstat_id).one()

        game = DBSession.query(Game).filter_by(game_id=game_id).one()

        log.debug(pwstats)
        log.debug(pgstat)
        log.debug(game)

    except Exception as e:
        pwstats = None
        pgstat = None
        game = None
        raise e
    return {'pwstats':pwstats, 'pgstat':pgstat, 'game':game}