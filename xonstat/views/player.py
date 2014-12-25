import datetime
import logging
import pyramid.httpexceptions
import sqlalchemy as sa
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
from calendar import timegm
from collections import namedtuple
from webhelpers.paginate import Page
from xonstat.models import *
from xonstat.util import page_url, to_json, pretty_date, datetime_seconds
from xonstat.util import is_cake_day, verify_request
from xonstat.views.helpers import RecentGame, recent_games_q
from urllib import unquote

log = logging.getLogger(__name__)


def player_index_data(request):
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

        players = Page(player_q, current_page, items_per_page=25, url=page_url)

    except Exception as e:
        players = None
        raise e

    return {'players':players
           }


def player_index(request):
    """
    Provides a list of all the current players.
    """
    return player_index_data(request)


def player_index_json(request):
    """
    Provides a list of all the current players. JSON.
    """
    return [{'status':'not implemented'}]


def get_games_played(player_id):
    """
    Provides a breakdown by gametype of the games played by player_id.

    Returns a list of namedtuples with the following members:
        - game_type_cd
        - games
        - wins
        - losses
        - win_pct

    The list itself is ordered by the number of games played
    """
    GamesPlayed = namedtuple('GamesPlayed', ['game_type_cd', 'games', 'wins',
        'losses', 'win_pct'])

    raw_games_played = DBSession.query('game_type_cd', 'wins', 'losses').\
            from_statement(
                "SELECT game_type_cd, "
                       "SUM(win) wins, "
                       "SUM(loss) losses "
                "FROM   (SELECT g.game_id, "
                               "g.game_type_cd, "
                               "CASE "
                                 "WHEN g.winner = pgs.team THEN 1 "
                                 "WHEN pgs.scoreboardpos = 1 THEN 1 "
                                 "ELSE 0 "
                               "END win, "
                               "CASE "
                                 "WHEN g.winner = pgs.team THEN 0 "
                                 "WHEN pgs.scoreboardpos = 1 THEN 0 "
                                 "ELSE 1 "
                               "END loss "
                        "FROM   games g, "
                               "player_game_stats pgs "
                        "WHERE  g.game_id = pgs.game_id "
                        "AND pgs.player_id = :player_id "
                        "AND g.players @> ARRAY[:player_id]) win_loss "
                "GROUP  BY game_type_cd "
            ).params(player_id=player_id).all()

    games_played = []
    overall_games = 0
    overall_wins = 0
    overall_losses = 0
    for row in raw_games_played:
        games = row.wins + row.losses
        overall_games += games
        overall_wins += row.wins
        overall_losses += row.losses
        win_pct = float(row.wins)/games * 100

        games_played.append(GamesPlayed(row.game_type_cd, games, row.wins,
            row.losses, win_pct))

    try:
        overall_win_pct = float(overall_wins)/overall_games * 100
    except:
        overall_win_pct = 0.0

    games_played.append(GamesPlayed('overall', overall_games, overall_wins,
        overall_losses, overall_win_pct))

    # sort the resulting list by # of games played
    games_played = sorted(games_played, key=lambda x:x.games)
    games_played.reverse()
    return games_played


def get_overall_stats(player_id):
    """
    Provides a breakdown of stats by gametype played by player_id.

    Returns a dictionary of namedtuples with the following members:
        - total_kills
        - total_deaths
        - k_d_ratio
        - last_played (last time the player played the game type)
        - last_played_epoch (same as above, but in seconds since epoch)
        - last_played_fuzzy (same as above, but in relative date)
        - total_playing_time (total amount of time played the game type)
        - total_playing_time_secs (same as the above, but in seconds)
        - total_pickups (ctf only)
        - total_captures (ctf only)
        - cap_ratio (ctf only)
        - total_carrier_frags (ctf only)
        - game_type_cd
        - game_type_descr

    The key to the dictionary is the game type code. There is also an
    "overall" game_type_cd which sums the totals and computes the total ratios.
    """
    OverallStats = namedtuple('OverallStats', ['total_kills', 'total_deaths',
        'k_d_ratio', 'last_played', 'last_played_epoch', 'last_played_fuzzy',
        'total_playing_time', 'total_playing_time_secs', 'total_pickups', 'total_captures', 'cap_ratio',
        'total_carrier_frags', 'game_type_cd', 'game_type_descr'])

    raw_stats = DBSession.query('game_type_cd', 'game_type_descr',
            'total_kills', 'total_deaths', 'last_played', 'total_playing_time',
            'total_pickups', 'total_captures', 'total_carrier_frags').\
            from_statement(
                "SELECT g.game_type_cd, "
                       "gt.descr game_type_descr, "
                       "Sum(pgs.kills)         total_kills, "
                       "Sum(pgs.deaths)        total_deaths, "
                       "Max(pgs.create_dt)     last_played, "
                       "Sum(pgs.alivetime)     total_playing_time, "
                       "Sum(pgs.pickups)       total_pickups, "
                       "Sum(pgs.captures)      total_captures, "
                       "Sum(pgs.carrier_frags) total_carrier_frags "
                "FROM   games g, "
                       "cd_game_type gt, "
                       "player_game_stats pgs "
                "WHERE  g.game_id = pgs.game_id "
                  "AND  g.game_type_cd = gt.game_type_cd "
                  "AND  g.players @> ARRAY[:player_id] "
                  "AND  pgs.player_id = :player_id "
                "GROUP  BY g.game_type_cd, game_type_descr "
                "UNION "
                "SELECT 'overall'              game_type_cd, "
                       "'Overall'              game_type_descr, "
                       "Sum(pgs.kills)         total_kills, "
                       "Sum(pgs.deaths)        total_deaths, "
                       "Max(pgs.create_dt)     last_played, "
                       "Sum(pgs.alivetime)     total_playing_time, "
                       "Sum(pgs.pickups)       total_pickups, "
                       "Sum(pgs.captures)      total_captures, "
                       "Sum(pgs.carrier_frags) total_carrier_frags "
                "FROM   player_game_stats pgs "
                "WHERE  pgs.player_id = :player_id "
            ).params(player_id=player_id).all()

    # to be indexed by game_type_cd
    overall_stats = {}

    for row in raw_stats:
        # individual gametype ratio calculations
        try:
            k_d_ratio = float(row.total_kills)/row.total_deaths
        except:
            k_d_ratio = None

        try:
            cap_ratio = float(row.total_captures)/row.total_pickups
        except:
            cap_ratio = None

        # everything else is untouched or "raw"
        os = OverallStats(total_kills=row.total_kills,
                total_deaths=row.total_deaths,
                k_d_ratio=k_d_ratio,
                last_played=row.last_played,
                last_played_epoch=timegm(row.last_played.timetuple()),
                last_played_fuzzy=pretty_date(row.last_played),
                total_playing_time=row.total_playing_time,
                total_playing_time_secs=int(datetime_seconds(row.total_playing_time)),
                total_pickups=row.total_pickups,
                total_captures=row.total_captures,
                cap_ratio=cap_ratio,
                total_carrier_frags=row.total_carrier_frags,
                game_type_cd=row.game_type_cd,
                game_type_descr=row.game_type_descr)

        overall_stats[row.game_type_cd] = os

    # We have to edit "overall" stats to exclude deaths in CTS.
    # Although we still want to record deaths, they shouldn't
    # count towards the overall K:D ratio.
    if 'cts' in overall_stats:
        os = overall_stats['overall']

        try:
            k_d_ratio = float(os.total_kills)/(os.total_deaths - overall_stats['cts'].total_deaths)
        except:
            k_d_ratio = None

        non_cts_deaths = os.total_deaths - overall_stats['cts'].total_deaths


        overall_stats['overall'] = OverallStats(
                total_kills             = os.total_kills,
                total_deaths            = non_cts_deaths,
                k_d_ratio               = k_d_ratio,
                last_played             = os.last_played,
                last_played_epoch       = os.last_played_epoch,
                last_played_fuzzy       = os.last_played_fuzzy,
                total_playing_time      = os.total_playing_time,
                total_playing_time_secs = os.total_playing_time_secs,
                total_pickups           = os.total_pickups,
                total_captures          = os.total_captures,
                cap_ratio               = os.cap_ratio,
                total_carrier_frags     = os.total_carrier_frags,
                game_type_cd            = os.game_type_cd,
                game_type_descr         = os.game_type_descr)

    return overall_stats


def get_fav_maps(player_id, game_type_cd=None):
    """
    Provides a breakdown of favorite maps by gametype.

    Returns a dictionary of namedtuples with the following members:
        - game_type_cd
        - map_name (map name)
        - map_id
        - times_played

    The favorite map is defined as the map you've played the most
    for the given game_type_cd.

    The key to the dictionary is the game type code. There is also an
    "overall" game_type_cd which is the overall favorite map. This is
    defined as the favorite map of the game type you've played the
    most. The input parameter game_type_cd is for this.
    """
    FavMap = namedtuple('FavMap', ['map_name', 'map_id', 'times_played', 'game_type_cd'])

    raw_favs = DBSession.query('game_type_cd', 'map_name',
            'map_id', 'times_played').\
            from_statement(
                "SELECT game_type_cd, "
                       "name map_name, "
                       "map_id, "
                       "times_played "
                "FROM   (SELECT g.game_type_cd, "
                               "m.name, "
                               "m.map_id, "
                               "Count(*) times_played, "
                               "Row_number() "
                                 "OVER ( "
                                   "partition BY g.game_type_cd "
                                   "ORDER BY Count(*) DESC, m.map_id ASC) rank "
                        "FROM   games g, "
                               "player_game_stats pgs, "
                               "maps m "
                        "WHERE  g.game_id = pgs.game_id "
                               "AND g.map_id = m.map_id "
                               "AND g.players @> ARRAY[:player_id]"
                               "AND pgs.player_id = :player_id "
                        "GROUP  BY g.game_type_cd, "
                                  "m.map_id, "
                                  "m.name) most_played "
                "WHERE  rank = 1 "
                "ORDER BY  times_played desc "
            ).params(player_id=player_id).all()

    fav_maps = {}
    overall_fav = None
    for row in raw_favs:
        fv = FavMap(map_name=row.map_name,
            map_id=row.map_id,
            times_played=row.times_played,
            game_type_cd=row.game_type_cd)

        # if we aren't given a favorite game_type_cd
        # then the overall favorite is the one we've
        # played the most
        if overall_fav is None:
            fav_maps['overall'] = fv
            overall_fav = fv.game_type_cd

        # otherwise it is the favorite map from the
        # favorite game_type_cd (provided as a param)
        # and we'll overwrite the first dict entry
        if game_type_cd == fv.game_type_cd:
            fav_maps['overall'] = fv

        fav_maps[row.game_type_cd] = fv

    return fav_maps


def get_ranks(player_id):
    """
    Provides a breakdown of the player's ranks by game type.

    Returns a dictionary of namedtuples with the following members:
        - game_type_cd
        - rank
        - max_rank

    The key to the dictionary is the game type code. There is also an
    "overall" game_type_cd which is the overall best rank.
    """
    Rank = namedtuple('Rank', ['rank', 'max_rank', 'percentile', 'game_type_cd'])

    raw_ranks = DBSession.query("game_type_cd", "rank", "max_rank").\
            from_statement(
                "select pr.game_type_cd, pr.rank, overall.max_rank "
                "from player_ranks pr,  "
                   "(select game_type_cd, max(rank) max_rank "
                    "from player_ranks  "
                    "group by game_type_cd) overall "
                "where pr.game_type_cd = overall.game_type_cd  "
                "and max_rank > 1 "
                "and player_id = :player_id "
                "order by rank").\
            params(player_id=player_id).all()

    ranks = {}
    found_top_rank = False
    for row in raw_ranks:
        rank = Rank(rank=row.rank,
            max_rank=row.max_rank,
            percentile=100 - 100*float(row.rank-1)/(row.max_rank-1),
            game_type_cd=row.game_type_cd)


        if not found_top_rank:
            ranks['overall'] = rank
            found_top_rank = True
        elif rank.percentile > ranks['overall'].percentile:
            ranks['overall'] = rank

        ranks[row.game_type_cd] = rank

    return ranks;


def get_elos(player_id):
    """
    Provides a breakdown of the player's elos by game type.

    Returns a dictionary of namedtuples with the following members:
        - player_id
        - game_type_cd
        - games
        - elo

    The key to the dictionary is the game type code. There is also an
    "overall" game_type_cd which is the overall best rank.
    """
    raw_elos = DBSession.query(PlayerElo).filter_by(player_id=player_id).\
            order_by(PlayerElo.elo.desc()).all()

    elos = {}
    found_max_elo = False
    for row in raw_elos:
        if not found_max_elo:
            elos['overall'] = row
            found_max_elo = True

        elos[row.game_type_cd] = row

    return elos


def get_recent_games(player_id, limit=10):
    """
    Provides a list of recent games for a player. Uses the recent_games_q helper.
    """
    # recent games played in descending order
    rgs = recent_games_q(player_id=player_id, force_player_id=True).limit(limit).all()
    recent_games = [RecentGame(row) for row in rgs]

    return recent_games


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


def player_info_data(request):
    player_id = int(request.matchdict['id'])
    if player_id <= 2:
        player_id = -1;

    try:
        player = DBSession.query(Player).filter_by(player_id=player_id).\
                filter(Player.active_ind == True).one()

        games_played   = get_games_played(player_id)
        overall_stats  = get_overall_stats(player_id)
        fav_maps       = get_fav_maps(player_id)
        elos           = get_elos(player_id)
        ranks          = get_ranks(player_id)
        recent_games   = get_recent_games(player_id)
        cake_day       = is_cake_day(player.create_dt)

    except Exception as e:
        raise pyramid.httpexceptions.HTTPNotFound

        ## do not raise application exceptions here (only for debugging)
        # raise e

    return {'player':player,
            'games_played':games_played,
            'overall_stats':overall_stats,
            'fav_maps':fav_maps,
            'elos':elos,
            'ranks':ranks,
            'recent_games':recent_games,
            'cake_day':cake_day,
            }


def player_info(request):
    """
    Provides detailed information on a specific player
    """
    return player_info_data(request)


def player_info_json(request):
    """
    Provides detailed information on a specific player. JSON.
    """

    # All player_info fields are converted into JSON-formattable dictionaries
    player_info = player_info_data(request)

    player = player_info['player'].to_dict()

    games_played = {}
    for game in player_info['games_played']:
        games_played[game.game_type_cd] = to_json(game)

    overall_stats = {}
    for gt,stats in player_info['overall_stats'].items():
        overall_stats[gt] = to_json(stats)

    elos = {}
    for gt,elo in player_info['elos'].items():
        elos[gt] = to_json(elo.to_dict())

    ranks = {}
    for gt,rank in player_info['ranks'].items():
        ranks[gt] = to_json(rank)

    fav_maps = {}
    for gt,mapinfo in player_info['fav_maps'].items():
        fav_maps[gt] = to_json(mapinfo)

    recent_games = []
    for game in player_info['recent_games']:
        recent_games.append(to_json(game))

    return [{
        'player':           player,
        'games_played':     games_played,
        'overall_stats':    overall_stats,
        'fav_maps':         fav_maps,
        'elos':             elos,
        'ranks':            ranks,
        'recent_games':     recent_games,
    }]
    #return [{'status':'not implemented'}]


def player_game_index_data(request):
    player_id = request.matchdict['player_id']

    game_type_cd = None
    game_type_descr = None

    if request.params.has_key('type'):
        game_type_cd = request.params['type']
        try:
            game_type_descr = DBSession.query(GameType.descr).\
                filter(GameType.game_type_cd == game_type_cd).\
                one()[0]
        except Exception as e:
            pass

    else:
        game_type_cd = None
        game_type_descr = None

    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    try:
        player = DBSession.query(Player).\
                filter_by(player_id=player_id).\
                filter(Player.active_ind == True).\
                one()

        rgs_q = recent_games_q(player_id=player.player_id,
            force_player_id=True, game_type_cd=game_type_cd)

        games = Page(rgs_q, current_page, items_per_page=20, url=page_url)

        # replace the items in the canned pagination class with more rich ones
        games.items = [RecentGame(row) for row in games.items]

        games_played = get_games_played(player_id)

    except Exception as e:
        player = None
        games = None
        game_type_cd = None
        game_type_descr = None
        games_played = None

    return {
            'player_id':player.player_id,
            'player':player,
            'games':games,
            'game_type_cd':game_type_cd,
            'game_type_descr':game_type_descr,
            'games_played':games_played,
           }


def player_game_index(request):
    """
    Provides an index of the games in which a particular
    player was involved. This is ordered by game_id, with
    the most recent game_ids first. Paginated.
    """
    return player_game_index_data(request)


def player_game_index_json(request):
    """
    Provides an index of the games in which a particular
    player was involved. This is ordered by game_id, with
    the most recent game_ids first. Paginated. JSON.
    """
    return [{'status':'not implemented'}]


def player_accuracy_data(request):
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
    return player_accuracy_data(request)


def player_accuracy_json(request):
    """
    Provides a JSON response representing the accuracy for the given weapon.

    Parameters:
       weapon = which weapon to display accuracy for. Valid values are 'nex',
                'shotgun', 'uzi', and 'minstanex'.
       games = over how many games to display accuracy. Can be up to 50.
    """
    return player_accuracy_data(request)


def player_damage_data(request):
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
    return player_damage_data(request)


def player_hashkey_info_data(request):
    # hashkey = request.matchdict['hashkey']

    # the incoming hashkey is double quoted, and WSGI unquotes once...
    # hashkey = unquote(hashkey)

    # if using request verification to obtain the hashkey
    (idfp, status) = verify_request(request)
    log.debug("d0_blind_id verification: idfp={0} status={1}\n".format(idfp, status))

    log.debug("\n----- BEGIN REQUEST BODY -----\n" + request.body +
            "----- END REQUEST BODY -----\n\n")

    # if config is to *not* verify requests and we get nothing back, this
    # query will return nothing and we'll 404.
    try:
        player = DBSession.query(Player).\
                filter(Player.player_id == Hashkey.player_id).\
                filter(Player.active_ind == True).\
                filter(Hashkey.hashkey == idfp).one()

        games_played      = get_games_played(player.player_id)
        overall_stats     = get_overall_stats(player.player_id)
        fav_maps          = get_fav_maps(player.player_id)
        elos              = get_elos(player.player_id)
        ranks             = get_ranks(player.player_id)
        most_recent_game  = get_recent_games(player.player_id, 1)[0]

    except Exception as e:
        raise pyramid.httpexceptions.HTTPNotFound

    return {'player':player,
            'hashkey':idfp,
            'games_played':games_played,
            'overall_stats':overall_stats,
            'fav_maps':fav_maps,
            'elos':elos,
            'ranks':ranks,
            'most_recent_game':most_recent_game,
            }


def player_hashkey_info_json(request):
    """
    Provides detailed information on a specific player. JSON.
    """

    # All player_info fields are converted into JSON-formattable dictionaries
    player_info = player_hashkey_info_data(request)

    player = player_info['player'].to_dict()

    games_played = {}
    for game in player_info['games_played']:
        games_played[game.game_type_cd] = to_json(game)

    overall_stats = {}
    for gt,stats in player_info['overall_stats'].items():
        overall_stats[gt] = to_json(stats)

    elos = {}
    for gt,elo in player_info['elos'].items():
        elos[gt] = to_json(elo.to_dict())

    ranks = {}
    for gt,rank in player_info['ranks'].items():
        ranks[gt] = to_json(rank)

    fav_maps = {}
    for gt,mapinfo in player_info['fav_maps'].items():
        fav_maps[gt] = to_json(mapinfo)

    most_recent_game = to_json(player_info['most_recent_game'])

    return [{
        'version':          1,
        'player':           player,
        'games_played':     games_played,
        'overall_stats':    overall_stats,
        'fav_maps':         fav_maps,
        'elos':             elos,
        'ranks':            ranks,
        'most_recent_game': most_recent_game,
    }]


def player_hashkey_info_text(request):
    """
    Provides detailed information on a specific player. Plain text.
    """
    # UTC epoch
    now = timegm(datetime.datetime.utcnow().timetuple())

    # All player_info fields are converted into JSON-formattable dictionaries
    player_info = player_hashkey_info_data(request)

    # gather all of the data up into aggregate structures
    player = player_info['player']
    games_played = player_info['games_played']
    overall_stats = player_info['overall_stats']
    elos = player_info['elos']
    ranks = player_info['ranks']
    fav_maps = player_info['fav_maps']
    most_recent_game = player_info['most_recent_game']

    # one-offs for things needing conversion for text/plain
    player_joined = timegm(player.create_dt.timetuple())
    player_joined_dt = player.create_dt
    alivetime = int(datetime_seconds(overall_stats['overall'].total_playing_time))

    # this is a plain text response, if we don't do this here then
    # Pyramid will assume html
    request.response.content_type = 'text/plain'

    return {
        'version':          1,
        'now':              now,
        'player':           player,
        'hashkey':          player_info['hashkey'],
        'player_joined':    player_joined,
        'player_joined_dt': player_joined_dt,
        'games_played':     games_played,
        'overall_stats':    overall_stats,
        'alivetime':        alivetime,
        'fav_maps':         fav_maps,
        'elos':             elos,
        'ranks':            ranks,
        'most_recent_game': most_recent_game,
    }


def player_elo_info_data(request):
    """
    Provides elo information on a specific player. Raw data is returned.
    """
    (idfp, status) = verify_request(request)
    log.debug("d0_blind_id verification: idfp={0} status={1}\n".format(idfp, status))

    log.debug("\n----- BEGIN REQUEST BODY -----\n" + request.body +
            "----- END REQUEST BODY -----\n\n")

    hashkey = request.matchdict['hashkey']

    # the incoming hashkey is double quoted, and WSGI unquotes once...
    hashkey = unquote(hashkey)

    try:
        player = DBSession.query(Player).\
                filter(Player.player_id == Hashkey.player_id).\
                filter(Player.active_ind == True).\
                filter(Hashkey.hashkey == hashkey).one()

        elos = get_elos(player.player_id)

    except Exception as e:
        log.debug(e)
        raise pyramid.httpexceptions.HTTPNotFound

    return {
        'hashkey':hashkey,
        'player':player,
        'elos':elos,
    }


def player_elo_info_json(request):
    """
    Provides elo information on a specific player. JSON.
    """
    elo_info = player_elo_info_data(request)

    player = player_info['player'].to_dict()

    elos = {}
    for gt, elo in elo_info['elos'].items():
        elos[gt] = to_json(elo.to_dict())

    return [{
        'version':          1,
        'player':           player,
        'elos':             elos,
    }]


def player_elo_info_text(request):
    """
    Provides elo information on a specific player. Plain text.
    """
    # UTC epoch
    now = timegm(datetime.datetime.utcnow().timetuple())

    # All player_info fields are converted into JSON-formattable dictionaries
    elo_info = player_elo_info_data(request)

    # this is a plain text response, if we don't do this here then
    # Pyramid will assume html
    request.response.content_type = 'text/plain'

    return {
        'version':          1,
        'now':              now,
        'hashkey':          elo_info['hashkey'],
        'player':           elo_info['player'],
        'elos':             elo_info['elos'],
    }


def player_captimes_data(request):
    player_id = int(request.matchdict['player_id'])
    if player_id <= 2:
        player_id = -1;

    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    PlayerCaptimes = namedtuple('PlayerCaptimes', ['fastest_cap',
            'create_dt', 'create_dt_epoch', 'create_dt_fuzzy',
            'player_id', 'game_id', 'map_id', 'map_name', 'server_id', 'server_name'])

    player = DBSession.query(Player).filter_by(player_id=player_id).one()

    #pct_q = DBSession.query('fastest_cap', 'create_dt', 'player_id', 'game_id', 'map_id',
    #            'map_name', 'server_id', 'server_name').\
    #        from_statement(
    #            "SELECT ct.fastest_cap, "
    #                   "ct.create_dt, "
    #                   "ct.player_id, "
    #                   "ct.game_id, "
    #                   "ct.map_id, "
    #                   "m.name map_name, "
    #                   "g.server_id, "
    #                   "s.name server_name "
    #            "FROM   player_map_captimes ct, "
    #                   "games g, "
    #                   "maps m, "
    #                   "servers s "
    #            "WHERE  ct.player_id = :player_id "
    #              "AND  g.game_id = ct.game_id "
    #              "AND  g.server_id = s.server_id "
    #              "AND  m.map_id = ct.map_id "
    #            #"ORDER  BY ct.fastest_cap "
    #            "ORDER  BY ct.create_dt desc"
    #        ).params(player_id=player_id)

    try:
        pct_q = DBSession.query(PlayerCaptime.fastest_cap, PlayerCaptime.create_dt,
                PlayerCaptime.player_id, PlayerCaptime.game_id, PlayerCaptime.map_id,
                Map.name.label('map_name'), Game.server_id, Server.name.label('server_name')).\
                filter(PlayerCaptime.player_id==player_id).\
                filter(PlayerCaptime.game_id==Game.game_id).\
                filter(PlayerCaptime.map_id==Map.map_id).\
                filter(Game.server_id==Server.server_id).\
                order_by(expr.desc(PlayerCaptime.create_dt))

        player_captimes = Page(pct_q, current_page, items_per_page=20, url=page_url)

        # replace the items in the canned pagination class with more rich ones
        player_captimes.items = [PlayerCaptimes(
                fastest_cap=row.fastest_cap,
                create_dt=row.create_dt,
                create_dt_epoch=timegm(row.create_dt.timetuple()),
                create_dt_fuzzy=pretty_date(row.create_dt),
                player_id=row.player_id,
                game_id=row.game_id,
                map_id=row.map_id,
                map_name=row.map_name,
                server_id=row.server_id,
                server_name=row.server_name
                ) for row in player_captimes.items]

    except Exception as e:
        player = None
        player_captimes = None

    return {
            'player_id':player_id,
            'player':player,
            'captimes':player_captimes,
            #'player_url':request.route_url('player_info', id=player_id),
        }


def player_captimes(request):
    return player_captimes_data(request)


def player_captimes_json(request):
    return player_captimes_data(request)


def player_weaponstats_data_json(request):
    player_id = int(request.matchdict["id"])
    if player_id <= 2:
        player_id = -1;

    game_type_cd = request.params.get("game_type", None)
    if game_type_cd == "overall":
        game_type_cd = None

    limit = 20
    if request.params.has_key("limit"):
        limit = int(request.params["limit"])

        if limit < 0:
            limit = 20
        if limit > 50:
            limit = 50


    # the game_ids of the most recently played ones 
    # of the given game type is used for a subquery
    games_list = DBSession.query(Game.game_id).\
            filter(Game.players.contains([player_id]))

    if game_type_cd is not None:
        games_list = games_list.filter(Game.game_type_cd == game_type_cd)

    games_list = games_list.order_by(Game.game_id.desc()).limit(limit)

    weapon_stats_raw = DBSession.query(PlayerWeaponStat).\
        filter(PlayerWeaponStat.player_id == player_id).\
        filter(PlayerWeaponStat.game_id.in_(games_list)).\
        all()

    games_to_weapons = {}
    weapons_used = {}
    sum_avgs = {}
    for ws in weapon_stats_raw:
        if ws.game_id not in games_to_weapons:
            games_to_weapons[ws.game_id] = [ws.weapon_cd]
        else:
            games_to_weapons[ws.game_id].append(ws.weapon_cd)

        weapons_used[ws.weapon_cd] = weapons_used.get(ws.weapon_cd, 0) + 1
        sum_avgs[ws.weapon_cd] = sum_avgs.get(ws.weapon_cd, 0) + float(ws.hit)/float(ws.fired)

    # Creating zero-valued weapon stat entries for games where a weapon was not
    # used in that game, but was used in another game for the set. This makes 
    # the charts look smoother
    for game_id in games_to_weapons.keys():
        for weapon_cd in set(weapons_used.keys()) - set(games_to_weapons[game_id]):
            weapon_stats_raw.append(PlayerWeaponStat(player_id=player_id,
                game_id=game_id, weapon_cd=weapon_cd))

    # averages for the weapons used in the range
    avgs = {}
    for w in weapons_used.keys():
        avgs[w] = round(sum_avgs[w]/float(weapons_used[w])*100, 2)

    weapon_stats_raw = sorted(weapon_stats_raw, key = lambda x: x.game_id)
    games            = sorted(games_to_weapons.keys())
    weapon_stats     = [ws.to_dict() for ws in weapon_stats_raw]

    return {
        "weapon_stats": weapon_stats,
        "weapons_used": weapons_used.keys(),
        "games": games,
        "averages": avgs,
    }

