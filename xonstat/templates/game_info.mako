<%inherit file="base.mako"/>
<%namespace file="scoreboard.mako" import="scoreboard" />
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="title">
Game Information - ${parent.title()}
</%block>


% if game is None:
<h2>Sorry, that game wasn't found!</h2>

% else:
<h2>Game Detail</h2>
<p>
Played on: ${game.start_dt.strftime('%m/%d/%Y at %I:%M %p')}<br />
Game Type: ${game.game_type_cd}<br />
Server: <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a><br />
Map: <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a><br />
</p>

##### SCOREBOARD #####
<h2>Scoreboard</h2>
${scoreboard(game.game_type_cd, pgstats)}
<br />
<br />


##### ACCURACY #####
<h2>Accuracy</h2>
% for pgstat in pgstats:
% if pgstat.player_game_stat_id in pwstats:
<a name="accuracy-${pgstat.player_game_stat_id}" />Accuracy for ${pgstat.nick_html_colors()}:
${accuracy(pwstats[pgstat.player_game_stat_id][0:5])}
<br />
<br />
% endif
% endfor

% endif
