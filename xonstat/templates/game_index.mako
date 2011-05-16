<%inherit file="base.mako"/>

<%block name="title">
Game Index - ${parent.title()}
</%block>

% if not games:
<h2>Sorry, no games yet. Get playing!</h2>

% else:
<h2>Recent Games</h2>
<ul>
% for (game_id, server_id, server_name, map_id, map_name) in games:
   <li>game <a href="${request.route_url("game_info", id=game_id)}" name="Game info page for game #${game_id}">#${game_id}:</a> <a href="${request.route_url("map_info", id=map_id)}" name="Map info page for ${map_name}">${map_name}</a> on <a href="${request.route_url("server_info", id=server_id)}" name="Server info page for ${server_name}">${server_name}</a></li>
% endfor
</ul>
% endif
