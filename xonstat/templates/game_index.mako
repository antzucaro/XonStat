<%inherit file="base.mako"/>
<%namespace file="scoreboard.mako" import="scoreboard" />

<%block name="title">
Game Index - ${parent.title()}
</%block>

<%block name="js">
${parent.js()}
<script type="text/javascript" src="${request.static_url('xonstat:static/js/jquery.js')}"></script>
<script type="text/javascript" src="${request.static_url('xonstat:static/js/jquery.dataTables.min.js')}"></script>
<script>
$(document).ready(function() { $('.scoreboard').dataTable(); } );
</script>
</%block>

% if not games:
<h2>Sorry, no games yet. Get playing!</h2>

% else:
<h2>Recent Games</h2>
% for (game, server, map) in games:
<p>
   <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a> on <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a> (<a href="${request.route_url('game_info', id=game.game_id)}" name="Permalink for game #${game.game_id}">permalink</a> for this game)

## show scoreboard using a def from another file
${scoreboard(game.game_type_cd, pgstats[game.game_id])}

% endfor
% endif

% if games.previous_page:
<a href="${request.route_url("game_index_paged", page=games.previous_page)}" name="Previous Page">Previous</a>
% endif
% if games.next_page:
<a href="${request.route_url("game_index_paged", page=games.next_page)}" name="Next Page">Next</a>
% endif
