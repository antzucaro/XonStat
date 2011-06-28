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
<% i = 1 %>
% for (player_id, nick, score) in top_players:
    <tr>
        <td>${i}</td>
        % if player_id != '-':
        <td><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${nick|n}</a></td>
        % else:
        <td>${nick}</td>
        % endif
        <td>${score}</td>
    </tr>
    <% i = i+1 %>
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
<% i = 1 %>
% for (server_id, name, count) in top_servers:
    <tr>
        <td>${i}</td>
        % if server_id != '-':
        <td><a href="${request.route_url('server_info', id=server_id)}" title="Go to the server info page for ${name}">${name}</a></td>
        % else:
        <td>${name}</td>
        % endif
        <td>${count}</td>
    </tr>
    <% i = i+1 %>
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
<% i = 1 %>
% for (map_id, name, count) in top_maps:
    <tr>
        <td>${i}</td>
        % if map_id != '-':
        <td><a href="${request.route_url('map_info', id=map_id)}" title="Go to the map info page for ${name}">${name}</a></td>
        % else:
        <td>${name}</td>
        % endif
        <td>${count}</td>
    </tr>
    <% i = i+1 %>
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
        <th>Type</th>
        <th>Server</th>
        <th>Map</th>
        <th>Time</th>
        <th>Winner</th>
    </tr>
    % for (game, server, map) in recent_games:
    % if game != '-':
    <tr>
        <td><a href="${request.route_url('game_info', id=game.game_id)}" title="View detailed information about this game">${game.game_id}</a></td>
        <td>${game.game_type_cd}</td>
        <td><a href="${request.route_url('server_info', id=server.server_id)}" title="Go to the detail page for this server">${server.name}</a></td>
        <td><a href="${request.route_url('map_info', id=map.map_id)}" title="Go to the map detail page for this map">${map.name}</a></td>
        <td>${game.start_dt.strftime('%m/%d/%Y %H:%M')}</td>
        <td>${game.winner}</td>
    </tr>
    % else:
    <tr>
        <td>-</td>
        <td>-</td>
        <td>-</td>
        <td>-</td>
        <td>-</td>
        <td>-</td>
    </tr>
    % endif
    % endfor
</table>
</div> <!-- END RECENT GAMES -->
