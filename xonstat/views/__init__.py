from xonstat.views.submission import submit_stats
from xonstat.views.player import player_index, player_info, player_game_index
from xonstat.views.player import player_accuracy
from xonstat.views.player import player_index_json, player_info_json
from xonstat.views.player import player_game_index_json, player_accuracy_json
from xonstat.views.player import player_damage_json
from xonstat.views.player import player_elo_info_text, player_elo_info_json
from xonstat.views.player import player_hashkey_info_text, player_hashkey_info_json
from xonstat.views.player import player_captimes, player_captimes_json

from xonstat.views.game   import game_info, rank_index
from xonstat.views.game   import game_info_json, rank_index_json
from xonstat.views.game   import game_finder

from xonstat.views.map    import map_info, map_index
from xonstat.views.map    import map_info_json, map_index_json
from xonstat.views.map    import map_captimes, map_captimes_json

from xonstat.views.server import server_info, server_game_index, server_index
from xonstat.views.server import server_info_json, server_game_index_json
from xonstat.views.server import server_index_json

from xonstat.views.search import search_q, search
from xonstat.views.search import search_json

from xonstat.views.exceptions   import notfound

from xonstat.views.main   import main_index
