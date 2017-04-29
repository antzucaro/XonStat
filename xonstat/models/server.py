"""
Models related to servers.
"""

from datetime import datetime as dt

from xonstat.models.mixins import FuzzyDateMixin, EpochMixin


class Server(FuzzyDateMixin, EpochMixin):
    """
    A Xonotic server, identifiable by name and (when there's a conflict) hashkey.
    """

    def __init__(self, name=None, hashkey=None, ip_addr=None, elo_ind=None, categories=None):
        self.name = name
        self.hashkey = hashkey
        self.ip_addr = ip_addr
        self.elo_ind = elo_ind if elo_ind is not None else True
        self.create_dt = dt.utcnow()
        self.categories = categories

    def __repr__(self):
        return "<Server({}, {})>".format(self.server_id, self.name.encode('utf-8'))

    def to_dict(self):
        return {
            'server_id': self.server_id,
            'name': self.name,
            'ip_addr': self.ip_addr,
            'location': self.location,
            'categories': self.categories,
        }
