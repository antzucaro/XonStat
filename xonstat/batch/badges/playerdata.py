from xonstat.models import DBSession, Player
from xonstat.views.player import get_games_played, get_overall_stats, get_ranks, get_elos


class PlayerData:

    # player data, will be filled by get_data()
    data = {}

    def __init__(self):
        self.data = {}

    def __getattr__(self, key):
        if self.data.has_key(key):
            return self.data[key]
        return None

    @classmethod
    def get_data(self, player_id):
        """Return player data as dict.

        This function is similar to the function in player.py but more optimized
        for this purpose.
        """
        # total games
        # wins/losses
        # kills/deaths
        
        # duel/dm/tdm/ctf elo + rank
        player = DBSession.query(Player).filter_by(player_id=player_id).\
                filter(Player.active_ind == True).one()
        games_played    = get_games_played(player_id)
        overall_stats   = get_overall_stats(player_id)
        ranks           = get_ranks(player_id)
        elos            = get_elos(player_id)

        games_played_dict = {}
        for game in games_played:
            games_played_dict[game.game_type_cd] = game

        ranks_dict = {}
        for gt,rank in ranks.items():
            ranks_dict[gt] = (rank.rank, rank.max_rank)

        elos_dict = {}
        for gt,elo in elos.items():
            if elo.games > 0:
                elos_dict[gt] = elo.elo

        self.data = {
                'player':player,
                'games_played':games_played_dict,
                'overall_stats':overall_stats,
                'ranks':ranks_dict,
                'elos':elos_dict,
            }
         

