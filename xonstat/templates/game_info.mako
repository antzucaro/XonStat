<%inherit file="base.mako"/>
<%namespace file="scoreboard.mako" import="scoreboard" />

<%block name="title">
Game Information - ${parent.title()}
</%block>


% if game is None:
<h2>Sorry, that game wasn't found!</h2>

% else:
<h2>Game Detail</h2>
<p>
Played on: ${start_dt.strftime('%m/%d/%Y at %I:%M %p')}<br />
Game Type: ${game_type_cd}<br />
Server: <a href="${request.route_url("server_info", id=server_id)}" name="Server info page for ${server_name}">${server_name}</a><br />
Map: <a href="${request.route_url("map_info", id=map_id)}" name="Map info page for ${map_name}">${map_name}</a><br />
</p>

<h2>Scoreboard</h2>
${scoreboard(game_type_cd, player_game_stats)}
% endif
