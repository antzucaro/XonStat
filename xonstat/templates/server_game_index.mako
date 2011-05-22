<%inherit file="base.mako"/>

<%block name="title">
Server Game Index for ${server.name} - ${parent.title()}
</%block>

% if not games:
<h2>Sorry, no games yet. Get playing on the server!</h2>

% else:
<h2>Games on ${server.name}</h2>
<ul>
% for (game, theserver, map) in games:
   <li><a href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">#${game.game_id}:</a> <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a></li>
% endfor
</ul>
% endif

% if games.previous_page:
<a href="${request.route_url("server_game_index", server_id=server.server_id, page=games.previous_page)}" name="Previous Page">Previous</a>
% endif
% if games.next_page:
<a href="${request.route_url("server_game_index", server_id=server.server_id, page=games.next_page)}" name="Next Page">Next</a>
% endif
