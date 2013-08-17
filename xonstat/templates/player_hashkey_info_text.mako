V 1
R XonStat/1.0
T ${now}
S ${request.route_url('player_info', id=player.player_id)}
P ${hashkey}
n ${player.nick}
i ${player.player_id}
e joined ${player_joined}
% if player.active_ind == True:
e active-ind 1
% else:
e active-ind 0
% endif
e location
e matches ${games_played[0].games}
e total-deaths ${overall_stats['overall'].total_deaths}
e total-fckills ${overall_stats['overall'].total_carrier_frags}
e alivetime ${overall_stats['overall'].total_playing_time_secs}
e total-kills ${overall_stats['overall'].total_kills}
e wins ${games_played[0].wins}
e favorite-map ${fav_maps['overall'].map_name} ${fav_maps['overall'].times_played} ${fav_maps['overall'].game_type_cd}
% for game_type_cd in overall_stats.keys():
% if game_type_cd != 'overall':
G ${game_type_cd}
% if game_type_cd in elos.keys():
e elo ${elos[game_type_cd].elo}
% endif
% if game_type_cd in ranks.keys():
e percentile ${ranks[game_type_cd].percentile}
% endif
% for gp in games_played:
% if gp.game_type_cd == game_type_cd:
e matches ${gp.games}
% endif
% endfor
% if game_type_cd in ranks.keys():
e rank ${ranks[game_type_cd].rank}
% endif
e total-deaths ${overall_stats[game_type_cd].total_deaths}
e alivetime ${overall_stats[game_type_cd].total_playing_time_secs}
e total-kills ${overall_stats[game_type_cd].total_kills}
% for gp in games_played:
% if gp.game_type_cd == game_type_cd:
e wins ${gp.wins}
% endif
% endfor
e favorite-map ${fav_maps[game_type_cd].map_name} ${fav_maps[game_type_cd].times_played}
% endif
% endfor
