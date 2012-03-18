import re
from colorsys import rgb_to_hls, hls_to_rgb
from cgi import escape as html_escape
from datetime import datetime

# Map of special chars to ascii from Darkplace's console.c.
_qfont_table = [
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

# Hex-colored spans for decimal color codes ^0 - ^9
_dec_spans = [
 "<span style='color:#333333'>",
 "<span style='color:#FF0000'>",
 "<span style='color:#33FF00'>",
 "<span style='color:#FFFF00'>",
 "<span style='color:#3366FF'>",
 "<span style='color:#33FFFF'>",
 "<span style='color:#FF3366'>",
 "<span style='color:#FFFFFF'>",
 "<span style='color:#999999'>",
 "<span style='color:#666666'>"
]

# Color code patterns
_all_colors = re.compile(r'\^(\d|x[\dA-Fa-f]{3})')
_dec_colors = re.compile(r'\^(\d)')
_hex_colors = re.compile(r'\^x([\dA-Fa-f])([\dA-Fa-f])([\dA-Fa-f])')

# On a light scale of 0 (black) to 255 (white)
_contrast_threshold = 128


def qfont_decode(qstr=''):
    """ Convert the qfont characters in a string to ascii.
    """
    if qstr == None:
        qstr = ''
    chars = []
    for c in qstr:
        if u'\ue000' <= c <= u'\ue0ff':
            c = _qfont_table[ord(c) - 0xe000]
        chars.append(c)
    return ''.join(chars)


def strip_colors(qstr=''):
    if qstr == None:
        qstr = ''
    return _all_colors.sub('', qstr)
    
    
def hex_repl(match):
    r = match.group(1) * 2
    g = match.group(2) * 2
    b = match.group(3) * 2
    hue, light, satur = rgb_to_hls(int(r, 16), int(g, 16), int(b, 16))
    if light < _contrast_threshold:
        light = _contrast_threshold
    r, g, b = hls_to_rgb(hue, light, satur)
    return '<span style="color:rgb({0},{1},{2})">'.format(r, g, b)


def html_colors(qstr=''):
    qstr = html_escape(qfont_decode(qstr).replace('^^', '^'))
    html = _dec_colors.sub(lambda match: _dec_spans[int(match.group(1))], qstr)
    html = _hex_colors.sub(hex_repl, html)
    return html + "</span>" * len(_all_colors.findall(qstr))


def page_url(page):
    return current_route_url(request, page=page, _query=request.GET)


def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        if day_diff/7 == 1:
            return "a week ago"
        else:
            return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        if day_diff/30 == 1:
            return "a month ago"
        else:
            return str(day_diff/30) + " months ago"
    else:
        if day_diff/365 == 1:
            return "a year ago"
        else:
            return str(day_diff/365) + " years ago"
