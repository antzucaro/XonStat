from xonstat.util import html_colors


class SummaryStat(object):
    def __repr__(self):
        return "<SummaryStat(total_players=%s, total_games=%s, total_servers=%s)>" % (self.total_players, self.total_games, self.total_servers)


class ActivePlayer(object):
    def __init__(self, sort_order=None, player_id=None, nick=None,
            alivetime=None):
        self.sort_order = sort_order
        self.player_id = player_id
        self.nick = nick
        self.alivetime = alivetime

    def nick_html_colors(self):
        return html_colors(self.nick)

    def __repr__(self):
        return "<ActivePlayer(%s, %s)>" % (self.sort_order, self.player_id)


class ActiveServer(object):
    def __init__(self, sort_order=None, server_id=None, server_name=None,
            games=None):
        self.sort_order = sort_order
        self.server_id = server_id
        self.server_name = server_name
        self.games = games

    def __repr__(self):
        return "<ActiveServer(%s, %s)>" % (self.sort_order, self.server_id)


class ActiveMap(object):
    def __init__(self, sort_order=None, map_id=None, map_name=None,
            games=None):
        self.sort_order = sort_order
        self.map_id = map_id
        self.map_name = map_name
        self.games = games

    def __repr__(self):
        return "<ActiveMap(%s, %s)>" % (self.sort_order, self.map_id)