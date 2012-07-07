from mako.template import Template
from os import system
from pyramid.paster import bootstrap
from xonstat.models import *
from xonstat.views.player import player_info_data

# converter params
CONVERTER = "/home/ant/xonotic/xonstat/xonstat/batch/badges/wkhtmltoimage-amd64 --crop-x 10 --crop-y 10 --width 560 --height 70 -f png"

# environment setup
env = bootstrap('../../../development.ini.home')
req = env['request']
req.matchdict = {'id':3}

# template setup
t = Template(filename = 'templates/badge.mako')

players = DBSession.query(Player).\
        filter(Player.player_id == PlayerElo.player_id).\
        filter(Player.nick != None).\
        filter(Player.player_id > 2).\
        filter(Player.active_ind == True).all()

for player in players:
    req.matchdict['id'] = player.player_id
    data = player_info_data(req)
    rt = t.render(player=data['player'], elos_display=data['elos_display'],
            total_stats=data['total_stats'], total_games=data['total_games'],
            games_breakdown=data['games_breakdown'])
    f = open("output/%s.html" % player.player_id, 'w')
    f.write(rt)
    f.close()

    cmd = "%s %s %s" % (CONVERTER, "output/%s.html" % player.player_id,
            "output/%s.png" % player.player_id)
    system(cmd)
