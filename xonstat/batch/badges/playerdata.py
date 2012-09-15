import sqlalchemy as sa
import sqlalchemy.sql.functions as func
from xonstat.models import *


class PlayerData:

    # player data, will be filled by get_data()
    data = {}

    def __init__(self):
        self.data = {}

    def __getattr__(self, key):
        if self.data.has_key(key):
            return self.data[key]
        return None

    def get_data(self, player_id):
        """Return player data as dict.

        This function is similar to the function in player.py but more optimized
        for this purpose.
        """
        # total games
        # wins/losses
        # kills/deaths
        # duel/dm/tdm/ctf elo + rank

        player = DBSession.query(Player).filter(Player.player_id == player_id).one()

        games_played = DBSession.query(
                Game.game_type_cd, func.count(), func.sum(PlayerGameStat.alivetime)).\
                filter(Game.game_id == PlayerGameStat.game_id).\
                filter(PlayerGameStat.player_id == player_id).\
                group_by(Game.game_type_cd).\
                order_by(func.count().desc()).\
                all()

        total_stats = {}
        total_stats['games'] = 0
        total_stats['games_breakdown'] = {}  # this is a dictionary inside a dictionary .. dictception?
        total_stats['games_alivetime'] = {}
        total_stats['gametypes'] = []
        for (game_type_cd, games, alivetime) in games_played:
            total_stats['games'] += games
            total_stats['gametypes'].append(game_type_cd)
            total_stats['games_breakdown'][game_type_cd] = games
            total_stats['games_alivetime'][game_type_cd] = alivetime

        (total_stats['kills'], total_stats['deaths'], total_stats['alivetime'],) = DBSession.query(
                func.sum(PlayerGameStat.kills),
                func.sum(PlayerGameStat.deaths),
                func.sum(PlayerGameStat.alivetime)).\
                filter(PlayerGameStat.player_id == player_id).\
                one()

        (total_stats['wins'], total_stats['losses']) = DBSession.\
                query("wins", "losses").\
                from_statement(
                    "SELECT SUM(win) wins, SUM(loss) losses "
                    "FROM   (SELECT  g.game_id, "
                    "                CASE "
                    "                  WHEN g.winner = pgs.team THEN 1 "
                    "                  WHEN pgs.rank = 1 THEN 1 "
                    "                  ELSE 0 "
                    "                END win, "
                    "                CASE "
                    "                  WHEN g.winner = pgs.team THEN 0 "
                    "                  WHEN pgs.rank = 1 THEN 0 "
                    "                  ELSE 1 "
                    "                END loss "
                    "        FROM    games g, "
                    "                player_game_stats pgs "
                    "        WHERE   g.game_id = pgs.game_id "
                    "                AND pgs.player_id = :player_id) win_loss").\
                params(player_id=player_id).one()

        ranks = DBSession.query("game_type_cd", "rank", "max_rank").\
                from_statement(
                    "SELECT  pr.game_type_cd, pr.rank, overall.max_rank "
                    "FROM    player_ranks pr, "
                    "        (SELECT  game_type_cd, max(rank) max_rank "
                    "        FROM     player_ranks "
                    "        GROUP BY game_type_cd) overall "
                    "WHERE   pr.game_type_cd = overall.game_type_cd  "
                    "        AND player_id = :player_id "
                    "ORDER BY rank").\
                params(player_id=player_id).all()

        ranks_dict = {}
        for gtc,rank,max_rank in ranks:
            ranks_dict[gtc] = (rank, max_rank)

        elos = DBSession.query(PlayerElo).\
                filter_by(player_id=player_id).\
                order_by(PlayerElo.elo.desc()).\
                all()

        elos_dict = {}
        for elo in elos:
            if elo.games >= 32:
                elos_dict[elo.game_type_cd] = elo.elo

        self.data = {
                'player':player,
                'total_stats':total_stats,
                'ranks':ranks_dict,
                'elos':elos_dict,
            }

