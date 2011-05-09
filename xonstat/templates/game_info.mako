<%inherit file="base.mako"/>

<%block name="title">
Game Information - ${parent.title()}
</%block>


% if game is None:
<h2>Sorry, that game wasn't found!</h2>

% else:
<h2>Game Detail</h2>
<p>
Played on: ${start_dt}<br />
Game Type: ${game_type_cd}<br />
Server: <a href="${request.route_url("server_info", id=server_id)}" name="Server info page for ${server_name}">${server_name}</a><br />
Map: <a href="${request.route_url("map_info", id=map_id)}" name="Map info page for ${map_name}">${map_name}</a><br />
</p>

<h2>Scoreboard</h2>
<table border="1">
    <tr>
        <td>Nick</td>
        <td>Kills</td>
        <td>Deaths</td>
        <td>Suicides</td>
        <td>Captures</td>
        <td>Returns</td>
        <td>Flag Carrier Kills</td>
        <td>Score</td>
    </tr>
% for player_game_stat in player_game_stats:
    <tr>
        <td>${player_game_stat.nick_html_colors()}</td>
        <td>${player_game_stat.kills}</td>
        <td>${player_game_stat.deaths}</td>
        <td>${player_game_stat.suicides}</td>
        <td>${player_game_stat.captures}</td>
        <td>${player_game_stat.returns}</td>
        <td>${player_game_stat.carrier_frags}</td>
        <td>${player_game_stat.score}</td>
    </tr>
% endfor
</table>
% endif
