<%inherit file="base.mako"/>

<%block name="title">
Main Page - ${parent.title()}
</%block>

<div id="leaderboard">

##### TOP PLAYERS #####
<table id="top-players" border="1">
    <tr>
        <th colspan="3">Top Players</th>
    </tr>
    <tr>
        <th>#</th>
        <th>Nick</th>
        <th>Score</th>
    </tr>
% for (player_id, nick, score) in top_players:
    <tr>
        % if player_id != '-':
        <td><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${player_id}</a></td>
        % else:
        <td>${player_id}</td>
        % endif
        <td>${nick}</td>
        <td>${score}</td>
    </tr>
% endfor
</table>

##### TOP SERVERS #####
<table id="top-servers" border="1">
    <tr>
        <th colspan="3">Top Servers</th>
    </tr>
    <tr>
        <th>#</th>
        <th>Server</th>
        <th>Games</th>
    </tr>
% for (server_id, name, count) in top_servers:
    <tr>
        % if server_id != '-':
        <td><a href="${request.route_url('server_info', id=server_id)}" title="Go to the server info page for this server">${server_id}</a></td>
        % else:
        <td>${server_id}</td>
        % endif
        <td>${name}</td>
        <td>${count}</td>
    </tr>
% endfor
</table>

##### TOP MAPS #####
<table id="top-maps" border="1">
    <tr>
        <th colspan="3">Top Maps</th>
    </tr>
    <tr>
        <th>#</th>
        <th>Map</th>
        <th>Times Played</th>
    </tr>
% for (map_id, name, count) in top_maps:
    <tr>
        % if map_id != '-':
        <td><a href="${request.route_url('map_info', id=map_id)}" title="Go to the map info page for this map">${map_id}</a></td>
        % else:
        <td>${map_id}</td>
        % endif
        <td>${name}</td>
        <td>${count}</td>
    </tr>
% endfor
</table>
</div> <!-- END LEADERBOARD -->

<div id="recent-games">

##### RECENT GAMES #####
<table id="recent-games-table" border="1">
    <tr>
        <th colspan="5">Recent Games</th>
    </tr>
    <tr>
        <th>Game #</th>
        <th>Server</th>
        <th>Map</th>
        <th>Time</th>
        <th>Winner</th>
    </tr>
    % for (game, server, map) in recent_games:
    % if game != '-':
    <tr>
        <td>${game.game_id}</td>
        <td>${server.name}</td>
        <td>${map.name}</td>
        <td>${game.start_dt}</td>
        <td>${game.winner}</td>
    </tr>
    % else:
    <tr>
        <td>-</td>
        <td>-</td>
        <td>-</td>
        <td>-</td>
        <td>-</td>
    </tr>
    % endif
    % endfor
</div> <!-- END RECENT GAMES -->
