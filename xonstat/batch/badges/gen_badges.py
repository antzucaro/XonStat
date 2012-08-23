#-*- coding: utf-8 -*-

import cairo as C
import sqlalchemy as sa
import sqlalchemy.sql.functions as func
from datetime import datetime
from mako.template import Template
from os import system
from pyramid.paster import bootstrap
from xonstat.models import *
from xonstat.views.player import player_info_data
from xonstat.util import qfont_decode
from colorsys import rgb_to_hls, hls_to_rgb


# similar to html_colors() from util.py
_contrast_threshold = 0.5

_dec_colors = [ (0.5,0.5,0.5),
                (1.0,0.0,0.0),
                (0.2,1.0,0.0),
                (1.0,1.0,0.0),
                (0.2,0.4,1.0),
                (0.2,1.0,1.0),
                (1.0,0.2,102),
                (1.0,1.0,1.0),
                (0.6,0.6,0.6),
                (0.5,0.5,0.5)
            ]


# parameters to affect the output, could be changed via URL
params = {
    'width':        560,
    'height':        70,
    'bg':           1,                      # 0 - black, 1 - dark_wall
    'font':         0,                      # 0 - xolonium, 1 - dejavu sans
    'gametypes':    ['duel','dm','ctf'],    # up to three gametypes to show
}


# maximal number of query results (for testing, set to 0 to get all)
NUM_PLAYERS = 100


def get_data(player):
    """Return player data as dict.
    
    This function is similar to the function in player.py but more optimized
    for this purpose.
    """

    # total games
    # wins/losses
    # kills/deaths
    # duel/dm/tdm/ctf elo + rank
    
    player_id = player.player_id
    
    total_stats = {}
    
    games_played = DBSession.query(
            Game.game_type_cd, func.count(), func.sum(PlayerGameStat.alivetime)).\
            filter(Game.game_id == PlayerGameStat.game_id).\
            filter(PlayerGameStat.player_id == player_id).\
            group_by(Game.game_type_cd).\
            order_by(func.count().desc()).\
            all()
    
    total_stats['games'] = 0
    total_stats['games_breakdown'] = {}  # this is a dictionary inside a dictionary .. dictception?
    total_stats['games_alivetime'] = {}
    for (game_type_cd, games, alivetime) in games_played:
        total_stats['games'] += games
        total_stats['games_breakdown'][game_type_cd] = games
        total_stats['games_alivetime'][game_type_cd] = alivetime
    
    (total_stats['kills'], total_stats['deaths'], total_stats['suicides'],
     total_stats['alivetime'],) = DBSession.query(
            func.sum(PlayerGameStat.kills),
            func.sum(PlayerGameStat.deaths),
            func.sum(PlayerGameStat.suicides),
            func.sum(PlayerGameStat.alivetime)).\
            filter(PlayerGameStat.player_id == player_id).\
            one()
    
    (total_stats['wins'],) = DBSession.query(
            func.count("*")).\
            filter(Game.game_id == PlayerGameStat.game_id).\
            filter(PlayerGameStat.player_id == player_id).\
            filter(Game.winner == PlayerGameStat.team or PlayerGameStat.rank == 1).\
            one()
    
    ranks = DBSession.query("game_type_cd", "rank", "max_rank").\
            from_statement(
                "select pr.game_type_cd, pr.rank, overall.max_rank "
                "from player_ranks pr,  "
                   "(select game_type_cd, max(rank) max_rank "
                    "from player_ranks  "
                    "group by game_type_cd) overall "
                "where pr.game_type_cd = overall.game_type_cd  "
                "and player_id = :player_id "
                "order by rank").\
            params(player_id=player_id).all()
    
    ranks_dict = {}
    for gtc,rank,max_rank in ranks:
        ranks_dict[gtc] = (rank, max_rank)

    elos = DBSession.query(PlayerElo).\
            filter_by(player_id=player_id).\
            order_by(PlayerElo.elo.desc()).\
            all()
    
    elos_dict = {}
    for elo in elos:
        if elo.games > 32:
            elos_dict[elo.game_type_cd] = elo.elo
    
    data = {
            'player':player,
            'total_stats':total_stats,
            'ranks':ranks_dict,
            'elos':elos_dict,
        }
        
    #print data
    return data


def render_image(data):
    """Render an image from the given data fields."""
    
    width, height = params['width'], params['height']
    output = "output/%s.png" % data['player'].player_id
    
    font = "Xolonium"
    if params['font'] == 1:
        font = "DejaVu Sans"


    ## create background

    surf = C.ImageSurface(C.FORMAT_RGB24, width, height)
    ctx = C.Context(surf)

    # draw background (just plain fillcolor)
    if params['bg'] == 0:
        ctx.rectangle(0, 0, 1, 1);
        ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0);
        ctx.fill();
    
    # draw background image (try to get correct tiling, too)
    if params['bg'] > 0:
        bg = None
        if params['bg'] == 1:
            bg = C.ImageSurface.create_from_png("img/dark_wall.png");
        
        if bg:
            bg_w, bg_h = bg.get_width(), bg.get_height()
            bg_xoff = 0
            while bg_xoff < width:
                bg_yoff = 0
                while bg_yoff < height:
                    ctx.set_source_surface(bg, bg_xoff, bg_yoff);
                    ctx.paint()
                    bg_yoff += bg_h
                bg_xoff += bg_w


    ## draw player's nickname with fancy colors
    
    # fontsize is reduced if width gets too large - TODO: needs finetuning
    ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(18)
    xoff, yoff, tw, th = ctx.text_extents(player.stripped_nick)[:4]
    if tw > 340:
        ctx.set_font_size(16)
    xoff, yoff, tw, th = ctx.text_extents(player.stripped_nick)[:4]
    if tw > 340:
        ctx.set_font_size(14)
    
    # split up nick into colored segments and draw each of them
    qstr = qfont_decode(player.nick).replace('^^', '^')
    txt_xoff = 0
    txt_xpos, txt_ypos = 5,18
    for txt in qstr.split('^'):
        try:
            if txt.startswith('x'):
                r = int(txt[1] * 2, 16) / 255.0
                g = int(txt[2] * 2, 16) / 255.0
                b = int(txt[3] * 2, 16) / 255.0
                hue, light, satur = rgb_to_hls(r, g, b)
                if light < _contrast_threshold:
                    light = _contrast_threshold
                    r, g, b = hls_to_rgb(hue, light, satur)
                txt = txt[4:]
            else:
                r,g,b = _dec_colors[int(txt[0])]
                txt = txt[1:]
        except:
            r,g,b = _dec_colors[7]
        
        if len(txt) < 1:
            # only colorcode and no real text, skip this
            continue
        
        ctx.set_source_rgb(r, g, b)
        ctx.move_to(txt_xpos + txt_xoff, txt_ypos)
        ctx.show_text(txt)

        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        if tw == 0:
            # only whitespaces, use some extra space
            tw += 5*len(txt)
        
        txt_xoff += tw + 1

    ## print elos and ranks
    
    elos = data["elos"]
    ranks = data["ranks"]
    games_x, games_y = 60,35
    games_w = 110       # width of each gametype field
    
    for gt in params['gametypes']:
        ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        txt = "[ %s ]" % gt.upper()
        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        ctx.move_to(games_x-xoff-tw/2,games_y-yoff-th/2)
        ctx.show_text(txt)
        
        ctx.set_line_width(1)
        ctx.move_to(games_x-games_w/2+5, games_y+8);
        ctx.line_to(games_x+games_w/2-5, games_y+8);
        ctx.stroke()
        ctx.move_to(games_x-games_w/2+5, games_y+32);
        ctx.line_to(games_x+games_w/2-5, games_y+32);
        ctx.stroke()
        
        if not elos.has_key(gt) or not ranks.has_key(gt):
            ctx.select_font_face(font, C.FONT_SLANT_ITALIC, C.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(10)
            ctx.set_source_rgb(0.7, 0.7, 0.7)
            txt = "(no stats yet!)"
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(games_x-xoff-tw/2,games_y+22-yoff-th/2)
            ctx.show_text(txt)
        else:
            ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(10)
            ctx.set_source_rgb(1.0, 1.0, 1.0)
            txt = "Elo: %.0f" % round(elos[gt], 0)
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(games_x-xoff-tw/2,games_y+15-yoff-th/2)
            ctx.show_text(txt)
            
            ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(8)
            ctx.set_source_rgb(0.7, 0.7, 0.7)
            txt = "Rank %d of %d" % ranks[gt]
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(games_x-xoff-tw/2,games_y+25-yoff-th/2)
            ctx.show_text(txt)
        
        games_x += games_w


    # print win percentage
    total_stats = data['total_stats']
    total_games = total_stats['games']
    win_x, win_y = 500,18
    
    if total_games > 0 and total_stats['wins'] is not None:
        ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        txt = "Win Percentage"
        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        ctx.move_to(win_x-xoff-tw/2,win_y-yoff-th/2)
        ctx.show_text(txt)
        
        ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12)
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        txt = "%.2f%%" % round(float(total_stats['wins'])/total_games * 100, 2)
        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        ctx.move_to(win_x-xoff-tw/2,win_y+14-yoff-th/2)
        ctx.show_text(txt)

        ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(8)
        ctx.set_source_rgb(0.8, 0.8, 0.8)
        txt = "%d wins" % total_stats["wins"]
        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        ctx.move_to(win_x-xoff-tw/2,win_y+28-yoff-th/2)
        ctx.show_text(txt)
        txt = "%d losses" % (total_games-total_stats['wins'])
        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        ctx.move_to(win_x-xoff-tw/2,win_y+38-yoff-th/2)
        ctx.show_text(txt)

    # print kill/death ratio
    kill_x, kill_y = 400,18
    if total_stats['kills'] > 0 and total_stats['deaths'] > 0:
        ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        txt = "Kill Ratio"
        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        ctx.move_to(kill_x-xoff-tw/2,kill_y-yoff-th/2)
        ctx.show_text(txt)
        
        ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12)
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        txt = "%.3f" % round(float(total_stats['kills'])/total_stats['deaths'], 3)
        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        ctx.move_to(kill_x-xoff-tw/2,kill_y+14-yoff-th/2)
        ctx.show_text(txt)

        ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(8)
        ctx.set_source_rgb(0.8, 0.8, 0.8)
        txt = "%d kills" % total_stats["kills"]
        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        ctx.move_to(kill_x-xoff-tw/2,kill_y+28-yoff-th/2)
        ctx.show_text(txt)
        txt = "%d deaths" % total_stats['deaths']
        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        ctx.move_to(kill_x-xoff-tw/2,kill_y+38-yoff-th/2)
        ctx.show_text(txt)

    # save to PNG
    surf.write_to_png(output)


# environment setup
env = bootstrap('../../../development.ini')
req = env['request']
req.matchdict = {'id':3}

print "Requesting player data from db ..."
start = datetime.now()
players = DBSession.query(Player).\
        filter(Player.player_id == PlayerElo.player_id).\
        filter(Player.nick != None).\
        filter(Player.player_id > 2).\
        filter(Player.active_ind == True).\
        limit(NUM_PLAYERS).all()
stop = datetime.now()
print "Query took %.2f seconds" % (stop-start).total_seconds()

print "Creating badges for %d players ..." % len(players)
start = datetime.now()
data_time, render_time = 0,0
for player in players:
    req.matchdict['id'] = player.player_id
    
    sstart = datetime.now()
    #data = player_info_data(req)
    data = get_data(player)
    sstop = datetime.now()
    data_time += (sstop-sstart).total_seconds()
    
    print "\t#%d (%s)" % (player.player_id, player.stripped_nick)

    sstart = datetime.now()
    render_image(data)
    sstop = datetime.now()
    render_time += (sstop-sstart).total_seconds()

stop = datetime.now()
print "Creating the badges took %.2f seconds (%.2f s per player)" % ((stop-start).total_seconds(), (stop-start).total_seconds()/float(len(players)))
print "Total time for getting data: %.2f s" % data_time
print "Total time for redering images: %.2f s" % render_time

