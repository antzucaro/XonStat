<%inherit file="base.mako"/>
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="title">
% if player:
Player Information for ${player.nick_html_colors()} - 
% endif

${parent.title()}
</%block>


% if player is None:
<h2>This player is so good we couldn't find him!</h2>
<p>Seriously though, he probably doesn't exist...just a figment of your imagination. Carry on then!</p>

% else:
<h2>${player.nick_html_colors()}</h2>
<p>
   Joined: ${player.create_dt.strftime('%m/%d/%Y at %I:%M %p')} <br />
</p>
% endif


##### ACCURACY #####
% if weapon_stats:
<h2>Accuracy</h2>
${accuracy(weapon_stats)}
% endif


##### RECENT GAMES #####
% if recent_games:
<h2>Recent Games</h2>
% for (gamestat, game, server, map) in recent_games:
   <a href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">#${game.game_id}:</a> <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a> on <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a>
<br />
% endfor
<a href="${request.route_url("player_game_index", player_id=player.player_id, page=1)}" title="Game index for ${player.nick}">More games</a> played by ${player.nick_html_colors()}...
% endif


