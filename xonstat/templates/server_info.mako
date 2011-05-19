<%inherit file="base.mako"/>

<%block name="title">
% if server:
Server Information for ${server.name} - 
% endif

${parent.title()}
</%block>


% if server is None:
<h2>Sorry, that server wasn't found!</h2>

% else:
<h2>${server.name}</h2>
<ul>
   <li>IP Address: ${server.ip_addr}</li>
   <li>Revision: ${server.revision}</li>
   <li>Created: ${server.create_dt.strftime('%m/%d/%Y at %I:%M %p')}</li>
</ul>
% if recent_games:
<h2>Recent Games</h2>
<ul>
% for (game, theserver, map) in recent_games:
   <li><a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a> (game <a href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">#${game.game_id}</a>)</li>
% endfor
</ul>
More games played on ${server.name}...
% endif
% endif
