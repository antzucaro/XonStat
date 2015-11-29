V 1
R XonStat/1.0
T ${now}
S ${server.server_id}
G ${game.game_id}
M ${gmap.map_id}
% for player_id in player_ids:
P ${hashkeys[player_id]}
i ${player_id}
% if player_id in elos:
e elo ${elos[player_id].elo.elo}
e elo_delta ${elos[player_id].elo_delta}
e elo_games ${elos[player_id].elo.games}
% endif
% if player_id in ranks:
e rank ${ranks[player_id].rank}
% endif
% endfor
