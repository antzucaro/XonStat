import logging
from collections import OrderedDict

from pyramid import httpexceptions
from sqlalchemy.orm.exc import *
from webhelpers.paginate import Page
from xonstat.models import DBSession, Server, Map, Game, PlayerGameStat, PlayerWeaponStat
from xonstat.models import PlayerGameFragMatrix, TeamGameStat, PlayerRank, GameType, Weapon
from xonstat.util import page_url
from xonstat.views.helpers import RecentGame, recent_games_q

log = logging.getLogger(__name__)


def _game_info_data(request):
    game_id = int(request.matchdict['id'])

    # show an extra column if "show_elo" is a GET parameter
    show_elo = bool(request.params.get("show_elo", False))

    try:
        (game, server, map, gametype) = DBSession.query(Game, Server, Map, GameType)\
            .filter(Game.game_id == game_id)\
            .filter(Game.server_id == Server.server_id)\
            .filter(Game.map_id == Map.map_id)\
            .filter(Game.game_type_cd == GameType.game_type_cd)\
            .one()

        pgstats = DBSession.query(PlayerGameStat)\
            .filter(PlayerGameStat.game_id == game_id)\
            .order_by(PlayerGameStat.scoreboardpos)\
            .order_by(PlayerGameStat.score)\
            .all()

        # Really old games don't have latency sent, so we have to check. If at
        # least one player has a latency value, we'll show the ping column.
        show_latency = False
        for pgstat in pgstats:
            if pgstat.avg_latency is not None:
                show_latency = True
                break

        q = DBSession.query(TeamGameStat).filter(TeamGameStat.game_id == game_id)

        if game.game_type_cd == 'ctf':
            q = q.order_by(TeamGameStat.caps.desc())
        elif game.game_type_cd == 'ca':
            q = q.order_by(TeamGameStat.rounds.desc())

        q = q.order_by(TeamGameStat.score.desc())

        tgstats = q.all()

        stats_by_team = OrderedDict()
        for pgstat in pgstats:
            if pgstat.team not in stats_by_team.keys():
                stats_by_team[pgstat.team] = []
            stats_by_team[pgstat.team].append(pgstat)

        captimes = []
        if game.game_type_cd == 'ctf':
            for pgstat in pgstats:
                if pgstat.fastest is not None:
                    captimes.append(pgstat)
            captimes = sorted(captimes, key=lambda x:x.fastest)

        pwstats = {}
        for (pwstat, weapon) in DBSession.query(PlayerWeaponStat, Weapon)\
                .filter(PlayerWeaponStat.game_id == game_id)\
                .filter(PlayerWeaponStat.weapon_cd == Weapon.weapon_cd)\
                .order_by(PlayerWeaponStat.actual.desc())\
                .all():
                    if pwstat.player_game_stat_id not in pwstats:
                        pwstats[pwstat.player_game_stat_id] = []

                    pwstats[pwstat.player_game_stat_id].append((weapon.descr,
                        weapon.weapon_cd, pwstat.actual, pwstat.max,
                        pwstat.hit, pwstat.fired, pwstat.frags))

        frag_matrix = DBSession.query(PlayerGameFragMatrix)\
            .filter(PlayerGameFragMatrix.game_id == game_id)\
            .all()

        matrix_by_pgstat_id = {e.player_game_stat_id: e for e in frag_matrix}
        if len(matrix_by_pgstat_id):
            show_frag_matrix = True
        else:
            show_frag_matrix = False

    except NoResultFound as e:
        raise httpexceptions.HTTPNotFound("Could not find that game!")

    except Exception as e:
        raise e

    return {
        'game': game,
        'server': server,
        'map': map,
        'gametype': gametype,
        'pgstats': pgstats,
        'tgstats': tgstats,
        'pwstats': pwstats,
        'captimes': captimes,
        'show_elo': show_elo,
        'show_latency': show_latency,
        'stats_by_team': stats_by_team,
        'show_frag_matrix': show_frag_matrix,
        'matrix_by_pgstat_id': matrix_by_pgstat_id,
    }


def game_info(request):
    """
    List the game stats (scoreboard) for a particular game. Paginated.
    """
    return _game_info_data(request)


def game_info_json(request):
    """
    List the game stats (scoreboard) for a particular game. Paginated. JSON.
    """
    data = _game_info_data(request)

    # convert pwstats into a more JSON-friendly format
    pwstats = {}
    for pgstat_id, pwstat_list in data["pwstats"].items():
        l = []
        for pwstat in pwstat_list:
            l.append({
                "player_game_stat_id": pgstat_id,
                "weapon_cd": pwstat[1],
                "actual": pwstat[2],
                "max": pwstat[3],
                "hit": pwstat[4],
                "fired": pwstat[5],
                "frags": pwstat[6],
            })

        pwstats[int(pgstat_id)] = l

    return {
        "game": data["game"].to_dict(),
        "server": data["server"].to_dict(),
        "map": data["map"].to_dict(),
        'pgstats': [pgstat.to_dict() for pgstat in data["pgstats"]],
        'pwstats': pwstats,
        'tgstats': [tgstat.to_dict() for tgstat in data["tgstats"]],
        # 'captimes': [captime.to_dict() for captime in data["captimes"]],
    }


def _rank_index_data(request):
    current_page = request.params.get("page", 1)

    # game type whitelist
    game_types_allowed = ["ca", "ctf", "dm", "duel", "ft", "ka", "tdm"]

    game_type_cd = request.matchdict['game_type_cd']
    if game_type_cd not in game_types_allowed:
        raise httpexceptions.HTTPNotFound()

    ranks_q = DBSession.query(PlayerRank).\
            filter(PlayerRank.game_type_cd==game_type_cd).\
            order_by(PlayerRank.rank)

    game_type = DBSession.query(GameType).\
            filter(GameType.game_type_cd == game_type_cd).one()

    ranks = Page(ranks_q, current_page, url=page_url)

    if len(ranks) == 0:
        ranks = None

    return {
            'ranks':ranks,
            'game_type_cd':game_type_cd,
            'game_type': game_type,
           }


def rank_index(request):
    """
    Provide a list of gametype ranks, paginated.
    """
    return _rank_index_data(request)


def rank_index_json(request):
    """
    Provide a list of gametype ranks, paginated. JSON.
    """
    return [{'status':'not implemented'}]


def game_finder_data(request):
    if request.params.has_key('page'):
        current_page = request.params['page']
    else:
        current_page = 1

    query = {}

    server_id, map_id, player_id = None, None, None
    game_type_cd, start_game_id, end_game_id = None, None, None
    game_type_descr = None

    # these become WHERE clauses when present
    if request.params.has_key('server_id'):
        server_id = request.params['server_id']
        query['server_id'] = server_id

    if request.params.has_key('map_id'):
        map_id = request.params['map_id']
        query['map_id'] = map_id

    if request.params.has_key('player_id'):
        player_id = request.params['player_id']
        query['player_id'] = player_id

    if request.params.has_key('start_game_id'):
        start_game_id = request.params['start_game_id']
        query['start_game_id'] = start_game_id

    if request.params.has_key('end_game_id'):
        end_game_id = request.params['end_game_id']
        query['end_game_id'] = end_game_id

    if request.params.has_key('type'):
        game_type_cd = request.params['type']
        query['type'] = game_type_cd
        try:
            game_type_descr = DBSession.query(GameType.descr).\
                filter(GameType.game_type_cd == game_type_cd).\
                one()[0]
        except Exception as e:
            game_type_cd = None

    rgs_q = recent_games_q(server_id=server_id, map_id=map_id,
            player_id=player_id, game_type_cd=game_type_cd,
            start_game_id=start_game_id, end_game_id=end_game_id)

    try:
        recent_games = [RecentGame(row) for row in rgs_q.limit(20).all()]

        if len(recent_games) > 0:
            query['start_game_id'] = recent_games[-1].game_id + 1

        # build the list of links for the stripe across the top
        game_type_links = []

        # clear out the game_id window
        gt_query = query.copy()
        if 'start_game_id' in gt_query:
            del gt_query['start_game_id']
        if 'end_game_id' in gt_query:
            del gt_query['end_game_id']

        for gt in ('overall','duel','ctf','dm','tdm','ca','kh','ft',
                'lms','as','dom','nb','cts','rc'):
            gt_query['type'] = gt
            url = request.route_url("game_index", _query=gt_query)
            game_type_links.append((gt, url))

    except:
        raise httpexceptions.HTTPBadRequest("Malformed Query")

    return {
            'recent_games':recent_games,
            'query':query,
            'game_type_cd':game_type_cd,
            'game_type_links':game_type_links,
           }


def game_finder(request):
    """
    Provide a list of recent games with an advanced filter.
    """
    return game_finder_data(request)


def game_finder_json(request):
    """
    Provide a list of recent games in JSON format.
    """
    data = game_finder_data(request)
    return [rg.to_dict() for rg in data["recent_games"]]
