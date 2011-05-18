<%inherit file="base.mako"/>

<%block name="title">
Game Index - ${parent.title()}
</%block>

% if not games:
<h2>Sorry, no games yet. Get playing!</h2>

% else:
<h2>Recent Games</h2>
<ul>
% for (game, server, map) in games:
   <li>game <a href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">#${game.game_id}:</a> <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a> on <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a></li>
% endfor
</ul>
% endif

% if games.last_page:
<a href="${request.route_url("game_index_paged", page=games.previous_page)}" name="Previous Page">Previous</a>
% endif
% if games.next_page:
<a href="${request.route_url("game_index_paged", page=games.next_page)}" name="Next Page">Next</a>
% endif
