V 1
R XonStat/1.0
T ${now}
S ${request.route_url('player_info', id=player.player_id)}
P ${hashkey}
n ${player.nick}
i ${player.player_id}
% if player.active_ind == True:
e active-ind 1
% else:
e active-ind 0
% endif
e location
% for game_type_cd in elos.keys():
% if game_type_cd != 'overall':
G ${game_type_cd}
e elo ${elos[game_type_cd].elo}
% endif
% endfor
