<%def name="scoreboard(game_type_cd, pgstats, teams=None, show_elo=False, show_latency=False)">
##teams: { scoreboardpos : ( teamname, teamscore, playercount ) }
% if teamscores:
<table class="table table-condensed">
<tbody><tr class="teamscores">
% for team,score in sorted(teamscores.items(), key=lambda x:x[1], reverse=True):
    <td class="${team} teamscore" width="${100/len(teamscores)}%">${team.capitalize()} Team: ${score}</td>
% endfor
  </tr></tbody>
</table>
% endif

<table class="table table-hover table-condensed">
  ${scoreboard_header(game_type_cd, pgstats[0])}
  <tbody>
  % for pgstat in pgstats:
  <tr class="${pgstat.team_html_color()}">
    <td class="nostretch">
      % if pgstat.player_id > 2:
      <a href="${request.route_url("player_info", id=pgstat.player_id)}"
        title="Go to the info page for this player">
        <span class="nick">${pgstat.nick_html_colors()|n}</span>
      </a>
      % else:
      <span class="nick">${pgstat.nick_html_colors()|n}</span>
      % endif
    </td>
    % if show_latency and pgstat.avg_latency is not None:
    <td class="scoreboard-entry">
      ${int(round(pgstat.avg_latency))}
    </td>
    % elif show_latency:
    <td class="scoreboard-entry"></td>
    % endif
    ${scoreboard_row(game_type_cd, pgstat)}
    % if game_type_cd != 'cts':
    <td class="scoreboard-entry">${pgstat.score}</td>
    % endif
    % if show_elo:
    % if pgstat.elo_delta is not None:
    <td class="scoreboard-entry">${round(pgstat.elo_delta,2)}</td>
    % else:
    <td class="scoreboard-entry">-</td>
    % endif
    % endif
    ##% if teams:
    ##% if teams.has_key(pgstat.scoreboardpos):
    ##<td class="scoreboard-entry teamscore" rowspan="${teams[pgstat.scoreboardpos].playercount}">${teams[pgstat.scoreboardpos].teamscore}</td>
    ##% endif
    ##% endif
  </tr>
  % endfor
  </tbody>
</table>
</%def>

##### SCOREBOARD HEADER #####
<%def name="scoreboard_header(game_type_cd, pgstat)">
% if game_type_cd == 'as':
<thead>
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="kills">Kills</th>
    <th class="deaths">Deaths</th>
    <th class="suicides">Suicides</th>
    <th class="objectives">Objectives</th>
    <th class="score">Score</th>
    ##% if teams:
    ##<th class="teamscore">Teamscore</th>
    ##% endif
    % if show_elo:
    <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd in 'ca' 'dm' 'duel' 'rune' 'tdm':
<thead>
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="kills">Kills</th>
    <th class="deaths">Deaths</th>
    <th class="suicides">Suicides</th>
    <th class="score">Score</th>
    ##% if teams:
    ##<th class="teamscore">Teamscore</th>
    ##% endif
    % if show_elo:
    <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd == 'cq':
<thead>
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="kills">Kills</th>
    <th class="deaths">Deaths</th>
    <th class="captured">Captured</th>
    <th class="released">Released</th>
    <th class="score">Score</th>
    ##% if show_elo:
    ##<th>Elo Change</th>
    ##% endif
  </tr>
</thead>
% endif

% if game_type_cd == 'cts':
<thead>
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="fastest">Fastest Time</th>
    <th class="deaths">Deaths</th>
  </tr>
</thead>
% endif

% if game_type_cd == 'ctf':
<thead class="ctf ${pgstat.team_html_color()}">
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="kills">Kills</th>
    <th class="captures">Captures</th>
    <th class="pickups">Pickups</th>
    <th class="fck" title="Flag Carrier Kill">FCK</th>
    <th class="returns">Returns</th>
    <th class="score">Score</th>
    ##% if teams:
    ##<th class="teamscore">Teamscore</th>
    ##% endif
    % if show_elo:
    <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd == 'dom':
<thead class="dom ${pgstat.team_html_color()}">
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="kills">Kills</th>
    <th class="deaths">Deaths</th>
    <th class="takes">Takes</th>
    <th class="ticks">Ticks</th>
    <th class="score">Score</th>
    ##% if teams:
    ##<th class="teamscore">Teamscore</th>
    ##% endif
    % if show_elo:
    <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd in 'ft' 'freezetag':
<thead class="freezetag ${pgstat.team_html_color()}">
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="kills">Kills</th>
    <th class="deaths">Deaths</th>
    <th class="revivals">Revivals</th>
    <th class="score">Score</th>
    ##% if teams:
    ##<th class="teamscore">Teamscore</th>
    ##% endif
    % if show_elo:
    <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd in 'ka' 'keepaway':
<thead>
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="kills">Kills</th>
    <th class="deaths">Deaths</th>
    <th class="pickups">Pickups</th>
    <th class="bctime">BC Time</th>
    <th class="bckills">BC Kills</th>
    ##% if teams:
    ##<th class="teamscore">Teamscore</th>
    ##% endif
    % if show_elo:
    <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd == 'kh':
<thead class="kh ${pgstat.team_html_color()}">
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="kills">Kills</th>
    <th class="deaths">Deaths</th>
    <th class="pickups">Pickups</th>
    <th class="caps">Captures</th>
    <th class="losses">Losses</th>
    <th class="pushes">Pushes</th>
    <th class="destroys">Destroys</th>
    <th class="kckills">KC Kills</th>
    <th class="score">Score</th>
    ##% if teams:
    ##<th class="teamscore">Teamscore</th>
    ##% endif
    % if show_elo:
    <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd in 'nb' 'nexball':
<thead class="nb ${pgstat.team_html_color()}">
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="goals">Goals</th>
    <th class="faults">Faults</th>
    <th class="score">Score</th>
    ##% if teams:
    ##<th class="teamscore">Teamscore</th>
    ##% endif
    % if show_elo:
    <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd == 'rc':
<thead>
  <tr>
    <th class="nick">Nick</th>
    % if show_latency:
    <th class="ping">Ping</th>
    % endif
    <th class="laps">Laps</th>
    <th class="fastest">Fastest Lap</th>
    <th class="time">Time</th>
  </tr>
</thead>
% endif

</%def>

##### SCOREBOARD ROWS #####
<%def name="scoreboard_row(game_type_cd, pgstat)">
% if game_type_cd == 'as':
<td class="scoreboard-entry">${pgstat.kills}</td>
<td class="scoreboard-entry">${pgstat.deaths}</td>
<td class="scoreboard-entry">${pgstat.suicides}</td>
<td class="scoreboard-entry">${pgstat.collects}</td>
% endif

% if game_type_cd in 'ca' 'dm' 'duel' 'rune' 'tdm':
<td class="scoreboard-entry">${pgstat.kills}</td>
<td class="scoreboard-entry">${pgstat.deaths}</td>
<td class="scoreboard-entry">${pgstat.suicides}</td>
% endif

% if game_type_cd == 'cq':
<td class="scoreboard-entry">${pgstat.kills}</td>
<td class="scoreboard-entry">${pgstat.deaths}</td>
<td class="scoreboard-entry">${pgstat.captures}</td>
<td class="scoreboard-entry">${pgstat.drops}</td>
% endif

% if game_type_cd == 'cts':
% if pgstat.fastest is not None:
<td class="scoreboard-entry">${round(float(pgstat.fastest.seconds) + (pgstat.fastest.microseconds/1000000.0), 2)}</td>
% else:
<td class="scoreboard-entry">-</td>
% endif
<td class="scoreboard-entry">${pgstat.deaths}</td>
% endif

% if game_type_cd == 'ctf':
<td class="scoreboard-entry">${pgstat.kills}</td>
<td class="scoreboard-entry">${pgstat.captures}</td>
<td class="scoreboard-entry">${pgstat.pickups}</td>
<td class="scoreboard-entry">${pgstat.carrier_frags}</td>
<td class="scoreboard-entry">${pgstat.returns}</td>
% endif

% if game_type_cd == 'dom':
<td class="scoreboard-entry">${pgstat.kills}</td>
<td class="scoreboard-entry">${pgstat.deaths}</td>
<td class="scoreboard-entry">${pgstat.pickups}</td>
<td class="scoreboard-entry">${pgstat.drops}</td>
% endif

% if game_type_cd in 'ft' 'freezetag':
<td class="scoreboard-entry">${pgstat.kills}</td>
<td class="scoreboard-entry">${pgstat.deaths}</td>
<td class="scoreboard-entry">${pgstat.revivals}</td>
% endif

% if game_type_cd in 'ka' 'keepaway':
<td class="scoreboard-entry">${pgstat.kills}</td>
<td class="scoreboard-entry">${pgstat.deaths}</td>
<td class="scoreboard-entry">${pgstat.pickups}</td>

% if pgstat.time is not None:
<td class="scoreboard-entry">${round(float(pgstat.time.seconds) + (pgstat.time.microseconds/1000000.0), 2)}</td>
% else:
<td class="scoreboard-entry">-</td>
% endif

<td class="scoreboard-entry">${pgstat.fckills}</td>
% endif

% if game_type_cd == 'kh':
<td class="scoreboard-entry">${pgstat.kills}</td>
<td class="scoreboard-entry">${pgstat.deaths}</td>
<td class="scoreboard-entry">${pgstat.pickups}</td>
<td class="scoreboard-entry">${pgstat.captures}</td>
<td class="scoreboard-entry">${pgstat.drops}</td>
<td class="scoreboard-entry">${pgstat.pushes}</td>
<td class="scoreboard-entry">${pgstat.destroys}</td>
<td class="scoreboard-entry">${pgstat.carrier_frags}</td>
% endif

% if game_type_cd in 'nb' 'nexball':
<td class="scoreboard-entry">${pgstat.captures}</td>
<td class="scoreboard-entry">${pgstat.drops}</td>
% endif

% if game_type_cd == 'rc':
<td class="scoreboard-entry">${pgstat.laps}</td>

% if pgstat.fastest is not None:
<td class="scoreboard-entry">${round(float(pgstat.fastest.seconds) + (pgstat.fastest.microseconds/1000000.0), 2)}</td>
% else:
<td class="scoreboard-entry">-</td>
% endif

% if pgstat.time is not None:
<td class="scoreboard-entry">${round(float(pgstat.time.seconds) + (pgstat.time.microseconds/1000000.0), 2)}</td>
% else:
<td class="scoreboard-entry">-</td>
% endif
% endif

</%def>
