import re
import zlib, struct
import cairo as C
from colorsys import rgb_to_hls, hls_to_rgb
import sqlalchemy as sa
import sqlalchemy.sql.functions as func
from xonstat.models import *
from xonstat.util import qfont_decode, _all_colors

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


def writepng(filename, buf, width, height):
    width_byte_4 = width * 4
    # fix color ordering (BGR -> RGB)
    for byte in xrange(width*height):
        pos = byte * 4
        buf[pos:pos+4] = buf[pos+2] + buf[pos+1] + buf[pos+0] + buf[pos+3]
    # merge lines
    #raw_data = b"".join(b'\x00' + buf[span:span + width_byte_4] for span in xrange((height - 1) * width * 4, -1, - width_byte_4))
    raw_data = b"".join(b'\x00' + buf[span:span + width_byte_4] for span in range(0, (height-1) * width * 4 + 1, width_byte_4))
    def png_pack(png_tag, data):
        chunk_head = png_tag + data
        return struct.pack("!I", len(data)) + chunk_head + struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head))
    data = b"".join([
        b'\x89PNG\r\n\x1a\n',
        png_pack(b'IHDR', struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)),
        png_pack(b'IDAT', zlib.compress(raw_data, 9)),
        png_pack(b'IEND', b'')])
    f = open(filename, "wb")
    try:
        f.write(data)
    finally:
        f.close()


class Skin:

    # player data, will be filled by get_data()
    data = {}

    # skin parameters, can be overriden by init
    params = {}

    def __init__(self, **params):
        # default parameters
        self.params = {
            'bg':               "dark_wall",    # None - plain; otherwise use given texture
            'bgcolor':          None,           # transparent bg when bgcolor==None
            'overlay':          None,           # add overlay graphic on top of bg
            'font':             "Xolonium",
            'width':            560,
            'height':           70,
            'nick_fontsize':    20,
            'nick_pos':         (5,18),
            'nick_maxwidth':    330,
            'gametype_fontsize':12,
            'gametype_pos':     (60,31),
            'gametype_width':   110,
            'gametype_height':  22,
            'gametype_color':   (1.0, 1.0, 1.0),
            'gametype_text':    "[ %s ]",
            'num_gametypes':    3,
            'nostats_fontsize': 12,
            'nostats_pos':      (60,59),
            'nostats_color':    (0.8, 0.2, 0.2),
            'nostats_angle':    -10,
            'nostats_text':     "no stats yet!",
            'elo_pos':          (60,47),
            'elo_fontsize':     10,
            'elo_color':        (1.0, 1.0, 0.5),
            'elo_text':         "Elo %.0f",
            'rank_fontsize':    8,
            'rank_pos':         (60,57),
            'rank_color':       (0.8, 0.8, 1.0),
            'rank_text':        "Rank %d of %d",
            'wintext_fontsize': 10,
            'wintext_pos':      (508,3),
            'wintext_width':    102,
            'wintext_color':    (0.8, 0.8, 0.8),
            'wintext_bg':       (0.8, 0.8, 0.8, 0.1),
            'wintext_text':     "Win Percentage",
            'winp_fontsize':    12,
            'winp_pos':         (508,19),
            'winp_colortop':    (0.2, 1.0, 1.0),
            'winp_colorbot':    (1.0, 1.0, 0.2),
            'wins_fontsize':    8,
            'wins_pos':         (508,33),
            'wins_color':       (0.6, 0.8, 0.8),
            'loss_fontsize':    8,
            'loss_pos':         (508,43),
            'loss_color':       (0.8, 0.8, 0.6),
            'kdtext_fontsize':  10,
            'kdtext_pos':       (390,3),
            'kdtext_width':     102,
            'kdtext_color':     (0.8, 0.8, 0.8),
            'kdtext_bg':        (0.8, 0.8, 0.8, 0.1),
            'kdtext_text':      "Kill Ratio",
            'kdr_fontsize':     12,
            'kdr_pos':          (392,19),
            'kdr_colortop':     (0.2, 1.0, 0.2),
            'kdr_colorbot':     (1.0, 0.2, 0.2),
            'kills_fontsize':   8,
            'kills_pos':        (392,46),
            'kills_color':      (0.6, 0.8, 0.6),
            'deaths_fontsize':  8,
            'deaths_pos':       (392,56),
            'deaths_color':     (0.8, 0.6, 0.6),
            'ptime_fontsize':   10,
            'ptime_pos':        (451,60),
            'ptime_width':      222,
            'ptime_bg':         (0.8, 0.8, 0.8, 0.5),
            'ptime_color':      (0.1, 0.1, 0.1),
            'ptime_text':       "Playing Time: %s",
        }
        
        for k,v in params.items():
            if self.params.has_key(k):
                self.params[k] = v

    def __getattr__(self, key):
        if self.params.has_key(key):
            return self.params[key]
        return None

    def render_image(self, output_filename):
        """Render an image for the given player id."""

        # setup variables

        player = self.data['player']
        total_stats = self.data['total_stats']
        total_games = total_stats['games']
        elos  = self.data["elos"]
        ranks = self.data["ranks"]

        font = "Xolonium"
        if self.font == 1:
            font = "DejaVu Sans"


        # build image

        surf = C.ImageSurface(C.FORMAT_ARGB32, self.width, self.height)
        ctx = C.Context(surf)
        ctx.set_antialias(C.ANTIALIAS_GRAY)
        
        # draw background
        if self.bg == None:
            if self.bgcolor != None:
                # plain fillcolor, full transparency possible with (1,1,1,0)
                ctx.save()
                ctx.set_operator(C.OPERATOR_SOURCE)
                ctx.rectangle(0, 0, self.width, self.height)
                ctx.set_source_rgba(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
                ctx.fill()
                ctx.restore()
        else:
            try:
                # background texture
                bg = C.ImageSurface.create_from_png("img/%s.png" % self.bg)
                
                # tile image
                if bg:
                    bg_w, bg_h = bg.get_width(), bg.get_height()
                    bg_xoff = 0
                    while bg_xoff < self.width:
                        bg_yoff = 0
                        while bg_yoff < self.height:
                            ctx.set_source_surface(bg, bg_xoff, bg_yoff)
                            #ctx.mask_surface(bg)
                            ctx.paint()
                            bg_yoff += bg_h
                        bg_xoff += bg_w
            except:
                #print "Error: Can't load background texture: %s" % self.bg
                pass

        # draw overlay graphic
        if self.overlay != None:
            try:
                overlay = C.ImageSurface.create_from_png("img/%s.png" % self.overlay)
                ctx.set_source_surface(overlay, 0, 0)
                #ctx.mask_surface(overlay)
                ctx.paint()
            except:
                #print "Error: Can't load overlay texture: %s" % self.overlay
                pass


        ## draw player's nickname with fancy colors
        
        # deocde nick, strip all weird-looking characters
        qstr = qfont_decode(player.nick).replace('^^', '^').replace(u'\x00', '')
        chars = []
        for c in qstr:
            # replace weird characters that make problems - TODO
            if ord(c) < 128:
                chars.append(c)
        qstr = ''.join(chars)
        stripped_nick = strip_colors(qstr.replace(' ', '_'))
        
        # fontsize is reduced if width gets too large
        ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
        shrinknick = 0
        while shrinknick < 10:
            ctx.set_font_size(self.nick_fontsize - shrinknick)
            xoff, yoff, tw, th = ctx.text_extents(stripped_nick)[:4]
            if tw > self.nick_maxwidth:
                shrinknick += 2
                continue
            break

        # determine width of single whitespace for later use
        xoff, yoff, tw, th = ctx.text_extents("_")[:4]
        space_w = tw

        # split nick into colored segments
        xoffset = 0
        _all_colors = re.compile(r'(\^\d|\^x[\dA-Fa-f]{3})')
        parts = _all_colors.split(qstr)
        while len(parts) > 0:
            tag = None
            txt = parts[0]
            if _all_colors.match(txt):
                tag = txt[1:]  # strip leading '^'
                if len(parts) < 2:
                    break
                txt = parts[1]
                del parts[1]
            del parts[0]
                
            if not txt or len(txt) == 0:
                # only colorcode and no real text, skip this
                continue
            
            if tag:
                if tag.startswith('x'):
                    r = int(tag[1] * 2, 16) / 255.0
                    g = int(tag[2] * 2, 16) / 255.0
                    b = int(tag[3] * 2, 16) / 255.0
                    hue, light, satur = rgb_to_hls(r, g, b)
                    if light < _contrast_threshold:
                        light = _contrast_threshold
                        r, g, b = hls_to_rgb(hue, light, satur)
                else:
                    r,g,b = _dec_colors[int(tag[0])]
            else:
                r,g,b = _dec_colors[7]
            
            ctx.set_source_rgb(r, g, b)
            ctx.move_to(self.nick_pos[0] + xoffset, self.nick_pos[1])
            ctx.show_text(txt)

            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            tw += (len(txt)-len(txt.strip())) * space_w  # account for lost whitespaces
            xoffset += tw + 2

        ## print elos and ranks
        
        # show up to three gametypes the player has participated in
        xoffset = 0
        for gt in total_stats['gametypes'][:self.num_gametypes]:
            if self.gametype_pos:
                ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_BOLD)
                ctx.set_font_size(self.gametype_fontsize)
                ctx.set_source_rgb(self.gametype_color[0],self.gametype_color[1],self.gametype_color[2])
                txt = self.gametype_text % gt.upper()
                xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
                ctx.move_to(self.gametype_pos[0]+xoffset-xoff-tw/2, self.gametype_pos[1]-yoff)
                ctx.show_text(txt)

                # draw lines - TODO put this in overlay graphic
                if self.overlay == None:
                    old_aa = ctx.get_antialias()
                    ctx.set_antialias(C.ANTIALIAS_NONE)
                    ctx.set_source_rgb(0.8, 0.8, 0.8)
                    ctx.set_line_width(1)
                    ctx.move_to(self.gametype_pos[0]+xoffset-self.gametype_width/2+5, self.gametype_pos[1]+14)
                    ctx.line_to(self.gametype_pos[0]+xoffset+self.gametype_width/2-5, self.gametype_pos[1]+14)
                    ctx.stroke()
                    ctx.move_to(self.gametype_pos[0]+xoffset-self.gametype_width/2+5, self.gametype_pos[1]+self.gametype_height+14)
                    ctx.line_to(self.gametype_pos[0]+xoffset+self.gametype_width/2-5, self.gametype_pos[1]+self.gametype_height+14)
                    ctx.stroke()
                    ctx.set_antialias(old_aa)

            if not elos.has_key(gt) or not ranks.has_key(gt):
                if self.nostats_pos:
                    ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_BOLD)
                    ctx.set_font_size(self.nostats_fontsize)
                    ctx.set_source_rgb(self.nostats_color[0],self.nostats_color[1],self.nostats_color[2])
                    txt = self.nostats_text
                    xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
                    ctx.move_to(self.nostats_pos[0]+xoffset-xoff-tw/2, self.nostats_pos[1]-yoff)
                    ctx.save()
                    ctx.rotate(math.radians(self.nostats_angle))
                    ctx.show_text(txt)
                    ctx.restore()
            else:
                if self.elo_pos:
                    ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
                    ctx.set_font_size(self.elo_fontsize)
                    ctx.set_source_rgb(self.elo_color[0], self.elo_color[1], self.elo_color[2])
                    txt = self.elo_text % round(elos[gt], 0)
                    xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
                    ctx.move_to(self.elo_pos[0]+xoffset-xoff-tw/2, self.elo_pos[1]-yoff)
                    ctx.show_text(txt)
                if  self.rank_pos:
                    ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
                    ctx.set_font_size(self.rank_fontsize)
                    ctx.set_source_rgb(self.rank_color[0], self.rank_color[1], self.rank_color[2])
                    txt = self.rank_text % ranks[gt]
                    xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
                    ctx.move_to(self.rank_pos[0]+xoffset-xoff-tw/2, self.rank_pos[1]-yoff)
                    ctx.show_text(txt)
            
            xoffset += self.gametype_width


        # print win percentage

        if self.wintext_pos:
            if self.overlay == None:
                ctx.rectangle(self.wintext_pos[0]-self.wintext_width/2, self.wintext_pos[1]-self.wintext_fontsize/2+1,
                        self.wintext_width, self.wintext_fontsize+4)
                ctx.set_source_rgba(self.wintext_bg[0], self.wintext_bg[1], self.wintext_bg[2], self.wintext_bg[3])
                ctx.fill()

            ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(self.wintext_fontsize)
            ctx.set_source_rgb(self.wintext_color[0], self.wintext_color[1], self.wintext_color[2])
            txt = self.wintext_text
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(self.wintext_pos[0]-xoff-tw/2, self.wintext_pos[1]-yoff)
            ctx.show_text(txt)

        wins, losses = total_stats["wins"], total_games-total_stats["wins"]
        txt = "???"
        try:
            ratio = float(wins)/total_games
            txt = "%.2f%%" % round(ratio * 100, 2)
        except:
            ratio = 0
        
        if self.winp_pos:
            ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_BOLD)
            ctx.set_font_size(self.winp_fontsize)
            r = ratio*self.winp_colortop[0] + (1-ratio)*self.winp_colorbot[0]
            g = ratio*self.winp_colortop[1] + (1-ratio)*self.winp_colorbot[1]
            b = ratio*self.winp_colortop[2] + (1-ratio)*self.winp_colorbot[2]
            ctx.set_source_rgb(r, g, b)
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(self.winp_pos[0]-xoff-tw/2, self.winp_pos[1]-yoff)
            ctx.show_text(txt)

        if self.wins_pos:
            ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(self.wins_fontsize)
            ctx.set_source_rgb(self.wins_color[0], self.wins_color[1], self.wins_color[2])
            txt = "%d win" % wins
            if wins != 1:
                txt += "s"
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(self.wins_pos[0]-xoff-tw/2, self.wins_pos[1]-yoff)
            ctx.show_text(txt)

        if self.loss_pos:
            ctx.set_font_size(self.loss_fontsize)
            ctx.set_source_rgb(self.loss_color[0], self.loss_color[1], self.loss_color[2])
            txt = "%d loss" % losses
            if losses != 1:
                txt += "es"
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(self.loss_pos[0]-xoff-tw/2, self.loss_pos[1]-yoff)
            ctx.show_text(txt)


        # print kill/death ratio

        if self.kdtext_pos:
            if self.overlay == None:
                ctx.rectangle(self.kdtext_pos[0]-self.kdtext_width/2, self.kdtext_pos[1]-self.kdtext_fontsize/2+1,
                        self.kdtext_width, self.kdtext_fontsize+4)
                ctx.set_source_rgba(self.kdtext_bg[0], self.kdtext_bg[1], self.kdtext_bg[2], self.kdtext_bg[3])
                ctx.fill()

            ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(self.kdtext_fontsize)
            ctx.set_source_rgb(self.kdtext_color[0], self.kdtext_color[1], self.kdtext_color[2])
            txt = self.kdtext_text
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(self.kdtext_pos[0]-xoff-tw/2, self.kdtext_pos[1]-yoff)
            ctx.show_text(txt)
        
        kills, deaths = total_stats['kills'] , total_stats['deaths'] 
        txt = "???"
        try:
            ratio = float(kills)/deaths
            txt = "%.3f" % round(ratio, 3)
        except:
            ratio = 0

        if self.kdr_pos:
            ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_BOLD)
            ctx.set_font_size(self.kdr_fontsize)
            nr = ratio / 2.0
            if nr > 1:
                nr = 1
            r = nr*self.kdr_colortop[0] + (1-nr)*self.kdr_colorbot[0]
            g = nr*self.kdr_colortop[1] + (1-nr)*self.kdr_colorbot[1]
            b = nr*self.kdr_colortop[2] + (1-nr)*self.kdr_colorbot[2]
            ctx.set_source_rgb(r, g, b)
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(self.kdr_pos[0]-xoff-tw/2, self.kdr_pos[1]-yoff)
            ctx.show_text(txt)

        if self.kills_pos:
            ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(self.kills_fontsize)
            ctx.set_source_rgb(self.kills_color[0], self.kills_color[1], self.kills_color[2])
            txt = "%d kill" % kills
            if kills != 1:
                txt += "s"
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(self.kills_pos[0]-xoff-tw/2, self.kills_pos[1]+yoff)
            ctx.show_text(txt)

        if self.deaths_pos:
            ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(self.deaths_fontsize)
            ctx.set_source_rgb(self.deaths_color[0], self.deaths_color[1], self.deaths_color[2])
            txt = "%d death" % deaths
            if deaths != 1:
                txt += "s"
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(self.deaths_pos[0]-xoff-tw/2, self.deaths_pos[1]+yoff)
            ctx.show_text(txt)


        # print playing time

        if self.ptime_pos:
            if self.overlay == None:
                ctx.rectangle( self.ptime_pos[0]-self.ptime_width/2, self.ptime_pos[1]-self.ptime_fontsize/2+1,
                        self.ptime_width, self.ptime_fontsize+4)
                ctx.set_source_rgba(self.ptime_bg[0], self.ptime_bg[1], self.ptime_bg[2], self.ptime_bg[2])
                ctx.fill()

            ctx.select_font_face(font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(self.ptime_fontsize)
            ctx.set_source_rgb(self.ptime_color[0], self.ptime_color[1], self.ptime_color[2])
            txt = self.ptime_text % str(total_stats['alivetime'])
            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.move_to(self.ptime_pos[0]-xoff-tw/2, self.ptime_pos[1]-yoff)
            ctx.show_text(txt)


        # save to PNG
        #surf.write_to_png(output_filename)
        surf.flush()
        imgdata = surf.get_data()
        writepng(output_filename, imgdata, self.width, self.height)


    def get_data(self, player):
        """Return player data as dict.

        This function is similar to the function in player.py but more optimized
        for this purpose.
        """

        # total games
        # wins/losses
        # kills/deaths
        # duel/dm/tdm/ctf elo + rank

        player_id = player.player_id

        games_played = DBSession.query(
                Game.game_type_cd, func.count(), func.sum(PlayerGameStat.alivetime)).\
                filter(Game.game_id == PlayerGameStat.game_id).\
                filter(PlayerGameStat.player_id == player_id).\
                group_by(Game.game_type_cd).\
                order_by(func.count().desc()).\
                limit(3).all()  # limit to 3 gametypes!

        total_stats = {}
        total_stats['games'] = 0
        total_stats['games_breakdown'] = {}  # this is a dictionary inside a dictionary .. dictception?
        total_stats['games_alivetime'] = {}
        total_stats['gametypes'] = []
        for (game_type_cd, games, alivetime) in games_played:
            total_stats['games'] += games
            total_stats['gametypes'].append(game_type_cd)
            total_stats['games_breakdown'][game_type_cd] = games
            total_stats['games_alivetime'][game_type_cd] = alivetime

        (total_stats['kills'], total_stats['deaths'], total_stats['alivetime'],) = DBSession.query(
                func.sum(PlayerGameStat.kills),
                func.sum(PlayerGameStat.deaths),
                func.sum(PlayerGameStat.alivetime)).\
                filter(PlayerGameStat.player_id == player_id).\
                one()

    #    (total_stats['wins'],) = DBSession.query(
    #            func.count("*")).\
    #            filter(Game.game_id == PlayerGameStat.game_id).\
    #            filter(PlayerGameStat.player_id == player_id).\
    #            filter(Game.winner == PlayerGameStat.team or PlayerGameStat.rank == 1).\
    #            one()

        (total_stats['wins'],) = DBSession.\
                query("total_wins").\
                from_statement(
                    "select count(*) total_wins "
                    "from games g, player_game_stats pgs "
                    "where g.game_id = pgs.game_id "
                    "and player_id=:player_id "
                    "and (g.winner = pgs.team or pgs.rank = 1)"
                ).params(player_id=player_id).one()

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

        self.data = {
                'player':player,
                'total_stats':total_stats,
                'ranks':ranks_dict,
                'elos':elos_dict,
            }

