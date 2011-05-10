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
<h2>Player Detail</h2>
<p>
   Nickname: ${player.nick} <br />
   Joined: ${player.create_dt.strftime('%m/%d/%Y at %I:%M %p')} <br />
</p>
% endif

% if recent_games:
<h2>Recent Games</h2>
<ul>
% for (game_id, server_id, server_name, map_id, map_name) in recent_games:
   <li><a href="${request.route_url("map_info", id=map_id)}" name="Map info page for ${map_name}">${map_name}</a> on <a href="${request.route_url("server_info", id=server_id)}" name="Server info page for ${server_name}">${server_name}</a> (game <a href="${request.route_url("game_info", id=game_id)}" name="Game info page for game #${game_id}">#${game_id}</a>)</li>
% endfor
</ul>
% endif
