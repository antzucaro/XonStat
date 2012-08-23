import datetime
import logging
import os
import pyramid.httpexceptions
import re
import time
from pyramid.response import Response
from sqlalchemy import Sequence
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from xonstat.d0_blind_id import d0_blind_id_verify
from xonstat.elo import process_elos
from xonstat.models import *
from xonstat.util import strip_colors, qfont_decode

log = logging.getLogger(__name__)


def is_blank_game(players):
    """Determine if this is a blank game or not. A blank game is either:

    1) a match that ended in the warmup stage, where accuracy events are not
    present

    2) a match in which no player made a positive or negative score AND was
    on the scoreboard
    """
    r = re.compile(r'acc-.*-cnt-fired')
    flg_nonzero_score = False
    flg_acc_events = False

    for events in players:
        if is_real_player(events):
            for (key,value) in events.items():
                if key == 'scoreboard-score' and value != '0':
                    flg_nonzero_score = True
                if r.search(key):
                    flg_acc_events = True

    return not (flg_nonzero_score and flg_acc_events)

def get_remote_addr(request):
    """Get the Xonotic server's IP address"""
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For']
    else:
        return request.remote_addr


def is_supported_gametype(gametype):
    """Whether a gametype is supported or not"""
    flg_supported = True

    if gametype == 'cts' or gametype == 'lms':
        flg_supported = False

    return flg_supported


def verify_request(request):
    try:
        (idfp, status) = d0_blind_id_verify(
                sig=request.headers['X-D0-Blind-Id-Detached-Signature'],
                querystring='',
                postdata=request.body)

        log.debug('\nidfp: {0}\nstatus: {1}'.format(idfp, status))
    except: 
        idfp = None
        status = None

    return (idfp, status)


def num_real_players(player_events, count_bots=False):
    """
    Returns the number of real players (those who played 
    and are on the scoreboard).
    """
    real_players = 0

    for events in player_events:
        if is_real_player(events, count_bots):
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


def is_real_player(events, count_bots=False):
    """
    Determines if a given set of player events correspond with a player who

    1) is not a bot (P event does not look like a bot)
    2) played in the game (matches 1)
    3) was present at the end of the game (scoreboardvalid 1)

    Returns True if the player meets the above conditions, and false otherwise.
    """
    flg_is_real = False

    # removing 'joins' here due to bug, but it should be here
    if 'matches' in events and 'scoreboardvalid' in events:
        if (events['P'].startswith('bot') and count_bots) or \
            not events['P'].startswith('bot'):
            flg_is_real = True

    return flg_is_real


def register_new_nick(session, player, new_nick):
    """
    Change the player record's nick to the newly found nick. Store the old
    nick in the player_nicks table for that player.

    session - SQLAlchemy database session factory
    player - player record whose nick is changing
    new_nick - the new nickname
    """
    # see if that nick already exists
    stripped_nick = strip_colors(player.nick)
    try:
        player_nick = session.query(PlayerNick).filter_by(
            player_id=player.player_id, stripped_nick=stripped_nick).one()
    except NoResultFound, e:
        # player_id/stripped_nick not found, create one
        # but we don't store "Anonymous Player #N"
        if not re.search('^Anonymous Player #\d+$', player.nick):
            player_nick = PlayerNick()
            player_nick.player_id = player.player_id
            player_nick.stripped_nick = player.stripped_nick
            player_nick.nick = player.nick
            session.add(player_nick)

    # We change to the new nick regardless
    player.nick = new_nick
    player.stripped_nick = strip_colors(new_nick)
    session.add(player)


def get_or_create_server(session=None, name=None, hashkey=None, ip_addr=None,
        revision=None):
    """
    Find a server by name or create one if not found. Parameters:

    session - SQLAlchemy database session factory
    name - server name of the server to be found or created
    hashkey - server hashkey
    """
    try:
        # find one by that name, if it exists
        server = session.query(Server).filter_by(name=name).one()

        # store new hashkey
        if server.hashkey != hashkey:
            server.hashkey = hashkey
            session.add(server)

        # store new IP address
        if server.ip_addr != ip_addr:
            server.ip_addr = ip_addr
            session.add(server)

        # store new revision
        if server.revision != revision:
            server.revision = revision
            session.add(server)

        log.debug("Found existing server {0}".format(server.server_id))

    except MultipleResultsFound, e:
        # multiple found, so also filter by hashkey
        server = session.query(Server).filter_by(name=name).\
                filter_by(hashkey=hashkey).one()
        log.debug("Found existing server {0}".format(server.server_id))

    except NoResultFound, e:
        # not found, create one
        server = Server(name=name, hashkey=hashkey)
        session.add(server)
        session.flush()
        log.debug("Created server {0} with hashkey {1}".format(
            server.server_id, server.hashkey))

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
        server_id=None, map_id=None, winner=None, match_id=None):
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
        session.query(Game).filter(Game.server_id==server_id).\
                filter(Game.match_id==match_id).one()

        log.debug("Error: game with same server and match_id found! Ignoring.")

        # if a game under the same server and match_id found, 
        # this is a duplicate game and can be ignored
        raise pyramid.httpexceptions.HTTPOk('OK')
    except NoResultFound, e:
        # server_id/match_id combination not found. game is ok to insert
        session.add(game)
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
                player.stripped_nick = strip_colors(nick[:128])
            else:
                player.nick = "Anonymous Player #{0}".format(player.player_id)
                player.stripped_nick = player.nick

            hk = Hashkey(player_id=player.player_id, hashkey=hashkey)
            session.add(hk)
            log.debug("Created player {0} ({2}) with hashkey {1}".format(
                player.player_id, hashkey, player.nick.encode('utf-8')))

    return player

def create_player_game_stat(session=None, player=None, 
        game=None, player_events=None):
    """
    Creates game statistics for a given player in a given game. Parameters:

    session - SQLAlchemy session factory
    player - Player record of the player who owns the stats
    game - Game record for the game to which the stats pertain
    player_events - dictionary for the actual stats that need to be transformed
    """

    # in here setup default values (e.g. if game type is CTF then
    # set kills=0, score=0, captures=0, pickups=0, fckills=0, etc
    # TODO: use game's create date here instead of now()
    seq = Sequence('player_game_stats_player_game_stat_id_seq')
    pgstat_id = session.execute(seq)
    pgstat = PlayerGameStat(player_game_stat_id=pgstat_id, 
            create_dt=datetime.datetime.utcnow())

    # set player id from player record
    pgstat.player_id = player.player_id

    #set game id from game record
    pgstat.game_id = game.game_id

    # all games have a score
    pgstat.score = 0

    if game.game_type_cd == 'dm' or game.game_type_cd == 'tdm' or game.game_type_cd == 'duel':
        pgstat.kills = 0
        pgstat.deaths = 0
        pgstat.suicides = 0
    elif game.game_type_cd == 'ctf':
        pgstat.kills = 0
        pgstat.captures = 0
        pgstat.pickups = 0
        pgstat.drops = 0
        pgstat.returns = 0
        pgstat.carrier_frags = 0

    for (key,value) in player_events.items():
        if key == 'n': pgstat.nick = value[:128]
        if key == 't': pgstat.team = int(value)
        if key == 'rank': pgstat.rank = int(value)
        if key == 'alivetime': 
            pgstat.alivetime = datetime.timedelta(seconds=int(round(float(value))))
        if key == 'scoreboard-drops': pgstat.drops = int(value)
        if key == 'scoreboard-returns': pgstat.returns = int(value)
        if key == 'scoreboard-fckills': pgstat.carrier_frags = int(value)
        if key == 'scoreboard-pickups': pgstat.pickups = int(value)
        if key == 'scoreboard-caps': pgstat.captures = int(value)
        if key == 'scoreboard-score': pgstat.score = int(value)
        if key == 'scoreboard-deaths': pgstat.deaths = int(value)
        if key == 'scoreboard-kills': pgstat.kills = int(value)
        if key == 'scoreboard-suicides': pgstat.suicides = int(value)

    # check to see if we had a name, and if
    # not use an anonymous handle
    if pgstat.nick == None:
        pgstat.nick = "Anonymous Player"
        pgstat.stripped_nick = "Anonymous Player"

    # otherwise process a nick change
    elif pgstat.nick != player.nick and player.player_id > 2:
        register_new_nick(session, player, pgstat.nick)

    # if the player is ranked #1 and it is a team game, set the game's winner
    # to be the team of that player
    # FIXME: this is a hack, should be using the 'W' field (not present)
    if pgstat.rank == 1 and pgstat.team:
        game.winner = pgstat.team
        session.add(game)

    session.add(pgstat)

    return pgstat


def create_player_weapon_stats(session=None, player=None, 
        game=None, pgstat=None, player_events=None):
    """
    Creates accuracy records for each weapon used by a given player in a
    given game. Parameters:

    session - SQLAlchemy session factory object
    player - Player record who owns the weapon stats
    game - Game record in which the stats were created
    pgstat - Corresponding PlayerGameStat record for these weapon stats
    player_events - dictionary containing the raw weapon values that need to be
        transformed
    """
    pwstats = []

    for (key,value) in player_events.items():
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

            if 'n' in player_events:
                pwstat.nick = player_events['n']
            else:
                pwstat.nick = player_events['P']

            if 'acc-' + weapon_cd + '-cnt-fired' in player_events:
                pwstat.fired = int(round(float(
                        player_events['acc-' + weapon_cd + '-cnt-fired'])))
            if 'acc-' + weapon_cd + '-fired' in player_events:
                pwstat.max = int(round(float(
                        player_events['acc-' + weapon_cd + '-fired'])))
            if 'acc-' + weapon_cd + '-cnt-hit' in player_events:
                pwstat.hit = int(round(float(
                        player_events['acc-' + weapon_cd + '-cnt-hit'])))
            if 'acc-' + weapon_cd + '-hit' in player_events:
                pwstat.actual = int(round(float(
                        player_events['acc-' + weapon_cd + '-hit'])))
            if 'acc-' + weapon_cd + '-frags' in player_events:
                pwstat.frags = int(round(float(
                        player_events['acc-' + weapon_cd + '-frags'])))

            session.add(pwstat)
            pwstats.append(pwstat)

    return pwstats


def parse_body(request):
    """
    Parses the POST request body for a stats submission
    """
    # storage vars for the request body
    game_meta = {}
    player_events = {}
    current_team = None
    players = []

    for line in request.body.split('\n'):
        try:
            (key, value) = line.strip().split(' ', 1)

            # Server (S) and Nick (n) fields can have international characters.
            # We convert to UTF-8.
            if key in 'S' 'n':
                value = unicode(value, 'utf-8')

            if key in 'V' 'T' 'G' 'M' 'S' 'C' 'R' 'W' 'I':
                game_meta[key] = value

            if key == 'P':
                # if we were working on a player record already, append
                # it and work on a new one (only set team info)
                if len(player_events) != 0:
                    players.append(player_events)
                    player_events = {}

                player_events[key] = value

            if key == 'e':
                (subkey, subvalue) = value.split(' ', 1)
                player_events[subkey] = subvalue
            if key == 'n':
                player_events[key] = value
            if key == 't':
                player_events[key] = value
        except:
            # no key/value pair - move on to the next line
            pass

    # add the last player we were working on
    if len(player_events) > 0:
        players.append(player_events)

    return (game_meta, players)


def create_player_stats(session=None, player=None, game=None, 
        player_events=None):
    """
    Creates player game and weapon stats according to what type of player
    """
    pgstat = create_player_game_stat(session=session, 
        player=player, game=game, player_events=player_events)

    #TODO: put this into a config setting in the ini file?
    if not re.search('^bot#\d+$', player_events['P']):
        create_player_weapon_stats(session=session, 
            player=player, game=game, pgstat=pgstat,
            player_events=player_events)


def stats_submit(request):
    """
    Entry handler for POST stats submissions.
    """
    try:
        log.debug("\n----- BEGIN REQUEST BODY -----\n" + request.body +
                "----- END REQUEST BODY -----\n\n")

        (idfp, status) = verify_request(request)
        if not idfp:
            log.debug("ERROR: Unverified request")
            raise pyramid.httpexceptions.HTTPUnauthorized("Unverified request")

        (game_meta, players) = parse_body(request)  

        if not has_required_metadata(game_meta):
            log.debug("ERROR: Required game meta missing")
            raise pyramid.httpexceptions.HTTPUnprocessableEntity("Missing game meta")

        if not is_supported_gametype(game_meta['G']):
            log.debug("ERROR: Unsupported gametype")
            raise pyramid.httpexceptions.HTTPOk("OK")

        if not has_minimum_real_players(request.registry.settings, players):
            log.debug("ERROR: Not enough real players")
            raise pyramid.httpexceptions.HTTPOk("OK")

        if is_blank_game(players):
            log.debug("ERROR: Blank game")
            raise pyramid.httpexceptions.HTTPOk("OK")

        # the "duel" gametype is fake
        if num_real_players(players, count_bots=True) == 2 and \
                game_meta['G'] == 'dm':
            game_meta['G'] = 'duel'


        # fix for DTG, who didn't #ifdef WATERMARK to set the revision info
        try:
            revision = game_meta['R']
        except:
            revision = "unknown"

        #----------------------------------------------------------------------
        # This ends the "precondition" section of sanity checks. All
        # functions not requiring a database connection go ABOVE HERE.
        #----------------------------------------------------------------------
        session = DBSession()

        server = get_or_create_server(session=session, hashkey=idfp, 
                name=game_meta['S'], revision=revision,
                ip_addr=get_remote_addr(request))

        gmap = get_or_create_map(session=session, name=game_meta['M'])

        # FIXME: use the gmtime instead of utcnow() when the timezone bug is
        # fixed
        game = create_game(session=session, 
                start_dt=datetime.datetime.utcnow(),
                #start_dt=datetime.datetime(
                    #*time.gmtime(float(game_meta['T']))[:6]), 
                server_id=server.server_id, game_type_cd=game_meta['G'], 
                   map_id=gmap.map_id, match_id=game_meta['I'])

        # find or create a record for each player
        # and add stats for each if they were present at the end
        # of the game
        for player_events in players:
            if 'n' in player_events:
                nick = player_events['n']
            else:
                nick = None

            if 'matches' in player_events and 'scoreboardvalid' \
                in player_events:
                player = get_or_create_player(session=session, 
                    hashkey=player_events['P'], nick=nick)
                log.debug('Creating stats for %s' % player_events['P'])
                create_player_stats(session=session, player=player, game=game, 
                        player_events=player_events)

        # update elos
        try:
            process_elos(game, session)
        except Exception as e:
            log.debug('Error (non-fatal): elo processing failed.')

        session.commit()
        log.debug('Success! Stats recorded.')
        return Response('200 OK')
    except Exception as e:
        session.rollback()
        return e
