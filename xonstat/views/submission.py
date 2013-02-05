import datetime
import logging
import os
import pyramid.httpexceptions
import re
import time
import sqlalchemy.sql.expression as expr
from pyramid.response import Response
from sqlalchemy import Sequence
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from xonstat.d0_blind_id import d0_blind_id_verify
from xonstat.elo import process_elos
from xonstat.models import *
from xonstat.util import strip_colors, qfont_decode


log = logging.getLogger(__name__)


def parse_stats_submission(body):
    """
    Parses the POST request body for a stats submission
    """
    # storage vars for the request body
    game_meta = {}
    events = {}
    players = []

    for line in body.split('\n'):
        try:
            (key, value) = line.strip().split(' ', 1)

            # Server (S) and Nick (n) fields can have international characters.
            if key in 'S' 'n':
                value = unicode(value, 'utf-8')

            if key not in 'P' 'n' 'e' 't' 'i':
                game_meta[key] = value

            if key == 'P':
                # if we were working on a player record already, append
                # it and work on a new one (only set team info)
                if len(events) > 0:
                    players.append(events)
                    events = {}

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

    # add the last player we were working on
    if len(events) > 0:
        players.append(events)

    return (game_meta, players)


def is_blank_game(gametype, players):
    """Determine if this is a blank game or not. A blank game is either:

    1) a match that ended in the warmup stage, where accuracy events are not
    present (for non-CTS games)

    2) a match in which no player made a positive or negative score AND was
    on the scoreboard

    ... or for CTS, which doesn't record accuracy events

    1) a match in which no player made a fastest lap AND was
    on the scoreboard
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


def verify_request(request):
    """Verify requests using the d0_blind_id library"""

    # first determine if we should be verifying or not
    val_verify_requests = request.registry.settings.get('xonstat.verify_requests', 'true')
    if val_verify_requests == "true":
        flg_verify_requests = True
    else:
        flg_verify_requests = False

    try:
        (idfp, status) = d0_blind_id_verify(
                sig=request.headers['X-D0-Blind-Id-Detached-Signature'],
                querystring='',
                postdata=request.body)

        log.debug('\nidfp: {0}\nstatus: {1}'.format(idfp, status))
    except:
        idfp = None
        status = None

    if flg_verify_requests and not idfp:
        log.debug("ERROR: Unverified request")
        raise pyramid.httpexceptions.HTTPUnauthorized("Unverified request")

    return (idfp, status)


def do_precondition_checks(request, game_meta, raw_players):
    """Precondition checks for ALL gametypes.
       These do not require a database connection."""
    if not has_required_metadata(game_meta):
        log.debug("ERROR: Required game meta missing")
        raise pyramid.httpexceptions.HTTPUnprocessableEntity("Missing game meta")

    try:
        version = int(game_meta['V'])
    except:
        log.debug("ERROR: Required game meta invalid")
        raise pyramid.httpexceptions.HTTPUnprocessableEntity("Invalid game meta")

    if not is_supported_gametype(game_meta['G'], version):
        log.debug("ERROR: Unsupported gametype")
        raise pyramid.httpexceptions.HTTPOk("OK")

    if not has_minimum_real_players(request.registry.settings, raw_players):
        log.debug("ERROR: Not enough real players")
        raise pyramid.httpexceptions.HTTPOk("OK")

    if is_blank_game(game_meta['G'], raw_players):
        log.debug("ERROR: Blank game")
        raise pyramid.httpexceptions.HTTPOk("OK")


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

    if 'T' not in metadata or\
        'G' not in metadata or\
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


def should_do_elos(game_type_cd):
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


def update_fastest_cap(session, player_id, game_id,  map_id, captime):
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
            player_id=player_id, map_id=map_id).one()

        # current captime is faster, so update
        if captime < cur_fastest_cap.fastest_cap:
            cur_fastest_cap.fastest_cap = captime
            cur_fastest_cap.game_id = game_id
            cur_fastest_cap.create_dt = datetime.datetime.utcnow()
            session.add(cur_fastest_cap)

    except NoResultFound, e:
        # none exists, so insert
        cur_fastest_cap = PlayerCaptime(player_id, game_id, map_id, captime)
        session.add(cur_fastest_cap)
        session.flush()


def get_or_create_server(session, name, hashkey, ip_addr, revision):
    """
    Find a server by name or create one if not found. Parameters:

    session - SQLAlchemy database session factory
    name - server name of the server to be found or created
    hashkey - server hashkey
    """
    server = None

    # finding by hashkey is preferred, but if not we will fall
    # back to using name only, which can result in dupes
    if hashkey is not None:
        servers = session.query(Server).\
            filter_by(hashkey=hashkey).\
            order_by(expr.desc(Server.create_dt)).limit(1).all()

        if len(servers) > 0:
            server = servers[0]
            log.debug("Found existing server {0} by hashkey ({1})".format(
                server.server_id, server.hashkey))
    else:
        servers = session.query(Server).\
            filter_by(name=name).\
            order_by(expr.desc(Server.create_dt)).limit(1).all()

        if len(servers) > 0:
            server = servers[0]
            log.debug("Found existing server {0} by name".format(server.server_id))

    # still haven't found a server by hashkey or name, so we need to create one
    if server is None:
        server = Server(name=name, hashkey=hashkey)
        session.add(server)
        session.flush()
        log.debug("Created server {0} with hashkey {1}".format(
            server.server_id, server.hashkey))

    # detect changed fields
    if server.name != name:
        server.name = name
        session.add(server)

    if server.hashkey != hashkey:
        server.hashkey = hashkey
        session.add(server)

    if server.ip_addr != ip_addr:
        server.ip_addr = ip_addr
        session.add(server)

    if server.revision != revision:
        server.revision = revision
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


def create_game(session=None, start_dt=None, game_type_cd=None,
        server_id=None, map_id=None, winner=None, match_id=None,
        duration=None):
    """
    Creates a game. Parameters:

    session - SQLAlchemy database session factory
    start_dt - when the game started (datetime object)
    game_type_cd - the game type of the game being played
    server_id - server identifier of the server hosting the game
    map_id - map on which the game was played
    winner - the team id of the team that won
    """
    seq = Sequence('games_game_id_seq')
    game_id = session.execute(seq)
    game = Game(game_id=game_id, start_dt=start_dt, game_type_cd=game_type_cd,
                server_id=server_id, map_id=map_id, winner=winner)
    game.match_id = match_id

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
    if re.search('^bot#\d+$', hashkey) or re.search('^bot#\d+#', hashkey):
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

    pgstat = create_default_game_stat(session, game.game_type_cd)

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
                        gmap.map_id, pgstat.fastest)

    # there is no "winning team" field, so we have to derive it
    if wins and pgstat.team is not None and game.winner is None:
        game.winner = pgstat.team
        session.add(game)

    session.add(pgstat)

    return pgstat


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
            seq = Sequence('player_weapon_stats_player_weapon_stats_id_seq')
            pwstat_id = session.execute(seq)
            pwstat = PlayerWeaponStat()
            pwstat.player_weapon_stats_id = pwstat_id
            pwstat.player_id = player.player_id
            pwstat.game_id = game.game_id
            pwstat.player_game_stat_id = pgstat.player_game_stat_id
            pwstat.weapon_cd = weapon_cd

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


def create_elos(session, game):
    """Elo handler for all game types."""
    try:
        process_elos(game, session)
    except Exception as e:
        log.debug('Error (non-fatal): elo processing failed.')


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
        (game_meta, raw_players) = parse_stats_submission(request.body)
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
                session  = session,
                hashkey  = idfp,
                name     = game_meta['S'],
                revision = revision,
                ip_addr  = get_remote_addr(request))

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
                duration     = duration)

        for events in raw_players:
            player = get_or_create_player(
                session = session,
                hashkey = events['P'],
                nick    = events.get('n', None))

            pgstat = create_game_stat(session, game_meta, game, server,
                    gmap, player, events)

            if should_do_weapon_stats(game_type_cd) and player.player_id > 1:
                pwstats = create_weapon_stats(session, game_meta, game, player,
                        pgstat, events)

        if should_do_elos(game_type_cd):
            create_elos(session, game)

        session.commit()
        log.debug('Success! Stats recorded.')
        return Response('200 OK')
    except Exception as e:
        if session:
            session.rollback()
        return e
