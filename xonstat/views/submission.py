import datetime
import logging
import re
import time
from pyramid.config import get_current_registry
from pyramid.response import Response
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from xonstat.d0_blind_id import d0_blind_id_verify
from xonstat.models import *
from xonstat.util import strip_colors

log = logging.getLogger(__name__)


def is_verified_request(request):
    (idfp, status) = d0_blind_id_verify(
            sig=request.headers['X-D0-Blind-Id-Detached-Signature'],
            querystring='',
            postdata=request.body)

    log.debug('\nidfp: {0}\nstatus: {1}'.format(idfp, status))

    if idfp != None:
        return True
    else:
        return False


def has_minimum_real_players(player_events):
    """
    Determines if the collection of player events has enough "real" players
    to store in the database. The minimum setting comes from the config file
    under the setting xonstat.minimum_real_players.
    """
    flg_has_min_real_players = True

    settings = get_current_registry().settings
    try: 
        minimum_required_players = int(
                settings['xonstat.minimum_required_players'])
    except:
        minimum_required_players = 2

    real_players = 0
    for events in player_events:
        if is_real_player(events):
            real_players += 1

    #TODO: put this into a config setting in the ini file?
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
        'S' not in metadata:
            flg_has_req_metadata = False

    return flg_has_req_metadata

    
def is_real_player(events):
    """
    Determines if a given set of player events correspond with a player who
    
    1) is not a bot (P event does not look like a bot)
    2) played in the game (matches 1)
    3) was present at the end of the game (scoreboardvalid 1)

    Returns True if the player meets the above conditions, and false otherwise.
    """
    flg_is_real = False

    if not events['P'].startswith('bot'):
        # removing 'joins' here due to bug, but it should be here
        if 'matches' in events and 'scoreboardvalid' in events:
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
            player_nick.stripped_nick = stripped_nick
            player_nick.nick = player.nick
            session.add(player_nick)

    # We change to the new nick regardless
    player.nick = new_nick
    session.add(player)


def get_or_create_server(session=None, name=None):
    """
    Find a server by name or create one if not found. Parameters:

    session - SQLAlchemy database session factory
    name - server name of the server to be found or created
    """
    try:
        # find one by that name, if it exists
        server = session.query(Server).filter_by(name=name).one()
        log.debug("Found server id {0}: {1}".format(
            server.server_id, server.name.encode('utf-8')))
    except NoResultFound, e:
        server = Server(name=name)
        session.add(server)
        session.flush()
        log.debug("Created server id {0}: {1}".format(
            server.server_id, server.name.encode('utf-8')))
    except MultipleResultsFound, e:
        # multiple found, so use the first one but warn
        log.debug(e)
        servers = session.query(Server).filter_by(name=name).order_by(
                Server.server_id).all()
        server = servers[0]
        log.debug("Created server id {0}: {1} but found \
                multiple".format(
            server.server_id, server.name.encode('utf-8')))

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
        server_id=None, map_id=None, winner=None):
    """
    Creates a game. Parameters:

    session - SQLAlchemy database session factory
    start_dt - when the game started (datetime object)
    game_type_cd - the game type of the game being played
    server_id - server identifier of the server hosting the game
    map_id - map on which the game was played
    winner - the team id of the team that won
    """

    game = Game(start_dt=start_dt, game_type_cd=game_type_cd,
                server_id=server_id, map_id=map_id, winner=winner)
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
    if re.search('^bot#\d+$', hashkey):
        player = session.query(Player).filter_by(player_id=1).one()
    # if we have an untracked player
    elif re.search('^player#\d+$', hashkey):
        player = session.query(Player).filter_by(player_id=2).one()
    # else it is a tracked player
    else:
        # see if the player is already in the database
        # if not, create one and the hashkey along with it
        try:
            hashkey = session.query(Hashkey).filter_by(
                    hashkey=hashkey).one()
            player = session.query(Player).filter_by(
                    player_id=hashkey.player_id).one()
            log.debug("Found existing player {0} with hashkey {1}".format(
                player.player_id, hashkey.hashkey))
        except:
            player = Player()
            session.add(player)
            session.flush()

	    # if nick is given to us, use it. If not, use "Anonymous Player"
            # with a suffix added for uniqueness.
            if nick:
                player.nick = nick[:128]
	    else:
                player.nick = "Anonymous Player #{0}".format(player.player_id)

            hashkey = Hashkey(player_id=player.player_id, hashkey=hashkey)
            session.add(hashkey)
            log.debug("Created player {0} ({2}) with hashkey {1}".format(
                player.player_id, hashkey.hashkey, player.nick.encode('utf-8')))

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
    pgstat = PlayerGameStat(create_dt=datetime.datetime.now())

    # set player id from player record
    pgstat.player_id = player.player_id

    #set game id from game record
    pgstat.game_id = game.game_id

    # all games have a score
    pgstat.score = 0

    if game.game_type_cd == 'dm':
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
        if key == 't': pgstat.team = value
        if key == 'rank': pgstat.rank = value
        if key == 'alivetime': 
            pgstat.alivetime = datetime.timedelta(seconds=int(round(float(value))))
        if key == 'scoreboard-drops': pgstat.drops = value
        if key == 'scoreboard-returns': pgstat.returns = value
        if key == 'scoreboard-fckills': pgstat.carrier_frags = value
        if key == 'scoreboard-pickups': pgstat.pickups = value
        if key == 'scoreboard-caps': pgstat.captures = value
        if key == 'scoreboard-score': pgstat.score = value
        if key == 'scoreboard-deaths': pgstat.deaths = value
        if key == 'scoreboard-kills': pgstat.kills = value
        if key == 'scoreboard-suicides': pgstat.suicides = value

    # check to see if we had a name, and if 
    # not use the name from the player id
    if pgstat.nick == None:
        pgstat.nick = player.nick

    # if the nick we end up with is different from the one in the
    # player record, change the nick to reflect the new value
    if pgstat.nick != player.nick and player.player_id > 1:
        register_new_nick(session, player, pgstat.nick)

    # if the player is ranked #1 and it is a team game, set the game's winner
    # to be the team of that player
    # FIXME: this is a hack, should be using the 'W' field (not present)
    if pgstat.rank == '1' and pgstat.team:
        game.winner = pgstat.team
        session.add(game)

    session.add(pgstat)
    session.flush()

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
            pwstat = PlayerWeaponStat()
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
    
    log.debug(request.body)

    for line in request.body.split('\n'):
        try:
            (key, value) = line.strip().split(' ', 1)

            # Server (S) and Nick (n) fields can have international characters.
            # We encode these as UTF-8.
            if key in 'S' 'n':
                value = unicode(value, 'utf-8')
    
            if key in 'V' 'T' 'G' 'M' 'S' 'C' 'R' 'W':
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
        if not is_verified_request(request):
            raise Exception("Request is not verified.")

        session = DBSession()

        (game_meta, players) = parse_body(request)  
    
        if not has_required_metadata(game_meta):
            log.debug("Required game meta fields (T, G, M, or S) missing. "\
                    "Can't continue.")
            raise Exception("Required game meta fields (T, G, M, or S) missing.")
    
        if not has_minimum_real_players(players):
            raise Exception("The number of real players is below the minimum. "\
                    "Stats will be ignored.")

        server = get_or_create_server(session=session, name=game_meta['S'])
        gmap = get_or_create_map(session=session, name=game_meta['M'])

        game = create_game(session=session, 
                start_dt=datetime.datetime(
                    *time.gmtime(float(game_meta['T']))[:6]), 
                server_id=server.server_id, game_type_cd=game_meta['G'], 
                map_id=gmap.map_id)
    
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
    
        session.commit()
        log.debug('Success! Stats recorded.')
        return Response('200 OK')
    except Exception as e:
        session.rollback()
        raise e
