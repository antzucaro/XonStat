import datetime
import logging
import re
import sqlalchemy as sa
import sqlalchemy.sql.functions as func
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


def get_games_played(player_id):
    """
    Provides a breakdown by gametype of the games played by player_id.

    Returns a tuple containing (total_games, games_breakdown), where
    total_games is the absolute number of games played by player_id
    and games_breakdown is an array containing (game_type_cd, # games)
    """
    games_played = DBSession.query(Game.game_type_cd, func.count()).\
            filter(Game.game_id == PlayerGameStat.game_id).\
            filter(PlayerGameStat.player_id == player_id).\
            group_by(Game.game_type_cd).\
            order_by(func.count().desc()).all()

    total = 0
    for (game_type_cd, games) in games_played:
        total += games

    return (total, games_played)


# TODO: should probably factor the above function into this one such that
# total_stats['ctf_games'] is the count of CTF games and so on...
def get_total_stats(player_id):
    """
    Provides aggregated stats by player_id.

    Returns a dict with the keys 'kills', 'deaths', 'alivetime'.

    kills = how many kills a player has over all games
    deaths = how many deaths a player has over all games
    alivetime = how long a player has played over all games

    If any of the above are None, they are set to 0.
    """
    total_stats = {}
    (total_stats['kills'], total_stats['deaths'], total_stats['alivetime']) = DBSession.\
            query("total_kills", "total_deaths", "total_alivetime").\
            from_statement(
                "select sum(kills) total_kills, "
                "sum(deaths) total_deaths, "
                "sum(alivetime) total_alivetime "
                "from player_game_stats "
                "where player_id=:player_id"
            ).params(player_id=player_id).one()

    (total_stats['wins'],) = DBSession.\
            query("total_wins").\
            from_statement(
                "select count(*) total_wins "
                "from games g, player_game_stats pgs "
                "where g.game_id = pgs.game_id "
                "and player_id=:player_id "
                "and (g.winner = pgs.team or pgs.rank = 1)"
            ).params(player_id=player_id).one()

    for (key,value) in total_stats.items():
        if value == None:
            total_stats[key] = 0

    return total_stats


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

        (total_games, games_breakdown) = get_games_played(player.player_id)

        total_stats = get_total_stats(player.player_id)

        elos = DBSession.query(PlayerElo).filter_by(player_id=player_id).\
                filter(PlayerElo.game_type_cd.in_(['ctf','duel','dm'])).\
                order_by(PlayerElo.elo.desc()).all()

        elos_display = []
        for elo in elos:
            if elo.games > 32:
                str = "{0} ({1})"
            else:
                str = "{0}* ({1})"

            elos_display.append(str.format(round(elo.elo, 3),
                elo.game_type_cd))

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

    except Exception as e:
        player = None
        elos_display = None
        weapon_stats = None
        total_stats = None
        recent_games = None
        total_games = None
        games_breakdown = None

    return {'player':player, 
            'elos_display':elos_display,
            'recent_games':recent_games,
            'weapon_stats':weapon_stats,
            'total_stats':total_stats, 
            'total_games':total_games,
            'games_breakdown':games_breakdown}


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
