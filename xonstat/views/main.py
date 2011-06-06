import logging
import sqlalchemy.sql.functions as func
from pyramid.response import Response
from xonstat.models import *

log = logging.getLogger(__name__)

def main_index(request):
    top_players = DBSession.query(Player.player_id, Player.nick, func.sum(PlayerGameStat.score)).\
            filter(Player.player_id == PlayerGameStat.player_id).\
            filter(Player.player_id > 2).\
            order_by(func.sum(PlayerGameStat.score)).\
            group_by(Player.nick).\
            group_by(Player.player_id).all()[0:10]

    return {'top_players':top_players}
