<%inherit file="base.mako"/>

<%block name="title">
Player Game Index for ${player.nick} - ${parent.title()}
</%block>

% if not games:
<h2>Sorry, no games yet. Get playing, scrub!</h2>

% else:
<h2>Recent Games by ${player.nick}</h2>
<ul>
% for (playergamestat, game, server, map) in games:
   <li>game <a href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">#${game.game_id}:</a> <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a></li>
% endfor
</ul>
% endif

% if games.previous_page:
<a href="${request.route_url("player_game_index", player_id=player.player_id, page=games.previous_page)}" name="Previous Page">Previous</a>
% endif
% if games.next_page:
<a href="${request.route_url("player_game_index", player_id=player.player_id, page=games.next_page)}" name="Next Page">Next</a>
% endif
