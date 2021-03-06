from xonstat.views.submission import submit_stats
from xonstat.views.player import player_index, player_info, player_game_index
from xonstat.views.player import player_accuracy
from xonstat.views.player import player_index_json, player_info_json
from xonstat.views.player import player_game_index_json, player_accuracy_json
from xonstat.views.player import player_damage_json
from xonstat.views.player import player_elo_info_text, player_elo_info_json
from xonstat.views.player import player_hashkey_info_text, player_hashkey_info_json
from xonstat.views.player import player_captimes, player_captimes_json
from xonstat.views.player import player_weaponstats_data_json, player_versus

from xonstat.views.game   import game_info, rank_index
from xonstat.views.game   import game_info_json, rank_index_json
from xonstat.views.game   import game_finder, game_finder_json

from xonstat.views.map import MapIndex, MapTopScorers, MapTopPlayers, MapTopServers
from xonstat.views.map import map_info, map_info_json
from xonstat.views.map import map_captimes, map_captimes_json

from xonstat.views.server import ServerIndex, ServerTopMaps, ServerTopScorers, ServerTopPlayers
from xonstat.views.server import ServerInfo

from xonstat.views.search import search_q, search
from xonstat.views.search import search_json

from xonstat.views.exceptions   import notfound

from xonstat.views.main   import main_index, top_players_index, top_servers_index
from xonstat.views.main   import top_maps_index, summary_stats_json

from xonstat.views.admin   import forbidden, login, merge

from xonstat.views.static   import robots
