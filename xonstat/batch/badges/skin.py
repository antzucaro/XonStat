import math
import re
import zlib, struct
import cairo as C
from colorsys import rgb_to_hls, hls_to_rgb
from xonstat.util import strip_colors, qfont_decode, _all_colors

# similar to html_colors() from util.py
_contrast_threshold = 0.5

# standard colorset (^0 ... ^9)
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


# function to write compressed PNG (using zlib)
def write_png(filename, buf, width, height):
    width_byte_4 = width * 4
    # fix color ordering (BGRA -> RGBA)
    for byte in xrange(width*height):
        pos = byte * 4
        buf[pos:pos+4] = buf[pos+2] + buf[pos+1] + buf[pos+0] + buf[pos+3]
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

    # skin parameters, can be overriden by init
    params = {}

    # skin name
    name = ""

    # render context
    ctx = None

    def __init__(self, name, **params):
        # default parameters
        self.name = name
        self.params = {
            'bg':               None,           # None - plain; otherwise use given texture
            'bgcolor':          None,           # transparent bg when bgcolor==None
            'overlay':          None,           # add overlay graphic on top of bg
            'font':             "Xolonium",
            'width':            560,
            'height':           70,
            'nick_fontsize':    20,
            'nick_pos':         (56,18),
            'nick_maxwidth':    280,
            'gametype_fontsize':10,
            'gametype_pos':     (101,33),
            'gametype_width':   94,
            'gametype_height':  0,
            'gametype_color':   (0.9, 0.9, 0.9),
            'gametype_text':    "%s",
            'gametype_align':   0,
            'gametype_upper':   True,
            'num_gametypes':    3,
            'nostats_fontsize': 12,
            'nostats_pos':      (101,59),
            'nostats_color':    (0.8, 0.2, 0.1),
            'nostats_angle':    -10,
            'nostats_text':     "no stats yet!",
            'nostats_align':    0,
            'elo_pos':          (101,47),
            'elo_fontsize':     10,
            'elo_color':        (1.0, 1.0, 0.5),
            'elo_text':         "Elo %.0f",
            'elo_align':        0,
            'rank_fontsize':    8,
            'rank_pos':         (101,58),
            'rank_color':       (0.8, 0.8, 1.0),
            'rank_text':        "Rank %d of %d",
            'rank_align':       0,
            'wintext_fontsize': 10,
            'wintext_pos':      (508,3),
            'wintext_color':    (0.8, 0.8, 0.8),
            'wintext_text':     "Win Percentage",
            'wintext_align':    0,
            'winp_fontsize':    12,
            'winp_pos':         (508,19),
            'winp_colortop':    (0.2, 1.0, 1.0),
            'winp_colormid':    (0.4, 0.8, 0.4),
            'winp_colorbot':    (1.0, 1.0, 0.2),
            'winp_align':       0,
            'wins_fontsize':    8,
            'wins_pos':         (508,33),
            'wins_color':       (0.6, 0.8, 0.8),
            'wins_align':       0,
            'loss_fontsize':    8,
            'loss_pos':         (508,43),
            'loss_color':       (0.8, 0.8, 0.6),
            'loss_align':       0,
            'kdtext_fontsize':  10,
            'kdtext_pos':       (390,3),
            'kdtext_width':     102,
            'kdtext_color':     (0.8, 0.8, 0.8),
            'kdtext_bg':        (0.8, 0.8, 0.8, 0.1),
            'kdtext_text':      "Kill Ratio",
            'kdtext_align':     0,
            'kdr_fontsize':     12,
            'kdr_pos':          (392,19),
            'kdr_colortop':     (0.2, 1.0, 0.2),
            'kdr_colormid':     (0.8, 0.8, 0.4),
            'kdr_colorbot':     (1.0, 0.2, 0.2),
            'kdr_align':        0,
            'kills_fontsize':   8,
            'kills_pos':        (392,33),
            'kills_color':      (0.6, 0.8, 0.6),
            'kills_align':      0,
            'deaths_fontsize':  8,
            'deaths_pos':       (392,43),
            'deaths_color':     (0.8, 0.6, 0.6),
            'deaths_align':     0,
            'ptime_fontsize':   10,
            'ptime_pos':        (451,60),
            'ptime_color':      (0.1, 0.1, 0.1),
            'ptime_text':       "Playing Time: %s",
            'ptime_align':      0,
        }
        
        for k,v in params.items():
            if self.params.has_key(k):
                self.params[k] = v

    def __str__(self):
        return self.name

    def __getattr__(self, key):
        if self.params.has_key(key):
            return self.params[key]
        return None

    def show_text(self, txt, pos, align=0, angle=None, offset=(0,0)):
        ctx = self.ctx

        xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
        if align > 0:
            ctx.move_to(pos[0]+offset[0]-xoff,      pos[1]+offset[1]-yoff)
        elif align < 0:
            ctx.move_to(pos[0]+offset[0]-xoff-tw,   pos[1]+offset[1]-yoff)
        else:
            ctx.move_to(pos[0]+offset[0]-xoff-tw/2, pos[1]+offset[1]-yoff)
        ctx.save()
        if angle:
            ctx.rotate(math.radians(angle))
        ctx.show_text(txt)
        ctx.restore()

    def set_font(self, fontsize, color, bold=False, italic=False):
        ctx    = self.ctx
        font   = self.font
        slant  = C.FONT_SLANT_ITALIC if italic else C.FONT_SLANT_NORMAL
        weight = C.FONT_WEIGHT_BOLD  if bold   else C.FONT_WEIGHT_NORMAL

        ctx.select_font_face(font, slant, weight)
        ctx.set_font_size(fontsize)
        if len(color) == 1:
            ctx.set_source_rgb(color[0], color[0], color[0])
        elif len(color) == 3:
            ctx.set_source_rgb(color[0], color[1], color[2])
        elif len(color) == 4:
            ctx.set_source_rgba(color[0], color[1], color[2], color[3])
        else:
            ctx.set_source_rgb(1, 1, 1)

    def render_image(self, data, output_filename):
        """Render an image for the given player id."""

        # setup variables

        player          = data.player
        elos            = data.elos
        ranks           = data.ranks
        #games           = data.total_stats['games']
        wins, losses    = data.total_stats['wins'], data.total_stats['losses']
        games           = wins + losses
        kills, deaths   = data.total_stats['kills'], data.total_stats['deaths']
        alivetime       = data.total_stats['alivetime']


        # build image

        surf = C.ImageSurface(C.FORMAT_ARGB32, self.width, self.height)
        ctx = C.Context(surf)
        self.ctx = ctx
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
        ctx.select_font_face(self.font, C.FONT_SLANT_NORMAL, C.FONT_WEIGHT_NORMAL)
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

            xoff, yoff, tw, th = ctx.text_extents(txt)[:4]
            ctx.set_source_rgb(r, g, b)
            ctx.move_to(self.nick_pos[0] + xoffset - xoff, self.nick_pos[1])
            ctx.show_text(txt)

            tw += (len(txt)-len(txt.strip())) * space_w  # account for lost whitespaces
            xoffset += tw + 2

        ## print elos and ranks
        
        xoffset, yoffset = 0, 0
        count = 0
        for gt in data.total_stats['gametypes'][:self.num_gametypes]:
            if not elos.has_key(gt) or not ranks.has_key(gt):
                continue
            count += 1
        
        # re-align segments if less than max. gametypes are shown
        if count > 0:
            if count < self.num_gametypes:
                diff = self.num_gametypes - count
                if diff % 2 == 0:
                    xoffset += (diff-1) * self.gametype_width
                    yoffset += (diff-1) * self.gametype_height
                else:
                    xoffset += 0.5 * diff * self.gametype_width
                    yoffset += 0.5 * diff * self.gametype_height
        
            # show a number gametypes the player has participated in
            for gt in data.total_stats['gametypes'][:self.num_gametypes]:
                if not elos.has_key(gt) or not ranks.has_key(gt):
                    continue

                offset = (xoffset, yoffset)
                if self.gametype_pos:
                    if self.gametype_upper:
                        txt = self.gametype_text % gt.upper()
                    else:
                        txt = self.gametype_text % gt.lower()
                    self.set_font(self.gametype_fontsize, self.gametype_color, bold=True)
                    self.show_text(txt, self.gametype_pos, self.gametype_align, offset=offset)

                if self.elo_pos:
                    txt = self.elo_text % round(elos[gt], 0)
                    self.set_font(self.elo_fontsize, self.elo_color)
                    self.show_text(txt, self.elo_pos, self.elo_align, offset=offset)
                if  self.rank_pos:
                    txt = self.rank_text % ranks[gt]
                    self.set_font(self.rank_fontsize, self.rank_color)
                    self.show_text(txt, self.rank_pos, self.rank_align, offset=offset)

                xoffset += self.gametype_width
                yoffset += self.gametype_height
        else:
            if self.nostats_pos:
                xoffset += (self.num_gametypes-2) * self.gametype_width
                yoffset += (self.num_gametypes-2) * self.gametype_height
                offset = (xoffset, yoffset)

                txt = self.nostats_text
                self.set_font(self.nostats_fontsize, self.nostats_color, bold=True)
                self.show_text(txt, self.nostats_pos, self.nostats_align, angle=self.nostats_angle, offset=offset)


        # print win percentage

        if self.wintext_pos:
            txt = self.wintext_text
            self.set_font(self.wintext_fontsize, self.wintext_color)
            self.show_text(txt, self.wintext_pos, self.wintext_align)

        txt = "???"
        try:
            ratio = float(wins)/games
            txt = "%.2f%%" % round(ratio * 100, 2)
        except:
            ratio = 0
        
        if self.winp_pos:
            if ratio >= 0.5:
                nr = 2*(ratio-0.5)
                r = nr*self.winp_colortop[0] + (1-nr)*self.winp_colormid[0]
                g = nr*self.winp_colortop[1] + (1-nr)*self.winp_colormid[1]
                b = nr*self.winp_colortop[2] + (1-nr)*self.winp_colormid[2]
            else:
                nr = 2*ratio
                r = nr*self.winp_colormid[0] + (1-nr)*self.winp_colorbot[0]
                g = nr*self.winp_colormid[1] + (1-nr)*self.winp_colorbot[1]
                b = nr*self.winp_colormid[2] + (1-nr)*self.winp_colorbot[2]
            self.set_font(self.winp_fontsize, (r,g,b), bold=True)
            self.show_text(txt, self.winp_pos, self.winp_align)

        if self.wins_pos:
            txt = "%d win" % wins
            if wins != 1:
                txt += "s"
            self.set_font(self.wins_fontsize, self.wins_color)
            self.show_text(txt, self.wins_pos, self.wins_align)

        if self.loss_pos:
            txt = "%d loss" % losses
            if losses != 1:
                txt += "es"
            self.set_font(self.loss_fontsize, self.loss_color)
            self.show_text(txt, self.loss_pos, self.loss_align)


        # print kill/death ratio

        if self.kdtext_pos:
            txt = self.kdtext_text
            self.set_font(self.kdtext_fontsize, self.kdtext_color)
            self.show_text(txt, self.kdtext_pos, self.kdtext_align)
        
        txt = "???"
        try:
            ratio = float(kills)/deaths
            txt = "%.3f" % round(ratio, 3)
        except:
            ratio = 0

        if self.kdr_pos:
            if ratio >= 1.0:
                nr = ratio-1.0
                if nr > 1:
                    nr = 1
                r = nr*self.kdr_colortop[0] + (1-nr)*self.kdr_colormid[0]
                g = nr*self.kdr_colortop[1] + (1-nr)*self.kdr_colormid[1]
                b = nr*self.kdr_colortop[2] + (1-nr)*self.kdr_colormid[2]
            else:
                nr = ratio
                r = nr*self.kdr_colormid[0] + (1-nr)*self.kdr_colorbot[0]
                g = nr*self.kdr_colormid[1] + (1-nr)*self.kdr_colorbot[1]
                b = nr*self.kdr_colormid[2] + (1-nr)*self.kdr_colorbot[2]
            self.set_font(self.kdr_fontsize, (r,g,b), bold=True)
            self.show_text(txt, self.kdr_pos, self.kdr_align)

        if self.kills_pos:
            txt = "%d kill" % kills
            if kills != 1:
                txt += "s"
            self.set_font(self.kills_fontsize, self.kills_color)
            self.show_text(txt, self.kills_pos, self.kills_align)

        if self.deaths_pos:
            txt = ""
            if deaths is not None:
                txt = "%d death" % deaths
                if deaths != 1:
                    txt += "s"
            self.set_font(self.deaths_fontsize, self.deaths_color)
            self.show_text(txt, self.deaths_pos, self.deaths_align)


        # print playing time

        if self.ptime_pos:
            txt = self.ptime_text % str(alivetime)
            self.set_font(self.ptime_fontsize, self.ptime_color)
            self.show_text(txt, self.ptime_pos, self.ptime_align)


        # save to PNG
        #surf.write_to_png(output_filename)
        surf.flush()
        imgdata = surf.get_data()
        write_png(output_filename, imgdata, self.width, self.height)

