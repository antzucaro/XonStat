"""
Mixins for methods used by several model classes.
"""
from calendar import timegm
from xonstat.util import pretty_date, html_colors


class FuzzyDateMixin(object):
    """Provides a class with a "create_dt" attribute the ability to return a fuzzy date."""

    def fuzzy_date(self):
        return pretty_date(self.create_dt)


class EpochMixin(object):
    """Provides a class with a "create_dt" attribute the ability to return the epoch time."""

    def epoch(self):
        return timegm(self.create_dt.timetuple())


class NickColorsMixin(object):
    """Provides a class with a "nick" attribute the ability to return the nick's HTML colors."""

    def nick_html_colors(self, limit=None):
        if self.nick is None:
            return "Anonymous Player"
        else:
            return html_colors(self.nick, limit)
