import re
from datetime import datetime

def strip_colors(str=None):
    str = re.sub(r'\^x\w\w\w', '', str)
    str = re.sub(r'\^\d', '', str)
    return str


def html_colors(str=None):
    orig = str
    str = re.sub(r'\^x(\w)(\w)(\w)', 
            "<span style='color:#\g<1>\g<1>\g<2>\g<2>\g<3>\g<3>'>", str)
    str = re.sub(r'\^1', "<span style='color:#FF9900'>", str)
    str = re.sub(r'\^2', "<span style='color:#33FF00'>", str)
    str = re.sub(r'\^3', "<span style='color:#FFFF00'>", str)
    str = re.sub(r'\^4', "<span style='color:#3366FF'>", str)
    str = re.sub(r'\^5', "<span style='color:#33FFFF'>", str)
    str = re.sub(r'\^6', "<span style='color:#FF3366'>", str)
    str = re.sub(r'\^7', "<span style='color:#FFFFFF'>", str)
    str = re.sub(r'\^8', "<span style='color:#999999'>", str)
    str = re.sub(r'\^9', "<span style='color:#666666'>", str)
    str = re.sub(r'\^0', "<span style='color:#333333'>", str)

    for span in range(len(re.findall(r'\^x\w\w\w|\^\d', orig))):
        str += "</span>"

    return str


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
