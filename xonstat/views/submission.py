import calendar
import datetime
import logging
import re

import pyramid.httpexceptions
from sqlalchemy import Sequence
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from xonstat.elo import EloProcessor
from xonstat.models import DBSession, Server, Map, Game, PlayerGameStat, PlayerWeaponStat
from xonstat.models import PlayerRank, PlayerCaptime
from xonstat.models import TeamGameStat, PlayerGameAnticheat, Player, Hashkey, PlayerNick
from xonstat.util import strip_colors, qfont_decode, verify_request, weapon_map

log = logging.getLogger(__name__)


def parse_stats_submission(body):
    """
    Parses the POST request body for a stats submission
    """
    # storage vars for the request body
    game_meta = {}
    events = {}
    players = []
    teams = []

    # we're not in either stanza to start
    in_P = in_Q = False

    for line in body.split('\n'):
        try:
            (key, value) = line.strip().split(' ', 1)

            # Server (S) and Nick (n) fields can have international characters.
            if key in 'S' 'n':
                value = unicode(value, 'utf-8')

            if key not in 'P' 'Q' 'n' 'e' 't' 'i':
                game_meta[key] = value

            if key == 'Q' or key == 'P':
                #log.debug('Found a {0}'.format(key))
                #log.debug('in_Q: {0}'.format(in_Q))
                #log.debug('in_P: {0}'.format(in_P))
                #log.debug('events: {0}'.format(events))

                # check where we were before and append events accordingly
                if in_Q and len(events) > 0:
                    #log.debug('creating a team (Q) entry')
                    teams.append(events)
                    events = {}
                elif in_P and len(events) > 0:
                    #log.debug('creating a player (P) entry')
                    players.append(events)
                    events = {}

                if key == 'P':
                    #log.debug('key == P')
                    in_P = True
                    in_Q = False
                elif key == 'Q':
                    #log.debug('key == Q')
                    in_P = False
                    in_Q = True

                events[key] = value

            if key == 'e':
                (subkey, subvalue) = value.split(' ', 1)
                events[subkey] = subvalue
            if key == 'n':
                events[key] = value
            if key == 't':
                events[key] = value
        except:
            # no key/value pair - move on to the next line
            pass

    # add the last entity we were working on
    if in_P and len(events) > 0:
        players.append(events)
    elif in_Q and len(events) > 0:
        teams.append(events)

    return (game_meta, players, teams)


def is_blank_game(gametype, players):
    """Determine if this is a blank game or not. A blank game is either:

    1) a match that ended in the warmup stage, where accuracy events are not
    present (for non-CTS games)

    2) a match in which no player made a positive or negative score AND was
    on the scoreboard

    ... or for CTS, which doesn't record accuracy events

    1) a match in which no player made a fastest lap AND was
    on the scoreboard

    ... or for NB, in which not all maps have weapons

    1) a match in which no player made a positive or negative score
    """
    r = re.compile(r'acc-.*-cnt-fired')
    flg_nonzero_score = False
    flg_acc_events = False
    flg_fastest_lap = False

    for events in players:
        if is_real_player(events) and played_in_game(events):
            for (key,value) in events.items():
                if key == 'scoreboard-score' and value != 0:
                    flg_nonzero_score = True
                if r.search(key):
                    flg_acc_events = True
                if key == 'scoreboard-fastest':
                    flg_fastest_lap = True

    if gametype == 'cts':
        return not flg_fastest_lap
    elif gametype == 'nb':
        return not flg_nonzero_score
    else:
        return not (flg_nonzero_score and flg_acc_events)


def get_remote_addr(request):
    """Get the Xonotic server's IP address"""
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For']
    else:
        return request.remote_addr


def is_supported_gametype(gametype, version):
    """Whether a gametype is supported or not"""
    is_supported = False

    # if the type can be supported, but with version constraints, uncomment
    # here and add the restriction for a specific version below
    supported_game_types = (
            'as',
            'ca',
            # 'cq',
            'ctf',
            'cts',
            'dm',
            'dom',
            'ft', 'freezetag',
            'ka', 'keepaway',
            'kh',
            # 'lms',
            'nb', 'nexball',
            # 'rc',
            'rune',
            'tdm',
        )

    if gametype in supported_game_types:
        is_supported = True
    else:
        is_supported = False

    # some game types were buggy before revisions, thus this additional filter
    if gametype == 'ca' and version <= 5:
        is_supported = False

    return is_supported


def do_precondition_checks(request, game_meta, raw_players):
    """Precondition checks for ALL gametypes.
       These do not require a database connection."""
    if not has_required_metadata(game_meta):
        msg = "Missing required game metadata"
        log.debug(msg)
        raise pyramid.httpexceptions.HTTPUnprocessableEntity(
            body=msg,
            content_type="text/plain"
        )

    try:
        version = int(game_meta['V'])
    except:
        msg = "Invalid or incorrect game metadata provided"
        log.debug(msg)
        raise pyramid.httpexceptions.HTTPUnprocessableEntity(
            body=msg,
            content_type="text/plain"
        )

    if not is_supported_gametype(game_meta['G'], version):
        msg = "Unsupported game type ({})".format(game_meta['G'])
        log.debug(msg)
        raise pyramid.httpexceptions.HTTPOk(
            body=msg,
            content_type="text/plain"
        )

    if not has_minimum_real_players(request.registry.settings, raw_players):
        msg = "Not enough real players"
        log.debug(msg)
        raise pyramid.httpexceptions.HTTPOk(
            body=msg,
            content_type="text/plain"
        )

    if is_blank_game(game_meta['G'], raw_players):
        msg = "Blank game"
        log.debug(msg)
        raise pyramid.httpexceptions.HTTPOk(
            body=msg,
            content_type="text/plain"
        )


def is_real_player(events):
    """
    Determines if a given set of events correspond with a non-bot
    """
    if not events['P'].startswith('bot'):
        return True
    else:
        return False


def played_in_game(events):
    """
    Determines if a given set of player events correspond with a player who
    played in the game (matches 1 and scoreboardvalid 1)
    """
    if 'matches' in events and 'scoreboardvalid' in events:
        return True
    else:
        return False


def num_real_players(player_events):
    """
    Returns the number of real players (those who played
    and are on the scoreboard).
    """
    real_players = 0

    for events in player_events:
        if is_real_player(events) and played_in_game(events):
            real_players += 1

    return real_players


def has_minimum_real_players(settings, player_events):
    """
    Determines if the collection of player events has enough "real" players
    to store in the database. The minimum setting comes from the config file
    under the setting xonstat.minimum_real_players.
    """
    flg_has_min_real_players = True

    try:
        minimum_required_players = int(
                settings['xonstat.minimum_required_players'])
    except:
        minimum_required_players = 2

    real_players = num_real_players(player_events)

    if real_players < minimum_required_players:
        flg_has_min_real_players = False

    return flg_has_min_real_players


def has_required_metadata(metadata):
    """
    Determines if a give set of metadata has enough data to create a game,
    server, and map with.
    """
    flg_has_req_metadata = True

    if 'G' not in metadata or\
        'M' not in metadata or\
        'I' not in metadata or\
        'S' not in metadata:
            flg_has_req_metadata = False

    return flg_has_req_metadata


def should_do_weapon_stats(game_type_cd):
    """True of the game type should record weapon stats. False otherwise."""
    if game_type_cd in 'cts':
        return False
    else:
        return True


def gametype_elo_eligible(game_type_cd):
    """True of the game type should process Elos. False otherwise."""
    elo_game_types = ('duel', 'dm', 'ca', 'ctf', 'tdm', 'ka', 'ft')

    if game_type_cd in elo_game_types:
        return True
    else:
        return False


def register_new_nick(session, player, new_nick):
    """
    Change the player record's nick to the newly found nick. Store the old
    nick in the player_nicks table for that player.

    session - SQLAlchemy database session factory
    player - player record whose nick is changing
    new_nick - the new nickname
    """
    # see if that nick already exists
    stripped_nick = strip_colors(qfont_decode(player.nick))
    try:
        player_nick = session.query(PlayerNick).filter_by(
            player_id=player.player_id, stripped_nick=stripped_nick).one()
    except NoResultFound, e:
        # player_id/stripped_nick not found, create one
        # but we don't store "Anonymous Player #N"
        if not re.search('^Anonymous Player #\d+$', player.nick):
            player_nick = PlayerNick()
            player_nick.player_id = player.player_id
            player_nick.stripped_nick = stripped_nick
            player_nick.nick = player.nick
            session.add(player_nick)

    # We change to the new nick regardless
    player.nick = new_nick
    player.stripped_nick = strip_colors(qfont_decode(new_nick))
    session.add(player)


def update_fastest_cap(session, player_id, game_id, map_id, captime, mod):
    """
    Check the fastest cap time for the player and map. If there isn't
    one, insert one. If there is, check if the passed time is faster.
    If so, update!
    """
    # we don't record fastest cap times for bots or anonymous players
    if player_id <= 2:
        return

    # see if a cap entry exists already
    # then check to see if the new captime is faster
    try:
        cur_fastest_cap = session.query(PlayerCaptime).filter_by(
            player_id=player_id, map_id=map_id, mod=mod).one()

        # current captime is faster, so update
        if captime < cur_fastest_cap.fastest_cap:
            cur_fastest_cap.fastest_cap = captime
            cur_fastest_cap.game_id = game_id
            cur_fastest_cap.create_dt = datetime.datetime.utcnow()
            session.add(cur_fastest_cap)

    except NoResultFound, e:
        # none exists, so insert
        cur_fastest_cap = PlayerCaptime(player_id, game_id, map_id, captime,
                mod)
        session.add(cur_fastest_cap)
        session.flush()


def update_server(server, name, hashkey, ip_addr, port, revision, impure_cvars):
    """
    Updates the server in the given DB session, if needed.

    :param server: The found server instance.
    :param name: The incoming server name.
    :param hashkey: The incoming server hashkey.
    :param ip_addr: The incoming server IP address.
    :param port: The incoming server port.
    :param revision: The incoming server revision.
    :param impure_cvars: The incoming number of impure server cvars.
    :return: bool
    """
    # ensure the two int attributes are actually ints
    try:
        port = int(port)
    except:
        port = None

    try:
        impure_cvars = int(impure_cvars)
    except:
        impure_cvars = 0

    updated = False
    if name and server.name != name:
        server.name = name
        updated = True
    if hashkey and server.hashkey != hashkey:
        server.hashkey = hashkey
        updated = True
    if ip_addr and server.ip_addr != ip_addr:
        server.ip_addr = ip_addr
        updated = True
    if port and server.port != port:
        server.port = port
        updated = True
    if revision and server.revision != revision:
        server.revision = revision
        updated = True
    if impure_cvars and server.impure_cvars != impure_cvars:
        server.impure_cvars = impure_cvars
        server.pure_ind = True if impure_cvars == 0 else False
        updated = True

    return updated


def get_or_create_server(session, name, hashkey, ip_addr, revision, port, impure_cvars):
    """
    Find a server by name or create one if not found. Parameters:

    session - SQLAlchemy database session factory
    name - server name of the server to be found or created
    hashkey - server hashkey
    ip_addr - the IP address of the server
    revision - the xonotic revision number
    port - the port number of the server
    impure_cvars - the number of impure cvar changes
    """
    servers_q = DBSession.query(Server).filter(Server.active_ind)

    if hashkey:
        # if the hashkey is provided, we'll use that
        servers_q = servers_q.filter((Server.name == name) or (Server.hashkey == hashkey))
    else:
        # otherwise, it is just by name
        servers_q = servers_q.filter(Server.name == name)

    # order by the hashkey, which means any hashkey match will appear first if there are multiple
    servers = servers_q.order_by(Server.hashkey, Server.create_dt).all()

    if len(servers) == 0:
        server = Server(name=name, hashkey=hashkey)
        session.add(server)
        session.flush()
        log.debug("Created server {} with hashkey {}.".format(server.server_id, server.hashkey))
    else:
        server = servers[0]
        if len(servers) == 1:
            log.info("Found existing server {}.".format(server.server_id))

        elif len(servers) > 1:
            server_id_list = ", ".join(["{}".format(s.server_id) for s in servers])
            log.warn("Multiple servers found ({})! Using the first one ({})."
                     .format(server_id_list, server.server_id))

    if update_server(server, name, hashkey, ip_addr, port, revision, impure_cvars):
        session.add(server)

    return server


def get_or_create_map(session=None, name=None):
    """
    Find a map by name or create one if not found. Parameters:

    session - SQLAlchemy database session factory
    name - map name of the map to be found or created
    """
    try:
        # find one by the name, if it exists
        gmap = session.query(Map).filter_by(name=name).one()
        log.debug("Found map id {0}: {1}".format(gmap.map_id,
            gmap.name))
    except NoResultFound, e:
        gmap = Map(name=name)
        session.add(gmap)
        session.flush()
        log.debug("Created map id {0}: {1}".format(gmap.map_id,
            gmap.name))
    except MultipleResultsFound, e:
        # multiple found, so use the first one but warn
        log.debug(e)
        gmaps = session.query(Map).filter_by(name=name).order_by(
                Map.map_id).all()
        gmap = gmaps[0]
        log.debug("Found map id {0}: {1} but found \
                multiple".format(gmap.map_id, gmap.name))

    return gmap


def create_game(session, start_dt, game_type_cd, server_id, map_id,
        match_id, duration, mod, winner=None):
    """
    Creates a game. Parameters:

    session - SQLAlchemy database session factory
    start_dt - when the game started (datetime object)
    game_type_cd - the game type of the game being played
    server_id - server identifier of the server hosting the game
    map_id - map on which the game was played
    winner - the team id of the team that won
    duration - how long the game lasted
    mod - mods in use during the game
    """
    seq = Sequence('games_game_id_seq')
    game_id = session.execute(seq)
    game = Game(game_id=game_id, start_dt=start_dt, game_type_cd=game_type_cd,
                server_id=server_id, map_id=map_id, winner=winner)
    game.match_id = match_id
    game.mod = mod[:64]

    # There is some drift between start_dt (provided by app) and create_dt
    # (default in the database), so we'll make them the same until this is 
    # resolved.
    game.create_dt = start_dt

    try:
        game.duration = datetime.timedelta(seconds=int(round(float(duration))))
    except:
        pass

    try:
        session.query(Game).filter(Game.server_id==server_id).\
                filter(Game.match_id==match_id).one()

        log.debug("Error: game with same server and match_id found! Ignoring.")

        # if a game under the same server and match_id found,
        # this is a duplicate game and can be ignored
        raise pyramid.httpexceptions.HTTPOk('OK')
    except NoResultFound, e:
        # server_id/match_id combination not found. game is ok to insert
        session.add(game)
        session.flush()
        log.debug("Created game id {0} on server {1}, map {2} at \
                {3}".format(game.game_id,
                    server_id, map_id, start_dt))

    return game


def get_or_create_player(session=None, hashkey=None, nick=None):
    """
    Finds a player by hashkey or creates a new one (along with a
    corresponding hashkey entry. Parameters:

    session - SQLAlchemy database session factory
    hashkey - hashkey of the player to be found or created
    nick - nick of the player (in case of a first time create)
    """
    # if we have a bot
    if re.search('^bot#\d+', hashkey):
        player = session.query(Player).filter_by(player_id=1).one()
    # if we have an untracked player
    elif re.search('^player#\d+$', hashkey):
        player = session.query(Player).filter_by(player_id=2).one()
    # else it is a tracked player
    else:
        # see if the player is already in the database
        # if not, create one and the hashkey along with it
        try:
            hk = session.query(Hashkey).filter_by(
                    hashkey=hashkey).one()
            player = session.query(Player).filter_by(
                    player_id=hk.player_id).one()
            log.debug("Found existing player {0} with hashkey {1}".format(
                player.player_id, hashkey))
        except:
            player = Player()
            session.add(player)
            session.flush()

            # if nick is given to us, use it. If not, use "Anonymous Player"
            # with a suffix added for uniqueness.
            if nick:
                player.nick = nick[:128]
                player.stripped_nick = strip_colors(qfont_decode(nick[:128]))
            else:
                player.nick = "Anonymous Player #{0}".format(player.player_id)
                player.stripped_nick = player.nick

            hk = Hashkey(player_id=player.player_id, hashkey=hashkey)
            session.add(hk)
            log.debug("Created player {0} ({2}) with hashkey {1}".format(
                player.player_id, hashkey, player.nick.encode('utf-8')))

    return player


def create_default_game_stat(session, game_type_cd):
    """Creates a blanked-out pgstat record for the given game type"""

    # this is what we have to do to get partitioned records in - grab the
    # sequence value first, then insert using the explicit ID (vs autogenerate)
    seq = Sequence('player_game_stats_player_game_stat_id_seq')
    pgstat_id = session.execute(seq)
    pgstat = PlayerGameStat(player_game_stat_id=pgstat_id,
            create_dt=datetime.datetime.utcnow())

    if game_type_cd == 'as':
        pgstat.kills = pgstat.deaths = pgstat.suicides = pgstat.collects = 0

    if game_type_cd in 'ca' 'dm' 'duel' 'rune' 'tdm':
        pgstat.kills = pgstat.deaths = pgstat.suicides = 0

    if game_type_cd == 'cq':
        pgstat.kills = pgstat.deaths = pgstat.suicides = pgstat.captures = 0
        pgstat.drops = 0

    if game_type_cd == 'ctf':
        pgstat.kills = pgstat.captures = pgstat.pickups = pgstat.drops = 0
        pgstat.returns = pgstat.carrier_frags = 0

    if game_type_cd == 'cts':
        pgstat.deaths = 0

    if game_type_cd == 'dom':
        pgstat.kills = pgstat.deaths = pgstat.suicides = pgstat.pickups = 0
        pgstat.drops = 0

    if game_type_cd == 'ft':
        pgstat.kills = pgstat.deaths = pgstat.suicides = pgstat.revivals = 0

    if game_type_cd == 'ka':
        pgstat.kills = pgstat.deaths = pgstat.suicides = pgstat.pickups = 0
        pgstat.carrier_frags = 0
        pgstat.time = datetime.timedelta(seconds=0)

    if game_type_cd == 'kh':
        pgstat.kills = pgstat.deaths = pgstat.suicides = pgstat.pickups = 0
        pgstat.captures = pgstat.drops = pgstat.pushes = pgstat.destroys = 0
        pgstat.carrier_frags = 0

    if game_type_cd == 'lms':
        pgstat.kills = pgstat.deaths = pgstat.suicides = pgstat.lives = 0

    if game_type_cd == 'nb':
        pgstat.kills = pgstat.deaths = pgstat.suicides = pgstat.captures = 0
        pgstat.drops = 0

    if game_type_cd == 'rc':
        pgstat.kills = pgstat.deaths = pgstat.suicides = pgstat.laps = 0

    return pgstat


def create_game_stat(session, game_meta, game, server, gmap, player, events):
    """Game stats handler for all game types"""

    game_type_cd = game.game_type_cd

    pgstat = create_default_game_stat(session, game_type_cd)

    # these fields should be on every pgstat record
    pgstat.game_id       = game.game_id
    pgstat.player_id     = player.player_id
    pgstat.nick          = events.get('n', 'Anonymous Player')[:128]
    pgstat.stripped_nick = strip_colors(qfont_decode(pgstat.nick))
    pgstat.score         = int(round(float(events.get('scoreboard-score', 0))))
    pgstat.alivetime     = datetime.timedelta(seconds=int(round(float(events.get('alivetime', 0.0)))))
    pgstat.rank          = int(events.get('rank', None))
    pgstat.scoreboardpos = int(events.get('scoreboardpos', pgstat.rank))

    if pgstat.nick != player.nick \
            and player.player_id > 2 \
            and pgstat.nick != 'Anonymous Player':
        register_new_nick(session, player, pgstat.nick)

    wins = False

    # gametype-specific stuff is handled here. if passed to us, we store it
    for (key,value) in events.items():
        if key == 'wins': wins = True
        if key == 't': pgstat.team = int(value)

        if key == 'scoreboard-drops': pgstat.drops = int(value)
        if key == 'scoreboard-returns': pgstat.returns = int(value)
        if key == 'scoreboard-fckills': pgstat.carrier_frags = int(value)
        if key == 'scoreboard-pickups': pgstat.pickups = int(value)
        if key == 'scoreboard-caps': pgstat.captures = int(value)
        if key == 'scoreboard-score': pgstat.score = int(round(float(value)))
        if key == 'scoreboard-deaths': pgstat.deaths = int(value)
        if key == 'scoreboard-kills': pgstat.kills = int(value)
        if key == 'scoreboard-suicides': pgstat.suicides = int(value)
        if key == 'scoreboard-objectives': pgstat.collects = int(value)
        if key == 'scoreboard-captured': pgstat.captures = int(value)
        if key == 'scoreboard-released': pgstat.drops = int(value)
        if key == 'scoreboard-fastest':
            pgstat.fastest = datetime.timedelta(seconds=float(value)/100)
        if key == 'scoreboard-takes': pgstat.pickups = int(value)
        if key == 'scoreboard-ticks': pgstat.drops = int(value)
        if key == 'scoreboard-revivals': pgstat.revivals = int(value)
        if key == 'scoreboard-bctime':
            pgstat.time = datetime.timedelta(seconds=int(value))
        if key == 'scoreboard-bckills': pgstat.carrier_frags = int(value)
        if key == 'scoreboard-losses': pgstat.drops = int(value)
        if key == 'scoreboard-pushes': pgstat.pushes = int(value)
        if key == 'scoreboard-destroyed': pgstat.destroys = int(value)
        if key == 'scoreboard-kckills': pgstat.carrier_frags = int(value)
        if key == 'scoreboard-lives': pgstat.lives = int(value)
        if key == 'scoreboard-goals': pgstat.captures = int(value)
        if key == 'scoreboard-faults': pgstat.drops = int(value)
        if key == 'scoreboard-laps': pgstat.laps = int(value)

        if key == 'avglatency': pgstat.avg_latency = float(value)
        if key == 'scoreboard-captime':
            pgstat.fastest = datetime.timedelta(seconds=float(value)/100)
            if game.game_type_cd == 'ctf':
                update_fastest_cap(session, player.player_id, game.game_id,
                        gmap.map_id, pgstat.fastest, game.mod)

    # there is no "winning team" field, so we have to derive it
    if wins and pgstat.team is not None and game.winner is None:
        game.winner = pgstat.team
        session.add(game)

    session.add(pgstat)

    return pgstat


def create_anticheats(session, pgstat, game, player, events):
    """Anticheats handler for all game types"""

    anticheats = []

    # all anticheat events are prefixed by "anticheat"
    for (key,value) in events.items():
        if key.startswith("anticheat"):
            try:
                ac = PlayerGameAnticheat(
                    player.player_id,
                    game.game_id,
                    key,
                    float(value)
                )
                anticheats.append(ac)
                session.add(ac)
            except Exception as e:
                log.debug("Could not parse value for key %s. Ignoring." % key)

    return anticheats


def create_default_team_stat(session, game_type_cd):
    """Creates a blanked-out teamstat record for the given game type"""

    # this is what we have to do to get partitioned records in - grab the
    # sequence value first, then insert using the explicit ID (vs autogenerate)
    seq = Sequence('team_game_stats_team_game_stat_id_seq')
    teamstat_id = session.execute(seq)
    teamstat = TeamGameStat(team_game_stat_id=teamstat_id,
            create_dt=datetime.datetime.utcnow())

    # all team game modes have a score, so we'll zero that out always
    teamstat.score = 0

    if game_type_cd in 'ca' 'ft' 'lms' 'ka':
        teamstat.rounds = 0

    if game_type_cd == 'ctf':
        teamstat.caps = 0

    return teamstat


def create_team_stat(session, game, events):
    """Team stats handler for all game types"""

    try:
        teamstat = create_default_team_stat(session, game.game_type_cd)
        teamstat.game_id = game.game_id

        # we should have a team ID if we have a 'Q' event
        if re.match(r'^team#\d+$', events.get('Q', '')):
            team = int(events.get('Q').replace('team#', ''))
            teamstat.team = team

        # gametype-specific stuff is handled here. if passed to us, we store it
        for (key,value) in events.items():
            if key == 'scoreboard-score': teamstat.score = int(round(float(value)))
            if key == 'scoreboard-caps': teamstat.caps = int(value)
            if key == 'scoreboard-goals': teamstat.caps = int(value)
            if key == 'scoreboard-rounds': teamstat.rounds = int(value)

        session.add(teamstat)
    except Exception as e:
        raise e

    return teamstat


def create_weapon_stats(session, game_meta, game, player, pgstat, events):
    """Weapon stats handler for all game types"""
    pwstats = []

    # Version 1 of stats submissions doubled the data sent.
    # To counteract this we divide the data by 2 only for
    # POSTs coming from version 1.
    try:
        version = int(game_meta['V'])
        if version == 1:
            is_doubled = True
            log.debug('NOTICE: found a version 1 request, halving the weapon stats...')
        else:
            is_doubled = False
    except:
        is_doubled = False

    for (key,value) in events.items():
        matched = re.search("acc-(.*?)-cnt-fired", key)
        if matched:
            weapon_cd = matched.group(1)

            # Weapon names changed for 0.8. We'll convert the old
            # ones to use the new scheme as well.
            mapped_weapon_cd = weapon_map.get(weapon_cd, weapon_cd)

            seq = Sequence('player_weapon_stats_player_weapon_stats_id_seq')
            pwstat_id = session.execute(seq)
            pwstat = PlayerWeaponStat()
            pwstat.player_weapon_stats_id = pwstat_id
            pwstat.player_id = player.player_id
            pwstat.game_id = game.game_id
            pwstat.player_game_stat_id = pgstat.player_game_stat_id
            pwstat.weapon_cd = mapped_weapon_cd

            if 'n' in events:
                pwstat.nick = events['n']
            else:
                pwstat.nick = events['P']

            if 'acc-' + weapon_cd + '-cnt-fired' in events:
                pwstat.fired = int(round(float(
                        events['acc-' + weapon_cd + '-cnt-fired'])))
            if 'acc-' + weapon_cd + '-fired' in events:
                pwstat.max = int(round(float(
                        events['acc-' + weapon_cd + '-fired'])))
            if 'acc-' + weapon_cd + '-cnt-hit' in events:
                pwstat.hit = int(round(float(
                        events['acc-' + weapon_cd + '-cnt-hit'])))
            if 'acc-' + weapon_cd + '-hit' in events:
                pwstat.actual = int(round(float(
                        events['acc-' + weapon_cd + '-hit'])))
            if 'acc-' + weapon_cd + '-frags' in events:
                pwstat.frags = int(round(float(
                        events['acc-' + weapon_cd + '-frags'])))

            if is_doubled:
                pwstat.fired = pwstat.fired/2
                pwstat.max = pwstat.max/2
                pwstat.hit = pwstat.hit/2
                pwstat.actual = pwstat.actual/2
                pwstat.frags = pwstat.frags/2

            session.add(pwstat)
            pwstats.append(pwstat)

    return pwstats


def get_ranks(session, player_ids, game_type_cd):
    """
    Gets the rank entries for all players in the given list, returning a dict
    of player_id -> PlayerRank instance. The rank entry corresponds to the
    game type of the parameter passed in as well.
    """
    ranks = {}
    for pr in session.query(PlayerRank).\
            filter(PlayerRank.player_id.in_(player_ids)).\
            filter(PlayerRank.game_type_cd == game_type_cd).\
            all():
                ranks[pr.player_id] = pr

    return ranks


def submit_stats(request):
    """
    Entry handler for POST stats submissions.
    """
    try:
        # placeholder for the actual session
        session = None

        log.debug("\n----- BEGIN REQUEST BODY -----\n" + request.body +
                "----- END REQUEST BODY -----\n\n")

        (idfp, status) = verify_request(request)
        (game_meta, raw_players, raw_teams) = parse_stats_submission(request.body)
        revision = game_meta.get('R', 'unknown')
        duration = game_meta.get('D', None)

        # only players present at the end of the match are eligible for stats
        raw_players = filter(played_in_game, raw_players)

        do_precondition_checks(request, game_meta, raw_players)

        # the "duel" gametype is fake
        if len(raw_players) == 2 \
            and num_real_players(raw_players) == 2 \
            and game_meta['G'] == 'dm':
            game_meta['G'] = 'duel'

        #----------------------------------------------------------------------
        # Actual setup (inserts/updates) below here
        #----------------------------------------------------------------------
        session = DBSession()

        game_type_cd = game_meta['G']

        # All game types create Game, Server, Map, and Player records
        # the same way.
        server = get_or_create_server(
                session      = session,
                hashkey      = idfp,
                name         = game_meta['S'],
                revision     = revision,
                ip_addr      = get_remote_addr(request),
                port         = game_meta.get('U', None),
                impure_cvars = game_meta.get('C', 0))

        gmap = get_or_create_map(
                session = session,
                name    = game_meta['M'])

        game = create_game(
                session      = session,
                start_dt     = datetime.datetime.utcnow(),
                server_id    = server.server_id,
                game_type_cd = game_type_cd,
                map_id       = gmap.map_id,
                match_id     = game_meta['I'],
                duration     = duration,
                mod          = game_meta.get('O', None))

        # keep track of the players we've seen
        player_ids = []
        pgstats = []
        hashkeys = {}
        for events in raw_players:
            player = get_or_create_player(
                session = session,
                hashkey = events['P'],
                nick    = events.get('n', None))

            pgstat = create_game_stat(session, game_meta, game, server,
                    gmap, player, events)
            pgstats.append(pgstat)

            if player.player_id > 1:
                anticheats = create_anticheats(session, pgstat, game, player, events)

            if player.player_id > 2:
                player_ids.append(player.player_id)
                hashkeys[player.player_id] = events['P']

            if should_do_weapon_stats(game_type_cd) and player.player_id > 1:
                pwstats = create_weapon_stats(session, game_meta, game, player,
                        pgstat, events)

        # store them on games for easy access
        game.players = player_ids

        for events in raw_teams:
            try:
                teamstat = create_team_stat(session, game, events)
            except Exception as e:
                raise e

        if server.elo_ind and gametype_elo_eligible(game_type_cd):
            ep = EloProcessor(session, game, pgstats)
            ep.save(session)

        session.commit()
        log.debug('Success! Stats recorded.')

        # ranks are fetched after we've done the "real" processing
        ranks = get_ranks(session, player_ids, game_type_cd)

        # plain text response
        request.response.content_type = 'text/plain'

        return {
                "now"        : calendar.timegm(datetime.datetime.utcnow().timetuple()),
                "server"     : server,
                "game"       : game,
                "gmap"       : gmap,
                "player_ids" : player_ids,
                "hashkeys"   : hashkeys,
                "elos"       : ep.wip,
                "ranks"      : ranks,
        }

    except Exception as e:
        if session:
            session.rollback()
        raise e
