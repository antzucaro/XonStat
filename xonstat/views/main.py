import logging
from datetime import datetime, timedelta

from beaker.cache import cache_region
from xonstat.models import DBSession, PlayerRank, ActivePlayer, ActiveServer, ActiveMap
from xonstat.views.helpers import RecentGame, recent_games_q

log = logging.getLogger(__name__)


@cache_region('hourly_term')
def get_summary_stats(scope="all"):
    """
    Gets the following aggregate statistics according to the provided scope:

        - the number of active players
        - the number of games per game type

    Scope can be "all" or "day".

    The fetched information is summarized into a string which is passed
    directly to the template.
    """
    if scope not in ["all", "day"]:
        scope = "all"

    try:
        ss = DBSession.query("num_players", "game_type_cd", "num_games").\
                from_statement(
                        "SELECT num_players, game_type_cd, num_games "
                        "FROM summary_stats_mv "
                        "WHERE scope = :scope "
                        "ORDER BY sort_order "
                ).params(scope=scope).all()

        i = 1
        total_games = 0
        other_games = 0
        for row in ss:
            # the number of players is constant in each row
            total_players = row.num_players

            total_games += row.num_games

            # we can't show all game types on the single summary line, so any
            # past the fifth one will get bundled in to an "other" count
            if i > 5:
                other_games += row.num_games

            i += 1

        # don't send anything if we don't have any activity
        if total_games == 0:
            stat_line = None
        else:
        # This is ugly because we're doing template-like stuff within the
        # view code. The alternative isn't any better, though: we would
        # have to assemble the string inside the template by using a Python
        # code block. For now I'll leave it like this since it is the lesser
        # of two evils IMO.
        # Also we need to hard-code the URL structure in here to allow caching,
        # which also sucks.
            in_paren = "; ".join(["{:2,d} {}".format(
                g.num_games,
                "<a href='/games?type={0}'>{0}</a>".format(g.game_type_cd)
            ) for g in ss[:5]])

            if other_games > 0:
                in_paren += "; {:2,d} other".format(other_games)

            stat_line = "{:2,d} players and {:2,d} games ({})".format(
                total_players,
                total_games,
                in_paren
            )

    except Exception as e:
        stat_line = None
        raise e

    return stat_line


@cache_region('hourly_term')
def get_ranks(game_type_cd):
    """
    Gets a set number of the top-ranked people for the specified game_type_cd.

    The game_type_cd parameter is the type to fetch. Currently limited to
    duel, dm, ctf, and tdm.
    """
    # how many ranks we want to fetch
    leaderboard_count = 10

    # only a few game modes are actually ranked
    if game_type_cd not in 'duel' 'dm' 'ctf' 'tdm':
        return None

    ranks = DBSession.query(PlayerRank).\
            filter(PlayerRank.game_type_cd==game_type_cd).\
            order_by(PlayerRank.rank).\
            limit(leaderboard_count).all()

    return ranks


@cache_region('hourly_term')
def get_top_players_by_time(limit=None, start=None):
    """
    The top players by the amount of time played during a date range.
    """
    q = DBSession.query(ActivePlayer)

    if start is not None:
        q = q.filter(ActivePlayer.sort_order >= start)

    q = q.order_by(ActivePlayer.sort_order)

    if limit is not None:
        q = q.limit(limit)

    return q.all()


@cache_region('hourly_term')
def get_top_servers_by_play_time(limit=None, start=None):
    """
    The top servers by the cumulative amount of time played on them during a given interval.
    """
    q = DBSession.query(ActiveServer)

    if start is not None:
        q = q.filter(ActiveServer.sort_order >= start)

    q = q.order_by(ActiveServer.sort_order)

    if limit is not None:
        q = q.limit(limit)

    return q.all()


@cache_region('hourly_term')
def get_top_maps_by_games(limit=None, start=None):
    """
    The top maps by the number of games played during a date range.
    """
    q = DBSession.query(ActiveMap)

    if start is not None:
        q = q.filter(ActiveMap.sort_order >= start)

    q = q.order_by(ActiveMap.sort_order)

    if limit is not None:
        q = q.limit(limit)

    return q.all()


def _main_index_data(request):
    try:
        leaderboard_lifetime = int(
                request.registry.settings['xonstat.leaderboard_lifetime'])
    except:
        leaderboard_lifetime = 30

    leaderboard_count = 10
    recent_games_count = 20

    # summary statistics for the tagline
    stat_line = get_summary_stats("all")
    day_stat_line = get_summary_stats("day")


    # the three top ranks tables
    ranks = []
    for gtc in ['duel', 'ctf', 'dm', 'tdm']:
        rank = get_ranks(gtc)
        if len(rank) != 0:
            ranks.append(rank)

    right_now = datetime.utcnow()
    back_then = datetime.utcnow() - timedelta(days=leaderboard_lifetime)

    # top players by playing time
    top_players = get_top_players_by_time(10)

    # top servers by number of games
    top_servers = get_top_servers_by_play_time(10)

    # top maps by total times played
    top_maps = get_top_maps_by_games(10)

    # recent games played in descending order
    rgs = recent_games_q(cutoff=back_then).limit(recent_games_count).all()
    recent_games = [RecentGame(row) for row in rgs]

    return {'top_players':top_players,
            'top_servers':top_servers,
            'top_maps':top_maps,
            'recent_games':recent_games,
            'ranks':ranks,
            'stat_line':stat_line,
            'day_stat_line':day_stat_line,
            }


def main_index(request):
    """
    Display the main page information.
    """
    return _main_index_data(request)


def main_index_json(request):
    """
    JSON output of the main page information.
    """
    return [{'status':'not implemented'}]


def top_players_index(request):
    try:
        start = int(request.params.get('start', None))
    except:
        start = None

    top_players = get_top_players_by_time(20, start)

    # building a query string
    query = {}
    if len(top_players) > 1:
        query['start'] = top_players[-1].sort_order + 1

    return {
            'top_players':top_players,
            'query':query,
            'start':start,
            }


def top_servers_index(request):
    try:
        start = int(request.params.get('start', None))
    except:
        start = None

    top_servers = get_top_servers_by_play_time(20, start)

    # building a query string
    query = {}
    if len(top_servers) > 1:
        query['start'] = top_servers[-1].sort_order + 1

    return {
            'top_servers':top_servers,
            'query':query,
            'start':start,
            }


def top_maps_index(request):
    try:
        start = int(request.params.get('start', None))
    except:
        start = None

    top_maps = get_top_maps_by_games(20, start)

    # building a query string
    query = {}
    if len(top_maps) > 1:
        query['start'] = top_maps[-1].sort_order + 1

    return {
            'top_maps':top_maps,
            'query':query,
            'start':start,
            }
