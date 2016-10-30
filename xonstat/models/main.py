"""
Models related to the main index page.
"""

from xonstat.util import html_colors


class SummaryStat(object):
    """
    The high level summary line that is shown on the main page.
    """

    def __repr__(self):
        return ("<SummaryStat(total_players={}, total_games={}, total_servers={})>"
                .format(self.total_players, self.total_games, self.total_servers))


class ActivePlayer(object):
    """
    A record in the "Most Active Players" list.
    """

    def __init__(self, sort_order=None, player_id=None, nick=None, alivetime=None):
        self.sort_order = sort_order
        self.player_id = player_id
        self.nick = nick
        self.alivetime = alivetime

    def nick_html_colors(self):
        return html_colors(self.nick)

    def __repr__(self):
        return "<ActivePlayer({}, {})>".format(self.sort_order, self.player_id)


class ActiveServer(object):
    """
    A record in the "Most Active Servers" list.
    """

    def __init__(self, sort_order=None, server_id=None, server_name=None, games=None):
        self.sort_order = sort_order
        self.server_id = server_id
        self.server_name = server_name
        self.games = games

    def __repr__(self):
        return "<ActiveServer({}, {})>".format(self.sort_order, self.server_id)


class ActiveMap(object):
    """
    A record in the "Most Active Maps" list.
    """

    def __init__(self, sort_order=None, map_id=None, map_name=None, games=None):
        self.sort_order = sort_order
        self.map_id = map_id
        self.map_name = map_name
        self.games = games

    def __repr__(self):
        return "<ActiveMap({}, {})>".format(self.sort_order, self.map_id)
