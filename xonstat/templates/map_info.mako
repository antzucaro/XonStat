<%inherit file="base.mako"/>

<%block name="title">
% if gmap:
Map Information for ${gmap.name} - 
% endif

${parent.title()}
</%block>


% if gmap is None:
<h2>Sorry, that map wasn't found!</h2>

% else:
<h2>Map Detail - ${gmap.name}</h2>

##### RECENT GAMES #####
<h2>Recent Games</h2>
<table id="recent-games">
    <thead>
        <tr>
            <th>Game #</th>
            <th>Type</th>
            <th>Time</th>
            <th>Winner</th>
        </tr>
    </thead>
    <tbody>
    % for (game, srv, map, pgstat) in recent_games:
        % if game != '-':
        <tr>
            <td><a href="${request.route_url('game_info', id=game.game_id)}" title="View detailed information about this game">${game.game_id}</a></td>
            <td class="gt_icon"><img title="${game.game_type_cd}" src="/static/images/icons/24x24/${game.game_type_cd}.png" alt="${game.game_type_cd}" /></td>
            <td>${game.start_dt.strftime('%m/%d/%Y %H:%M')}</td>
            <td class=
            % if pgstat.team == 5:
            "blue"
            % elif pgstat.team == 14:
            "red"
            % elif pgstat.team == 13:
            "yellow"
            % endif
            >
            % if pgstat.player_id > 2:
            <a href="${request.route_url('player_info', id=pgstat.player_id)}" title="Go to the player info page for this player">${pgstat.nick_html_colors()|n}</a></td>
            % else:
            ${pgstat.nick_html_colors()|n}</td>
            % endif
        </tr>
        % else:
        <tr>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
        </tr>
        % endif
    % endfor
    </tbody>
</table>


##### TOP SCORERS #####
<div class="table_block">
<h2>Top Scoring Players</h2>
<table>
    <thead>
        <tr>
            <th>#</th>
            <th>Nick</th>
            <th>Score</th>
        </tr>
    </thead>
    <tbody>
    <% i = 1 %>
    % for (score_player_id, score_nick, score_value) in top_scorers:
        <tr>
            <td>${i}</td>
            % if score_player_id != '-':
            <td><a href="${request.route_url('player_info', id=score_player_id)}" title="Go to the player info page for this player">${score_nick|n}</a></td>
            % else:
            <td>${score_nick}</td>
            % endif
            <td>${score_value}</td>
        </tr>
        <% i = i+1 %>
    % endfor
    </tbody>
</table>
</div>


##### TOP PLAYERS #####
<div class="table_block">
<h2>Most Active Players</h2>
<table id="top-players">
    <thead>
        <tr>
            <th>#</th>
            <th>Nick</th>
            <th>Playing Time</th>
        </tr>
    </thead>
    <tbody>
    <% i = 1 %>
    % for (player_id, nick, alivetime) in top_players:
        <tr>
            <td>${i}</td>
            % if player_id != '-':
            <td><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${nick|n}</a></td>
            % else:
            <td>${nick}</td>
            % endif
            <td>${alivetime}</td>
        </tr>
        <% i = i+1 %>
    % endfor
    </tbody>
</table>
</div>


##### TOP SERVERS #####
<div class="table_block">
<h2>Most Active Servers</h2>
<table id="top-servers">
    <thead>
        <tr>
            <th>#</th>
            <th>Name</th>
            <th>Times Played</th>
        </tr>
    </thead>
    <tbody>
    <% i = 1 %>
    % for (server_id, name, times_played) in top_servers:
        <tr>
            <td>${i}</td>
            <td><a href="${request.route_url('server_info', id=server_id)}" title="Go to the server info page for this server">${name}</a></td>
            <td>${times_played}</td>
        </tr>
        <% i = i+1 %>
    % endfor
    </tbody>
</table>
</div>


% endif
