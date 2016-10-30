"""
Models related to servers.
"""

from calendar import timegm
from datetime import datetime as dt

from xonstat.util import pretty_date


class Server(object):
    """
    A Xonotic server, identifiable by name and (when there's a conflict) hashkey.
    """

    def __init__(self, name=None, hashkey=None, ip_addr=None):
        self.name = name
        self.hashkey = hashkey
        self.ip_addr = ip_addr
        self.create_dt = dt.utcnow()

    def __repr__(self):
        return "<Server({}, {})>".format(self.server_id, self.name.encode('utf-8'))

    def to_dict(self):
        return {
            'server_id': self.server_id,
            'name': self.name,
            'ip_addr': self.ip_addr,
            'location': self.location,
        }

    def fuzzy_date(self):
        return pretty_date(self.create_dt)

    def epoch(self):
        return timegm(self.create_dt.timetuple())