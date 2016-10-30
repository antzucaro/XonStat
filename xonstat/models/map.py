"""
Models related to maps.
"""

from calendar import timegm

from xonstat.util import pretty_date, strip_colors, html_colors


class Map(object):
    """
    A playable map. Roughly equivalent to a pk3 file, but distinguished by name instead.
    """

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return "<Map({}, {}, {})>".format(self.map_id, self.name, self.version)

    def to_dict(self):
        return {
            'map_id': self.map_id,
            'name': self.name,
            'version': self.version,
        }

    def fuzzy_date(self):
        return pretty_date(self.create_dt)

    def epoch(self):
        return timegm(self.create_dt.timetuple())


# TODO: investigate if this model is truly a model, or really just a query (i.e. namedtuple)
class MapCapTime(object):
    """
    Fastest flag capture times per map.
    """

    def __init__(self, row):
        self.fastest_cap = row.fastest_cap
        self.create_dt = row.create_dt
        self.create_dt_epoch = timegm(row.create_dt.timetuple())
        self.create_dt_fuzzy = pretty_date(row.create_dt)
        self.player_id = row.player_id
        self.player_nick = row.player_nick
        self.player_nick_stripped = strip_colors(row.player_nick)
        self.player_nick_html = html_colors(row.player_nick)
        self.game_id = row.game_id
        self.server_id = row.server_id
        self.server_name = row.server_name

    def to_dict(self):
        return {
            "fastest_cap": self.fastest_cap.total_seconds(),
            "create_dt_epoch": self.create_dt_epoch,
            "create_dt_fuzzy": self.create_dt_fuzzy,
            "player_id": self.player_id,
            "player_nick": self.player_nick,
            "player_nick_stripped": self.player_nick_stripped,
            "game_id": self.game_id,
            "server_id": self.server_id,
            "server_name": self.server_name,
        }
