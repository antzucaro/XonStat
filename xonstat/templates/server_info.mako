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
IP Address: ${server.ip_addr} <br />
Revision: ${server.revision} <br />
Created: ${server.create_dt.strftime('%m/%d/%Y at %I:%M %p')} <br />

% if recent_games:
<h2>Recent Games</h2>
% for (game, theserver, map) in recent_games:
   <a href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">#${game.game_id}</a>: <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a>
<br />
% endfor
<a href="${request.route_url("server_game_index", server_id=server.server_id, page=1)}" name="Game index page for server #${server.name}">More games played on ${server.name}...</a>
% endif
% endif
