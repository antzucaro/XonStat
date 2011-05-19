<%inherit file="base.mako"/>

<%block name="title">
% if player:
Player Information for ${player.nick} - 
% endif

${parent.title()}
</%block>


% if player is None:
<h2>Sorry, that player wasn't found!</h2>

% else:
<h2>${player.nick}</h2>
<p>
   Joined: ${player.create_dt.strftime('%m/%d/%Y at %I:%M %p')} <br />
</p>
% endif

% if recent_games:
<h2>Recent Games</h2>
<ul>
% for (gamestat, game, server, map) in recent_games:
   <li>game <a href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">#${game.game_id}:</a> <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a> on <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a></li>
% endfor
</ul>
More games played by ${player.nick}...
% endif
