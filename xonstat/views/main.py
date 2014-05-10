import logging
import sqlalchemy as sa
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
from beaker.cache import cache_regions, cache_region
from collections import namedtuple
from datetime import datetime, timedelta
from pyramid.response import Response
from xonstat.models import *
from xonstat.util import *
from xonstat.views.helpers import RecentGame, recent_games_q
from webhelpers.paginate import Page


log = logging.getLogger(__name__)


@cache_region('hourly_term')
def get_summary_stats(request, cutoff_days=None):
    """
    Gets the following aggregate statistics about the past cutoff_days days:
        - the number of active players
        - the number of games per game type
    If cutoff_days is None, the above stats are calculated for all time.

    This information is then summarized into a string which is passed
    directly to the template.
    """
    try:
        if cutoff_days is not None:
            # only games played during this range are considered
            right_now = datetime.now()
            cutoff_dt = right_now - timedelta(days=cutoff_days)

            games = DBSession.query(Game.game_type_cd, func.count()).\
                filter(expr.between(Game.create_dt, cutoff_dt, right_now)).\
                group_by(Game.game_type_cd).\
                order_by(expr.desc(func.count())).all()

            active_players = DBSession.query(func.count(sa.distinct(PlayerGameStat.player_id))).\
                filter(PlayerGameStat.player_id > 2).\
                filter(expr.between(PlayerGameStat.create_dt, cutoff_dt, right_now)).\
                one()[0]
        else:
            games = DBSession.query(Game.game_type_cd, func.count()).\
                group_by(Game.game_type_cd).\
                order_by(expr.desc(func.count())).all()

            active_players = DBSession.query(func.count(sa.distinct(PlayerGameStat.player_id))).\
                filter(PlayerGameStat.player_id > 2).\
                one()[0]

        total_games = 0
        for total in games:
            total_games += total[1]

        i = 1
        other_games = 0
        for total in games:
            if i > 5:
                other_games += total[1]
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
            in_paren = "; ".join(["{:2,d} {}".format(
                g[1],
                "<a href='{}'>{}</a>".format(
                    request.route_url("game_index", _query={'type':g[0]}),
                    g[0]
                )
            ) for g in games[:5]])

            if len(games) > 5:
                in_paren += "; {:2,d} other".format(other_games)

            stat_line = "{:2,d} active players and {:2,d} games ({})".format(
                active_players,
                total_games,
                in_paren
            )

    except Exception as e:
        stat_line = None

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


def top_players_by_time_q(cutoff_days):
    """
    Query for the top players by the amount of time played during a date range.

    Games older than cutoff_days days old are ignored.
    """

    # only games played during this range are considered
    right_now = datetime.utcnow()
    cutoff_dt = right_now - timedelta(days=cutoff_days)

    top_players_q = DBSession.query(Player.player_id, Player.nick,
            func.sum(PlayerGameStat.alivetime)).\
            filter(Player.player_id == PlayerGameStat.player_id).\
            filter(Player.player_id > 2).\
            filter(expr.between(PlayerGameStat.create_dt, cutoff_dt, right_now)).\
            order_by(expr.desc(func.sum(PlayerGameStat.alivetime))).\
            group_by(Player.nick).\
            group_by(Player.player_id)

    return top_players_q


@cache_region('hourly_term')
def get_top_players_by_time(cutoff_days):
    """
    The top players by the amount of time played during a date range.

    Games older than cutoff_days days old are ignored.
    """
    # how many to retrieve
    count = 10

    # only games played during this range are considered
    right_now = datetime.utcnow()
    cutoff_dt = right_now - timedelta(days=cutoff_days)

    top_players_q = top_players_by_time_q(cutoff_days)

    top_players = top_players_q.limit(count).all()

    top_players = [(player_id, html_colors(nick), score) \
            for (player_id, nick, score) in top_players]

    return top_players


def top_servers_by_players_q(cutoff_days):
    """
    Query to get the top servers by the amount of players active
    during a date range.

    Games older than cutoff_days days old are ignored.
    """
    # only games played during this range are considered
    right_now = datetime.utcnow()
    cutoff_dt = right_now - timedelta(days=cutoff_days)

    top_servers_q = DBSession.query(Server.server_id, Server.name,
        func.count()).\
        filter(Game.server_id==Server.server_id).\
        filter(expr.between(Game.create_dt, cutoff_dt, right_now)).\
        order_by(expr.desc(func.count(Game.game_id))).\
        group_by(Server.server_id).\
        group_by(Server.name)

    return top_servers_q


@cache_region('hourly_term')
def get_top_servers_by_players(cutoff_days):
    """
    The top servers by the amount of players active during a date range.

    Games older than cutoff_days days old are ignored.
    """
    # how many to retrieve
    count = 10

    top_servers = top_servers_by_players_q(cutoff_days).limit(count).all()

    return top_servers


def top_maps_by_times_played_q(cutoff_days):
    """
    Query to retrieve the top maps by the amount of times it was played
    during a date range.

    Games older than cutoff_days days old are ignored.
    """
    # only games played during this range are considered
    right_now = datetime.utcnow()
    cutoff_dt = right_now - timedelta(days=cutoff_days)

    top_maps_q = DBSession.query(Game.map_id, Map.name,
            func.count()).\
            filter(Map.map_id==Game.map_id).\
            filter(expr.between(Game.create_dt, cutoff_dt, right_now)).\
            order_by(expr.desc(func.count())).\
            group_by(Game.map_id).\
            group_by(Map.name)

    return top_maps_q


@cache_region('hourly_term')
def get_top_maps_by_times_played(cutoff_days):
    """
    The top maps by the amount of times it was played during a date range.

    Games older than cutoff_days days old are ignored.
    """
    # how many to retrieve
    count = 10

    top_maps = top_maps_by_times_played_q(cutoff_days).limit(count).all()

    return top_maps


def _main_index_data(request):
    try:
        leaderboard_lifetime = int(
                request.registry.settings['xonstat.leaderboard_lifetime'])
    except:
        leaderboard_lifetime = 30

    leaderboard_count = 10
    recent_games_count = 20

    # summary statistics for the tagline
    stat_line = get_summary_stats(request, None)
    day_stat_line = get_summary_stats(request, 1)


    # the three top ranks tables
    ranks = []
    for gtc in ['duel', 'ctf', 'dm', 'tdm']:
        rank = get_ranks(gtc)
        if len(rank) != 0:
            ranks.append(rank)

    right_now = datetime.utcnow()
    back_then = datetime.utcnow() - timedelta(days=leaderboard_lifetime)

    # top players by playing time
    top_players = get_top_players_by_time(leaderboard_lifetime)

    # top servers by number of total players played
    top_servers = get_top_servers_by_players(leaderboard_lifetime)

    # top maps by total times played
    top_maps = get_top_maps_by_times_played(leaderboard_lifetime)

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
    mainindex_data =  _main_index_data(request)

    # FIXME: code clone, should get these from _main_index_data
    leaderboard_count = 10
    recent_games_count = 20

    for i in range(leaderboard_count-len(mainindex_data['top_players'])):
        mainindex_data['top_players'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(mainindex_data['top_servers'])):
        mainindex_data['top_servers'].append(('-', '-', '-'))

    for i in range(leaderboard_count-len(mainindex_data['top_maps'])):
        mainindex_data['top_maps'].append(('-', '-', '-'))

    return mainindex_data


def main_index_json(request):
    """
    JSON output of the main page information.
    """
    return [{'status':'not implemented'}]


def top_players_by_time(request):
    current_page = request.params.get('page', 1)

    cutoff_days = int(request.registry.settings.\
        get('xonstat.leaderboard_lifetime', 30))

    top_players_q = top_players_by_time_q(cutoff_days)

    top_players = Page(top_players_q, current_page, items_per_page=25, url=page_url)

    top_players.items = [(player_id, html_colors(nick), score) \
            for (player_id, nick, score) in top_players.items]

    return {'top_players':top_players}


def top_servers_by_players(request):
    current_page = request.params.get('page', 1)

    cutoff_days = int(request.registry.settings.\
        get('xonstat.leaderboard_lifetime', 30))

    top_servers_q = top_servers_by_players_q(cutoff_days)

    top_servers = Page(top_servers_q, current_page, items_per_page=25, url=page_url)

    return {'top_servers':top_servers}


def top_maps_by_times_played(request):
    current_page = request.params.get('page', 1)

    cutoff_days = int(request.registry.settings.\
        get('xonstat.leaderboard_lifetime', 30))

    top_maps_q = top_maps_by_times_played_q(cutoff_days)

    top_maps = Page(top_maps_q, current_page, items_per_page=25, url=page_url)

    return {'top_maps':top_maps}
