import sys
import logging
import pyramid.httpexceptions
import pyramid.url
import re
from colorsys import rgb_to_hls, hls_to_rgb
from cgi import escape as html_escape
from datetime import datetime, timedelta
from decimal import Decimal
from collections import namedtuple
from xonstat.d0_blind_id import d0_blind_id_verify


log = logging.getLogger(__name__)


# Map of old weapons codes to new ones
weapon_map = {
  "grenadelauncher": "mortar", 
  "laser": "blaster", 
  "minstanex": "vaporizer", 
  "nex": "vortex", 
  "rocketlauncher": "devastator", 
  "uzi": "machinegun", 
}


# Map of special chars to ascii from Darkplace's console.c.
_qfont_ascii_table = [
 '\0', '#',  '#',  '#',  '#',  '.',  '#',  '#',
 '#',  '\t', '\n', '#',  ' ',  '\r', '.',  '.',
 '[',  ']',  '0',  '1',  '2',  '3',  '4',  '5',
 '6',  '7',  '8',  '9',  '.',  '<',  '=',  '>',
 ' ',  '!',  '"',  '#',  '$',  '%',  '&',  '\'',
 '(',  ')',  '*',  '+',  ',',  '-',  '.',  '/',
 '0',  '1',  '2',  '3',  '4',  '5',  '6',  '7',
 '8',  '9',  ':',  ';',  '<',  '=',  '>',  '?',
 '@',  'A',  'B',  'C',  'D',  'E',  'F',  'G',
 'H',  'I',  'J',  'K',  'L',  'M',  'N',  'O',
 'P',  'Q',  'R',  'S',  'T',  'U',  'V',  'W',
 'X',  'Y',  'Z',  '[',  '\\', ']',  '^',  '_',
 '`',  'a',  'b',  'c',  'd',  'e',  'f',  'g',
 'h',  'i',  'j',  'k',  'l',  'm',  'n',  'o',
 'p',  'q',  'r',  's',  't',  'u',  'v',  'w',
 'x',  'y',  'z',  '{',  '|',  '}',  '~',  '<',

 '<',  '=',  '>',  '#',  '#',  '.',  '#',  '#',
 '#',  '#',  ' ',  '#',  ' ',  '>',  '.',  '.',
 '[',  ']',  '0',  '1',  '2',  '3',  '4',  '5',
 '6',  '7',  '8',  '9',  '.',  '<',  '=',  '>',
 ' ',  '!',  '"',  '#',  '$',  '%',  '&',  '\'',
 '(',  ')',  '*',  '+',  ',',  '-',  '.',  '/',
 '0',  '1',  '2',  '3',  '4',  '5',  '6',  '7',
 '8',  '9',  ':',  ';',  '<',  '=',  '>',  '?',
 '@',  'A',  'B',  'C',  'D',  'E',  'F',  'G',
 'H',  'I',  'J',  'K',  'L',  'M',  'N',  'O',
 'P',  'Q',  'R',  'S',  'T',  'U',  'V',  'W',
 'X',  'Y',  'Z',  '[',  '\\', ']',  '^',  '_',
 '`',  'a',  'b',  'c',  'd',  'e',  'f',  'g',
 'h',  'i',  'j',  'k',  'l',  'm',  'n',  'o',
 'p',  'q',  'r',  's',  't',  'u',  'v',  'w',
 'x',  'y',  'z',  '{',  '|',  '}',  '~',  '<'
]

_qfont_unicode_glyphs = [
   u'\u0020',       u'\u0020',       u'\u2014',       u'\u0020',
   u'\u005F',       u'\u2747',       u'\u2020',       u'\u00B7',
   u'\U0001F52B',   u'\u0020',       u'\u0020',       u'\u25A0',
   u'\u2022',       u'\u2192',       u'\u2748',       u'\u2748',
   u'\u005B',       u'\u005D',       u'\U0001F47D',   u'\U0001F603',
   u'\U0001F61E',   u'\U0001F635',   u'\U0001F615',   u'\U0001F60A',
   u'\u00AB',       u'\u00BB',       u'\u2022',       u'\u203E',
   u'\u2748',       u'\u25AC',       u'\u25AC',       u'\u25AC',
   u'\u0020',       u'\u0021',       u'\u0022',       u'\u0023',
   u'\u0024',       u'\u0025',       u'\u0026',       u'\u0027',
   u'\u0028',       u'\u0029',       u'\u00D7',       u'\u002B',
   u'\u002C',       u'\u002D',       u'\u002E',       u'\u002F',
   u'\u0030',       u'\u0031',       u'\u0032',       u'\u0033',
   u'\u0034',       u'\u0035',       u'\u0036',       u'\u0037',
   u'\u0038',       u'\u0039',       u'\u003A',       u'\u003B',
   u'\u003C',       u'\u003D',       u'\u003E',       u'\u003F',
   u'\u0040',       u'\u0041',       u'\u0042',       u'\u0043',
   u'\u0044',       u'\u0045',       u'\u0046',       u'\u0047',
   u'\u0048',       u'\u0049',       u'\u004A',       u'\u004B',
   u'\u004C',       u'\u004D',       u'\u004E',       u'\u004F',
   u'\u0050',       u'\u0051',       u'\u0052',       u'\u0053',
   u'\u0054',       u'\u0055',       u'\u0056',       u'\u0057',
   u'\u0058',       u'\u0059',       u'\u005A',       u'\u005B',
   u'\u005C',       u'\u005D',       u'\u005E',       u'\u005F',
   u'\u0027',       u'\u0061',       u'\u0062',       u'\u0063',
   u'\u0064',       u'\u0065',       u'\u0066',       u'\u0067',
   u'\u0068',       u'\u0069',       u'\u006A',       u'\u006B',
   u'\u006C',       u'\u006D',       u'\u006E',       u'\u006F',
   u'\u0070',       u'\u0071',       u'\u0072',       u'\u0073',
   u'\u0074',       u'\u0075',       u'\u0076',       u'\u0077',
   u'\u0078',       u'\u0079',       u'\u007A',       u'\u007B',
   u'\u007C',       u'\u007D',       u'\u007E',       u'\u2190',
   u'\u003C',       u'\u003D',       u'\u003E',       u'\U0001F680',
   u'\u00A1',       u'\u004F',       u'\u0055',       u'\u0049',
   u'\u0043',       u'\u00A9',       u'\u00AE',       u'\u25A0',
   u'\u00BF',       u'\u25B6',       u'\u2748',       u'\u2748',
   u'\u2772',       u'\u2773',       u'\U0001F47D',   u'\U0001F603',
   u'\U0001F61E',   u'\U0001F635',   u'\U0001F615',   u'\U0001F60A',
   u'\u00AB',       u'\u00BB',       u'\u2747',       u'\u0078',
   u'\u2748',       u'\u2014',       u'\u2014',       u'\u2014',
   u'\u0020',       u'\u0021',       u'\u0022',       u'\u0023',
   u'\u0024',       u'\u0025',       u'\u0026',       u'\u0027',
   u'\u0028',       u'\u0029',       u'\u002A',       u'\u002B',
   u'\u002C',       u'\u002D',       u'\u002E',       u'\u002F',
   u'\u0030',       u'\u0031',       u'\u0032',       u'\u0033',
   u'\u0034',       u'\u0035',       u'\u0036',       u'\u0037',
   u'\u0038',       u'\u0039',       u'\u003A',       u'\u003B',
   u'\u003C',       u'\u003D',       u'\u003E',       u'\u003F',
   u'\u0040',       u'\u0041',       u'\u0042',       u'\u0043',
   u'\u0044',       u'\u0045',       u'\u0046',       u'\u0047',
   u'\u0048',       u'\u0049',       u'\u004A',       u'\u004B',
   u'\u004C',       u'\u004D',       u'\u004E',       u'\u004F',
   u'\u0050',       u'\u0051',       u'\u0052',       u'\u0053',
   u'\u0054',       u'\u0055',       u'\u0056',       u'\u0057',
   u'\u0058',       u'\u0059',       u'\u005A',       u'\u005B',
   u'\u005C',       u'\u005D',       u'\u005E',       u'\u005F',
   u'\u0027',       u'\u0041',       u'\u0042',       u'\u0043',
   u'\u0044',       u'\u0045',       u'\u0046',       u'\u0047',
   u'\u0048',       u'\u0049',       u'\u004A',       u'\u004B',
   u'\u004C',       u'\u004D',       u'\u004E',       u'\u004F',
   u'\u0050',       u'\u0051',       u'\u0052',       u'\u0053',
   u'\u0054',       u'\u0055',       u'\u0056',       u'\u0057',
   u'\u0058',       u'\u0059',       u'\u005A',       u'\u007B',
   u'\u007C',       u'\u007D',       u'\u007E',       u'\u25C0',
]

# Hex-colored spans for decimal color codes ^0 - ^9
_dec_spans = [
 "<span style='color:rgb(128,128,128)'>",
 "<span style='color:rgb(255,0,0)'>",
 "<span style='color:rgb(51,255,0)'>",
 "<span style='color:rgb(255,255,0)'>",
 "<span style='color:rgb(51,102,255)'>",
 "<span style='color:rgb(51,255,255)'>",
 "<span style='color:rgb(255,51,102)'>",
 "<span style='color:rgb(255,255,255)'>",
 "<span style='color:rgb(153,153,153)'>",
 "<span style='color:rgb(128,128,128)'>"
]

# Color code patterns
_all_colors = re.compile(r'\^(\d|x[\dA-Fa-f]{3})')
_dec_colors = re.compile(r'\^(\d)')
_hex_colors = re.compile(r'\^x([\dA-Fa-f])([\dA-Fa-f])([\dA-Fa-f])')

# On a light scale of 0 (black) to 1.0 (white)
_contrast_threshold = 0.5


def qfont_decode(qstr='', glyph_translation=False):
    """ Convert the qfont characters in a string to ascii.

        glyph_translation - determines whether to convert the unicode characters to
                   their ascii counterparts (if False, the default) or to
                   the mapped glyph in the Xolonium font (if True).
    """
    if qstr == None:
        qstr = ''
    chars = []
    for c in qstr:
        if u'\ue000' <= c <= u'\ue0ff':
            if glyph_translation:
                c = _qfont_unicode_glyphs[ord(c) - 0xe000]
            else:
                c = _qfont_ascii_table[ord(c) - 0xe000]
        chars.append(c)
    return ''.join(chars)


def strip_colors(qstr=''):
    if qstr == None:
        qstr = ''
    return _all_colors.sub('', qstr)


def hex_repl(match):
    """Convert Darkplaces hex color codes to CSS rgb.
    Brighten colors with HSL light value less than 50%"""

    # Extend hex char to 8 bits and to 0.0-1.0 scale
    r = int(match.group(1) * 2, 16) / 255.0
    g = int(match.group(2) * 2, 16) / 255.0
    b = int(match.group(3) * 2, 16) / 255.0

    # Check if color is too dark
    hue, light, satur = rgb_to_hls(r, g, b)
    if light < _contrast_threshold:
        light = _contrast_threshold
        r, g, b = hls_to_rgb(hue, light, satur)

    # Convert back to 0-255 scale for css
    return '<span style="color:rgb(%d,%d,%d)">' % (255 * r, 255 * g, 255 * b)


def html_colors(qstr='', limit=None):
    qstr = html_escape(qfont_decode(qstr, glyph_translation=True))
    qstr = qstr.replace('^^', '^')

    if limit is not None and limit > 0:
        qstr = limit_printable_characters(qstr, limit)

    html = _dec_colors.sub(lambda match: _dec_spans[int(match.group(1))], qstr)
    html = _hex_colors.sub(hex_repl, html)
    return html + "</span>" * len(_all_colors.findall(qstr))


def limit_printable_characters(qstr, limit):
    # initialize assuming all printable characters
    pc = [1 for i in range(len(qstr))]

    groups = _all_colors.finditer(qstr)
    for g in groups:
        pc[g.start():g.end()] = [0 for i in range(g.end() - g.start())]

    # printable characters in the string is less than or equal to what was requested
    if limit >= len(qstr) or sum(pc) <= limit:
        return qstr
    else:
        sumpc = 0
        for i,v in enumerate(pc):
            sumpc += v
            if sumpc == limit:
                return qstr[0:i+1]


def page_url(page):
    return pyramid.url.current_route_url(request, page=page, _query=request.GET)


def pretty_date(time=False):
    '''Returns a human-readable relative date.'''
    now = datetime.utcnow()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        print "not a time value"
        diff = now - now

    dim = round(diff.seconds/60.0 + diff.days*1440.0)

    if dim == 0:
        return "less than a minute ago"
    elif dim == 1:
        return "1 minute ago"
    elif dim >= 2 and dim <= 44:
        return "{0} minutes ago".format(int(dim))
    elif dim >= 45 and dim <= 89:
        return "about 1 hour ago"
    elif dim >= 90 and dim <= 1439:
        return "about {0} hours ago".format(int(round(dim/60.0)))
    elif dim >= 1440 and dim <= 2519:
        return "1 day ago"
    elif dim >= 2520 and dim <= 43199:
        return "{0} days ago".format(int(round(dim/1440.0)))
    elif dim >= 43200 and dim <= 86399:
        return "about 1 month ago"
    elif dim >= 86400 and dim <= 525599:
        return "{0} months ago".format(int(round(dim/43200.0)))
    elif dim >= 525600 and dim <= 655199:
        return "about 1 year ago"
    elif dim >= 655200 and dim <= 914399:
        return "over 1 year ago"
    elif dim >= 914400 and dim <= 1051199:
        return "almost 2 years ago"
    else:
        return "about {0} years ago".format(int(round(dim/525600.0)))

def datetime_seconds(td):
    return float(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def to_json(data):
    if not type(data) == dict:
        # assume it's a named tuple
        data = data._asdict()
    result = {}
    for key,value in data.items():
        if value == None:
            result[key] = None
        elif type(value) in [bool,int,long,float,complex,str]:
            result[key] = value
        elif type(value) == unicode:
            result[key] = value.encode('utf-8')
        elif type(value) == Decimal:
            result[key] = float(value)
        elif type(value) == datetime:
            result[key] = value.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif type(value) == timedelta:
            result[key] = datetime_seconds(value)
        else:
            result[key] = to_json(value.to_dict())
    return result


def is_leap_year(today_dt=None):
    if today_dt is None:
        today_dt = datetime.utcnow()

    if today_dt.year % 400 == 0:
       leap_year = True
    elif today_dt.year % 100 == 0:
       leap_year = False
    elif today_dt.year % 4 == 0:
       leap_year = True
    else:
       leap_year = False

    return leap_year


def is_cake_day(create_dt, today_dt=None):
    cake_day = False

    if today_dt is None:
        today_dt = datetime.utcnow()

    # cakes are given on the first anniversary, not the actual create date!
    if datetime.date(today_dt) != datetime.date(create_dt):
        if today_dt.day == create_dt.day and today_dt.month == create_dt.month:
            cake_day = True

        # leap year people get their cakes on March 1
        if not is_leap_year(today_dt) and create_dt.month == 2 and create_dt.day == 29:
            if today_dt.month == 3 and today_dt.day == 1:
                cake_day = True

    return cake_day


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
    except:
        log.debug('ERROR: Could not verify request: {0}'.format(sys.exc_info()))
        idfp = None
        status = None

    if flg_verify_requests and not idfp:
        log.debug("ERROR: Unverified request")
        raise pyramid.httpexceptions.HTTPUnauthorized("Unverified request")

    return (idfp, status)
