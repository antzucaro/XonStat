<%inherit file="base.mako"/>

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
<table border="1" cellpadding="3">
% if game_type_cd == 'ctf':
    <tr>
        <td>Nick</td>
        <td>Kills</td>
        <td>Captures</td>
        <td>Pickups</td>
        <td>Flag Carrier Kills</td>
        <td>Returns</td>
        <td>Score</td>
        <td>Accuracy</td>
    </tr>

% for player_game_stat in player_game_stats:
    <tr>
        <td>
        % if player_game_stat.player_id > 2:
          <a href="${request.route_url("player_info", id=player_game_stat.player_id)}"
           title="Go to the info page for this player">
          ${player_game_stat.nick_html_colors()}
          </a>
        % else:
          ${player_game_stat.nick_html_colors()}
        % endif
        </td>
        <td>${player_game_stat.kills}</td>
        <td>${player_game_stat.captures}</td>
        <td>${player_game_stat.pickups}</td>
        <td>${player_game_stat.carrier_frags}</td>
        <td>${player_game_stat.returns}</td>
        <td>${player_game_stat.score}</td>
        <td>
        % if player_game_stat.player_id > 1:
          <a href="${request.route_url("player_weapon_stats", game_id=player_game_stat.game_id, pgstat_id=player_game_stat.player_game_stat_id)}"
           title="View weapon accuracy details for this player in this game">
          View
          </a>
        % endif
        </td>
    </tr>
% endfor
% endif

% if game_type_cd == 'dm':
    <tr>
        <td>Nick</td>
        <td>Kills</td>
        <td>Deaths</td>
        <td>Suicides</td>
        <td>Score</td>
    </tr>

% for player_game_stat in player_game_stats:
    <tr>
        <td>${player_game_stat.nick_html_colors()}</td>
        <td>${player_game_stat.kills}</td>
        <td>${player_game_stat.deaths}</td>
        <td>${player_game_stat.suicides}</td>
        <td>${player_game_stat.score}</td>
    </tr>
% endfor
% endif
</table>
% endif
