V 1
R XonStat/1.0
T ${now}
S ${request.route_url('server_info', id=server.server_id)}
G ${request.route_url('game_info', id=game.game_id)}
M ${request.route_url('map_info', id=gmap.map_id)}
% for player_id in player_ids:
P ${hashkeys[player_id]}
i ${request.route_url('player_info', id=player_id)}
% if player_id in elos:
e elo ${elos[player_id].elo.elo}
e elo_delta ${elos[player_id].elo_delta}
e elo_games ${elos[player_id].elo.games}
e k-factor ${elos[player_id].k}
e score-per-second ${elos[player_id].score_per_second}
e alivetime ${elos[player_id].alivetime}
% endif
% endfor
