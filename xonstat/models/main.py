"""
Models related to the main index page.
"""

from xonstat.util import html_colors


class SummaryStat(object):
    """
    The high level summary line that is shown on the main page.
    """

    def __repr__(self):
        return ("<SummaryStat(total_players={0.total_players}, total_games={0.total_games}, "
                "total_servers={0.total_servers})>".format(self))


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
        return "<ActivePlayer({0.sort_order}, {0.player_id})>".format(self)


class ActiveServer(object):
    """
    A record in the "Most Active Servers" list.
    """

    def __init__(self, sort_order=None, server_id=None, server_name=None, play_time=None):
        self.sort_order = sort_order
        self.server_id = server_id
        self.server_name = server_name
        self.play_time = play_time

    def __repr__(self):
        return "<ActiveServer({0.sort_order}, {0.server_id})>".format(self)


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
        return "<ActiveMap({0.sort_order}, {0.map_id})>".format(self)
