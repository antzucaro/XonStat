<%def name="scoreboard(game_type_cd, pgstats)">
<table class="scoreboard" border="1" cellpadding="3">

${scoreboard_header(game_type_cd)}

% for pgstat in pgstats:
    <tr style="background-color:${pgstat.team_html_color()}">
        <td>
        % if pgstat.player_id > 2:
          <a href="${request.route_url("player_info", id=pgstat.player_id)}"
           title="Go to the info page for this player">
          <span class="nick">${pgstat.nick_html_colors()|n}</span>
          </a>
        % else:
          <span class="nick">${pgstat.nick_html_colors()|n}</span>
        % endif
        </td>
	${scoreboard_row(game_type_cd, pgstat)}
        <td><span style="color:#FFFF00;">${pgstat.score}</span></td>
        <td>
        % if pgstat.player_id > 1:
          <a href="${request.route_url("game_info", id=pgstat.game_id)}#accuracy-${pgstat.player_game_stat_id}"
           title="View weapon accuracy details for this player in this game">
          View
          </a>
        % endif
        </td>
    </tr>
% endfor
</table>
</%def>

##### SCOREBOARD HEADER #####
<%def name="scoreboard_header(game_type_cd)">
% if game_type_cd == 'dm' or game_type_cd == 'tdm':
    <tr class="table-header" style="color:black;}">
        <th>Nick</th>
        <th>Kills</th>
        <th>Deaths</th>
        <th>Suicides</th>
        <th>Score</th>
        <th>Accuracy</th>
    </tr>
% endif

% if game_type_cd == 'ctf':
    <tr class="table-header" style="color:${pgstats[0].team_html_color()}">
        <th>Nick</th>
        <th>Kills</th>
        <th>Captures</th>
        <th>Pickups</th>
        <th>Flag Carrier Kills</th>
        <th>Returns</th>
        <th>Score</th>
        <th>Accuracy</th>
    </tr>
% endif

% if game_type_cd == 'ca':
    <tr class="table-header" style="color:${pgstats[0].team_html_color()}">
        <th>Nick</th>
        <th>Kills</th>
        <th>Score</th>
        <th>Accuracy</th>
    </tr>
% endif

% if game_type_cd == 'freezetag':
    <tr style="color:${pgstats[0].team_html_color()}">
        <th>Nick</th>
        <th>Kills</th>
        <th>Deaths</th>
        <th>Suicides</th>
        <th>Score</th>
        <th>Accuracy</th>
    </tr>
% endif
</%def>

##### SCOREBOARD ROWS #####
<%def name="scoreboard_row(game_type_cd, pgstat)">
% if game_type_cd == 'dm' or game_type_cd == 'tdm':
        <td>${pgstat.kills}</td>
        <td>${pgstat.deaths}</td>
        <td>${pgstat.suicides}</td>
% endif

% if game_type_cd == 'ctf':
        <td>${pgstat.kills}</td>
        <td>${pgstat.captures}</td>
        <td>${pgstat.pickups}</td>
        <td>${pgstat.carrier_frags}</td>
        <td>${pgstat.returns}</td>
% endif

% if game_type_cd == 'ca':
        <td>${pgstat.kills}</td>
% endif

% if game_type_cd == 'freezetag':
        <td>${pgstat.kills}</td>
        <td>${pgstat.deaths}</td>
        <td>${pgstat.suicides}</td>
% endif
</%def>
