import datetime
import json
import logging
import re
import sqlalchemy as sa
import sqlalchemy.sql.functions as func
import time
from pyramid.response import Response
from pyramid.url import current_route_url
from sqlalchemy import desc, distinct
from webhelpers.paginate import Page, PageURL
from xonstat.models import *
from xonstat.util import page_url

log = logging.getLogger(__name__)


def _player_index_data(request):
    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    try:
        player_q = DBSession.query(Player).\
                filter(Player.player_id > 2).\
                filter(Player.active_ind == True).\
                filter(sa.not_(Player.nick.like('Anonymous Player%'))).\
                order_by(Player.player_id.desc())

        players = Page(player_q, current_page, items_per_page=10, url=page_url)

    except Exception as e:
        players = None
        raise e

    return {'players':players
           }


def player_index(request):
    """
    Provides a list of all the current players.
    """
    return _player_index_data(request)


def player_index_json(request):
    """
    Provides a list of all the current players. JSON.
    """
    return [{'status':'not implemented'}]


def _get_games_played(player_id):
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
def _get_total_stats(player_id):
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


def _get_fav_map(player_id):
    """
    Get the player's favorite map. The favorite map is defined
    as the map that he or she has played the most in the past 
    90 days.

    Returns a dictionary with keys for the map's name and id.
    """
    # 90 day window
    back_then = datetime.datetime.utcnow() - datetime.timedelta(days=90)

    raw_fav_map = DBSession.query(Map.name, Map.map_id).\
            filter(Game.game_id == PlayerGameStat.game_id).\
            filter(Game.map_id == Map.map_id).\
            filter(PlayerGameStat.player_id == player_id).\
            filter(PlayerGameStat.create_dt > back_then).\
            group_by(Map.name, Map.map_id).\
            order_by(func.count().desc()).\
            limit(1).one()

    fav_map = {}
    fav_map['name'] = raw_fav_map[0]
    fav_map['id'] = raw_fav_map[1]

    return fav_map


def get_accuracy_stats(player_id, weapon_cd, games):
    """
    Provides accuracy for weapon_cd by player_id for the past N games.
    """
    # Reaching back 90 days should give us an accurate enough average
    # We then multiply this out for the number of data points (games) to
    # create parameters for a flot graph
    try:
        raw_avg = DBSession.query(func.sum(PlayerWeaponStat.hit),
                func.sum(PlayerWeaponStat.fired)).\
                filter(PlayerWeaponStat.player_id == player_id).\
                filter(PlayerWeaponStat.weapon_cd == weapon_cd).\
                one()

        avg = round(float(raw_avg[0])/raw_avg[1]*100, 2)

        # Determine the raw accuracy (hit, fired) numbers for $games games
        # This is then enumerated to create parameters for a flot graph
        raw_accs = DBSession.query(PlayerWeaponStat.game_id, 
            PlayerWeaponStat.hit, PlayerWeaponStat.fired).\
                filter(PlayerWeaponStat.player_id == player_id).\
                filter(PlayerWeaponStat.weapon_cd == weapon_cd).\
                order_by(PlayerWeaponStat.game_id.desc()).\
                limit(games).\
                all()

        # they come out in opposite order, so flip them in the right direction
        raw_accs.reverse()

        accs = []
        for i in range(len(raw_accs)):
            accs.append((raw_accs[i][0], round(float(raw_accs[i][1])/raw_accs[i][2]*100, 2)))
    except:
        accs = []
        avg = 0.0

    return (avg, accs)


def get_damage_stats(player_id, weapon_cd, games):
    """
    Provides damage info for weapon_cd by player_id for the past N games.
    """
    try:
        raw_avg = DBSession.query(func.sum(PlayerWeaponStat.actual),
                func.sum(PlayerWeaponStat.hit)).\
                filter(PlayerWeaponStat.player_id == player_id).\
                filter(PlayerWeaponStat.weapon_cd == weapon_cd).\
                one()

        avg = round(float(raw_avg[0])/raw_avg[1], 2)

        # Determine the damage efficiency (hit, fired) numbers for $games games
        # This is then enumerated to create parameters for a flot graph
        raw_dmgs = DBSession.query(PlayerWeaponStat.game_id, 
            PlayerWeaponStat.actual, PlayerWeaponStat.hit).\
                filter(PlayerWeaponStat.player_id == player_id).\
                filter(PlayerWeaponStat.weapon_cd == weapon_cd).\
                order_by(PlayerWeaponStat.game_id.desc()).\
                limit(games).\
                all()

        # they come out in opposite order, so flip them in the right direction
        raw_dmgs.reverse()

        dmgs = []
        for i in range(len(raw_dmgs)):
            # try to derive, unless we've hit nothing then set to 0!
            try:
                dmg = round(float(raw_dmgs[i][1])/raw_dmgs[i][2], 2)
            except:
                dmg = 0.0

            dmgs.append((raw_dmgs[i][0], dmg))
    except Exception as e:
        dmgs = []
        avg = 0.0

    return (avg, dmgs)


def _player_info_data(request):
    player_id = int(request.matchdict['id'])
    if player_id <= 2:
        player_id = -1;

    try:
        player = DBSession.query(Player).filter_by(player_id=player_id).\
                filter(Player.active_ind == True).one()

        # games played, alivetime, wins, kills, deaths
        total_stats = _get_total_stats(player.player_id)

        # games breakdown - N games played (X ctf, Y dm) etc
        (total_games, games_breakdown) = _get_games_played(player.player_id)

        # favorite map from the past 90 days
        fav_map = _get_fav_map(player.player_id)

        # friendly display of elo information and preliminary status
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

        # which weapons have been used in the past 90 days
        # and also, used in 5 games or more?
        back_then = datetime.datetime.utcnow() - datetime.timedelta(days=90)
        recent_weapons = []
        for weapon in DBSession.query(PlayerWeaponStat.weapon_cd, func.count()).\
                filter(PlayerWeaponStat.player_id == player_id).\
                filter(PlayerWeaponStat.create_dt > back_then).\
                group_by(PlayerWeaponStat.weapon_cd).\
                having(func.count() > 4).\
                all():
                    recent_weapons.append(weapon[0])

        # recent games table, all data
        recent_games = DBSession.query(PlayerGameStat, Game, Server, Map).\
                filter(PlayerGameStat.player_id == player_id).\
                filter(PlayerGameStat.game_id == Game.game_id).\
                filter(Game.server_id == Server.server_id).\
                filter(Game.map_id == Map.map_id).\
                order_by(Game.game_id.desc())[0:10]

    except Exception as e:
        player = None
        elos_display = None
        total_stats = None
        recent_games = None
        total_games = None
        games_breakdown = None
        recent_weapons = []
        fav_map = None

    return {'player':player,
            'elos_display':elos_display,
            'recent_games':recent_games,
            'total_stats':total_stats,
            'total_games':total_games,
            'games_breakdown':games_breakdown,
            'recent_weapons':recent_weapons,
            'fav_map':fav_map,
            }


def player_info(request):
    """
    Provides detailed information on a specific player
    """
    return _player_info_data(request)


def player_info_json(request):
    """
    Provides detailed information on a specific player. JSON.
    """
    return [{'status':'not implemented'}]


def _player_game_index_data(request):
    player_id = request.matchdict['player_id']

    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    try:
        games_q = DBSession.query(Game, Server, Map).\
            filter(PlayerGameStat.game_id == Game.game_id).\
            filter(PlayerGameStat.player_id == player_id).\
            filter(Game.server_id == Server.server_id).\
            filter(Game.map_id == Map.map_id).\
            order_by(Game.game_id.desc())

        games = Page(games_q, current_page, items_per_page=10, url=page_url)

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


def player_game_index(request):
    """
    Provides an index of the games in which a particular
    player was involved. This is ordered by game_id, with
    the most recent game_ids first. Paginated.
    """
    return _player_game_index_data(request)


def player_game_index_json(request):
    """
    Provides an index of the games in which a particular
    player was involved. This is ordered by game_id, with
    the most recent game_ids first. Paginated. JSON.
    """
    return [{'status':'not implemented'}]


def _player_accuracy_data(request):
    player_id = request.matchdict['id']
    allowed_weapons = ['nex', 'rifle', 'shotgun', 'uzi', 'minstanex']
    weapon_cd = 'nex'
    games = 20

    if request.params.has_key('weapon'):
        if request.params['weapon'] in allowed_weapons:
            weapon_cd = request.params['weapon']

    if request.params.has_key('games'):
        try:
            games = request.params['games']

            if games < 0:
                games = 20
            if games > 50:
                games = 50
        except:
            games = 20

    (avg, accs) = get_accuracy_stats(player_id, weapon_cd, games)

    # if we don't have enough data for the given weapon
    if len(accs) < games:
        games = len(accs)

    return {
            'player_id':player_id, 
            'player_url':request.route_url('player_info', id=player_id), 
            'weapon':weapon_cd, 
            'games':games, 
            'avg':avg, 
            'accs':accs
            }


def player_accuracy(request):
    """
    Provides the accuracy for the given weapon. (JSON only)
    """
    return _player_accuracy_data(request)


def player_accuracy_json(request):
    """
    Provides a JSON response representing the accuracy for the given weapon.

    Parameters:
       weapon = which weapon to display accuracy for. Valid values are 'nex',
                'shotgun', 'uzi', and 'minstanex'.
       games = over how many games to display accuracy. Can be up to 50.
    """
    return _player_accuracy_data(request)


def _player_damage_data(request):
    player_id = request.matchdict['id']
    allowed_weapons = ['grenadelauncher', 'electro', 'crylink', 'hagar',
            'rocketlauncher', 'laser']
    weapon_cd = 'rocketlauncher'
    games = 20

    if request.params.has_key('weapon'):
        if request.params['weapon'] in allowed_weapons:
            weapon_cd = request.params['weapon']

    if request.params.has_key('games'):
        try:
            games = request.params['games']

            if games < 0:
                games = 20
            if games > 50:
                games = 50
        except:
            games = 20

    (avg, dmgs) = get_damage_stats(player_id, weapon_cd, games)

    # if we don't have enough data for the given weapon
    if len(dmgs) < games:
        games = len(dmgs)

    return {
            'player_id':player_id, 
            'player_url':request.route_url('player_info', id=player_id), 
            'weapon':weapon_cd, 
            'games':games, 
            'avg':avg, 
            'dmgs':dmgs
            }


def player_damage_json(request):
    """
    Provides a JSON response representing the damage for the given weapon.

    Parameters:
       weapon = which weapon to display damage for. Valid values are
         'grenadelauncher', 'electro', 'crylink', 'hagar', 'rocketlauncher',
         'laser'.
       games = over how many games to display damage. Can be up to 50.
    """
    return _player_damage_data(request)
