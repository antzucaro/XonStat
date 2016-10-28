#-*- coding: utf-8 -*-

import sys
from datetime import datetime, timedelta

from playerdata import PlayerData
from pyramid.paster import bootstrap
from skin import Skin
from sqlalchemy import distinct
from xonstat.models import DBSession, PlayerGameStat, Player, PlayerElo
from xonstat.util import datetime_seconds

# maximal number of query results (for testing, set to None to get all)
NUM_PLAYERS = None

# filter by player id (for testing, set to None to disable)
PLAYER_ID = None

# we look for players who have activity within the past DELTA hours
DELTA = 6

VERBOSE = False

INIFILE = None  # keep this set to "None"

# classic skin WITHOUT NAME - writes PNGs into "output//###.png"
skin_classic = Skin( "",
        bg              = "broken_noise",
        overlay         = "overlay_classic",
    )

# more fancy skin [** WIP **]- writes PNGs into "output/archer/###.png"
skin_archer = Skin( "archer",
        #bg              = "background_archer-v2_full",
        bg              = "background_archer-v3",
        overlay         = "",
        nick_maxwidth	= 260,
        gametype_pos    = (91,33),
        nostats_pos    	= (91,59),
        elo_pos    	= (91,47),
        rank_pos    = (91,58),
        winp_pos	= (509,20),
        wins_pos	= (508,35),
        loss_pos	= (508,45),
        kdr_pos		= (392,20),
        kills_pos	= (392,35),
        deaths_pos	= (392,45),
        ptime_color	= (0.05, 0.05, 0.1),
    )

# minimal skin - writes PNGs into "output/minimal/###.png"
skin_minimal = Skin( "minimal",
        bg              = None,
        bgcolor         = (0.04, 0.04, 0.04, 1.0),
        overlay         = "overlay_minimal",
        width           = 560,
        height          = 40,
        nick_fontsize   = 16,
        nick_pos        = (36,16),
        num_gametypes   = 3,
        nick_maxwidth   = 280,
        gametype_pos    = (70,30),
        gametype_color  = (0.0, 0.0, 0.0),
        gametype_text   = "%s:",
        gametype_width  = 100,
        gametype_fontsize = 10,
        gametype_align  = -1,
        gametype_upper  = False,
        elo_pos         = (75,30),
        elo_text        = "Elo %.0f",
        elo_color       = (0.7, 0.7, 0.7),
        elo_align       = 1,
        rank_pos        = None,
        nostats_pos     = None,
        #nostats_pos     = (75,30),
        #nostats_fontsize = 10,
        #nostats_angle   = 0,
        #nostats_text    = "no stats yet!",
        #nostats_color   = (0.7, 0.4, 0.4),
        kdr_pos         = (392,15),
        kdr_fontsize    = 10,
        kdr_colortop    = (0.6, 0.8, 0.6),
        kdr_colormid    = (0.6, 0.6, 0.6),
        kdr_colorbot    = (0.8, 0.6, 0.6),
        kills_pos       = None,
        deaths_pos      = None,
        winp_pos        = (508,15),
        winp_fontsize   = 10,
        winp_colortop   = (0.6, 0.8, 0.8),
        winp_colormid   = (0.6, 0.6, 0.6),
        winp_colorbot   = (0.8, 0.8, 0.6),
        wins_pos        = None,
        loss_pos        = None,
        ptime_pos       = (451,30),
        ptime_color     = (0.7, 0.7, 0.7),
    )


# parse cmdline parameters (for testing)

skins = []
for arg in sys.argv[1:]:
    if arg.startswith("-"):
        try:
            key,value = arg[1:].split("=")
        except:
            key,value = arg[1:], ""
        if key == "force":
            DELTA = 2**24   # large enough to enforce update, and doesn't result in errors
        elif key == "delta":
            DELTA = float(value)
        elif key == "test":
            NUM_PLAYERS = 100
        elif key == "player":
            PLAYER_ID = int(value)
        elif key == "verbose":
            VERBOSE = True
        else:
            print """Usage:  gen_badges.py [options] <ini-file> [skin list]
    Options:
        -force      Force updating all badges (delta = 2^24)
        -delta n    Manually set an update interval (delta)
        -test       Limit number of players to 100 (for testing)
        -player #   Filter by given player id
        -verbose    Show more verbose output
        -help       Show this help text
    Ini-File:
        Name of a Pyramid ini-file to use (e.g. prodution.ini or development.ini).
    Skin list:
        Space-separated list of skins to use when creating badges.
        Available skins:  classic, minimal, archer
        If no skins are given, classic and minmal will be used by default.
        NOTE: Output directories must exists before running the program!
"""
            sys.exit(-1)
    else:
        if INIFILE == None:
            INIFILE = arg
        else:
            if arg == "classic":
                skins.append(skin_classic)
            elif arg == "minimal":
                skins.append(skin_minimal)
            elif arg == "archer":
		        skins.append(skin_archer)

if len(skins) == 0:
    skins = [ skin_classic, skin_minimal, skin_archer ]

if not INIFILE:
    print "You must provide the name of an ini-file to use! Type 'gen_badges.py -h' for help."
    sys.exit(-1)

# environment setup
env = bootstrap(INIFILE)
req = env['request']
req.matchdict = {'id':3}

print "Requesting player data from db ..."
cutoff_dt = datetime.utcnow() - timedelta(hours=DELTA)
start = datetime.now()
players = []
if NUM_PLAYERS:
    players = DBSession.query(distinct(Player.player_id)).\
            filter(Player.player_id == PlayerElo.player_id).\
            filter(Player.player_id == PlayerGameStat.player_id).\
            filter(PlayerGameStat.create_dt > cutoff_dt).\
            filter(Player.nick != None).\
            filter(Player.player_id > 2).\
            filter(Player.active_ind == True).\
            limit(NUM_PLAYERS).all()
elif PLAYER_ID:
    players = DBSession.query(distinct(Player.player_id)).\
            filter(Player.player_id == PlayerElo.player_id).\
            filter(Player.player_id == PlayerGameStat.player_id).\
            filter(PlayerGameStat.create_dt > cutoff_dt).\
            filter(Player.nick != None).\
            filter(Player.player_id == PLAYER_ID).\
            filter(Player.active_ind == True).\
            limit(NUM_PLAYERS).all()
else:
    players = DBSession.query(distinct(Player.player_id)).\
            filter(Player.player_id == PlayerElo.player_id).\
            filter(Player.player_id == PlayerGameStat.player_id).\
            filter(PlayerGameStat.create_dt > cutoff_dt).\
            filter(Player.nick != None).\
            filter(Player.player_id > 2).\
            filter(Player.active_ind == True).\
            all()

playerdata = PlayerData

if len(players) > 0:
    stop = datetime.now()
    td = stop-start
    print "Query took %.2f seconds" % (datetime_seconds(td))

    print "Creating badges for %d players ..." % len(players)
    start = datetime.now()
    data_time, render_time = 0,0
    for player_id in players:
        req.matchdict['id'] = player_id

        sstart = datetime.now()
        playerdata.get_data(player_id)
        sstop = datetime.now()
        td = sstop-sstart
        data_time += datetime_seconds(td)

        sstart = datetime.now()
        for sk in skins:
            sk.render_image(playerdata.data, "output/%s/%d.png" % (str(sk), player_id[0]))
        sstop = datetime.now()
        td = sstop-sstart
        render_time += datetime_seconds(td)

        if VERBOSE == True:
            print player_id, unicode(playerdata.data['player'].nick)

    stop = datetime.now()
    td = stop-start
    total_seconds = datetime_seconds(td)
    print "Creating the badges took %.1f seconds (%.3f s per player)" % (total_seconds, total_seconds/float(len(players)))
    print "Total time for rendering images: %.3f s" % render_time
    print "Total time for getting data: %.3f s" % data_time

else:
    print "No active players found!"

