<%def name="scoreboard(game_type_cd, pgstats, show_elo=False, show_latency=False)">
<table  class="table-hover table-condensed">
  ${scoreboard_header(game_type_cd, pgstats[0])}
  <tbody>
  % for pgstat in pgstats:
    <tr class="${pgstat.team_html_color()}">
      % if show_latency and pgstat.avg_latency is not None:
        <td class="show-for-medium-up text-center">
          ${int(round(pgstat.avg_latency))}
        </td>
      % elif show_latency:
        <td class="show-for-medium-up text-center">-</td>
      % endif

      <td class="small-5 medium-3 no-stretch">
        % if pgstat.player_id > 2:
          <a href="${request.route_url("player_info", id=pgstat.player_id)}" title="Go to the info page for this player">
            ${pgstat.nick_html_colors()|n}
          </a>
        % else:
          ${pgstat.nick_html_colors()|n}
        % endif
      </td>

      ${scoreboard_row(game_type_cd, pgstat)}

      % if game_type_cd != 'cts':
        <td class="small-3 player-score">${pgstat.score}</td>
      % endif

      % if show_elo:
        % if pgstat.elo_delta is not None:
          <td class="show-for-medium-up">${round(pgstat.elo_delta,2)}</td>
        % else:
          <td class="show-for-medium-up">-</td>
        % endif
      % endif
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
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-4">Nick</th>
    <th>Kills</th>
    <th>Deaths</th>
    <th>Suicides</th>
    <th>Objectives</th>
    <th class="medium-1">Score</th>
    % if show_elo:
      <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd in 'ca' 'dm' 'duel' 'rune' 'tdm':
<thead>
  <tr>
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-5 medium-3">Nick</th>
    <th>Kills</th>
    <th class="show-for-medium-up">Deaths</th>
    <th class="show-for-medium-up">Suicides</th>
    <th class="small-3 medium-1">Score</th>
    % if show_elo:
      <th class="show-for-medium-up">Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd == 'cq':
<thead>
  <tr>
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-2">Nick</th>
    <th>Kills</th>
    <th>Deaths</th>
    <th>Captured</th>
    <th>Released</th>
    <th>Score</th>
    % if show_elo:
      <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd == 'cts':
<thead>
  <tr>
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-2">Nick</th>
    <th>Fastest Time</th>
    <th>Deaths</th>
  </tr>
</thead>
% endif

% if game_type_cd == 'ctf':
<thead class="ctf ${pgstat.team_html_color()}">
  <tr>
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-5 medium-3">Nick</th>
    <th class="show-for-medium-up">Kills</th>
    <th>Caps</th>
    <th class="show-for-medium-up">Pickups</th>
    <th class="show-for-medium-up" title="Flag Carrier Kill">FCK</th>
    <th class="show-for-medium-up">Returns</th>
    <th class="medium-1">Score</th>
    % if show_elo:
      <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd == 'dom':
<thead class="dom ${pgstat.team_html_color()}">
  <tr>
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-2">Nick</th>
    <th>Kills</th>
    <th>Deaths</th>
    <th>Takes</th>
    <th>Ticks</th>
    <th>Score</th>
    % if show_elo:
      <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd in 'ft' 'freezetag':
<thead class="freezetag ${pgstat.team_html_color()}">
  <tr>
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-2">Nick</th>
    <th>Kills</th>
    <th>Deaths</th>
    <th>Revivals</th>
    <th>Score</th>
    % if show_elo:
      <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd in 'ka' 'keepaway':
<thead>
  <tr>
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-2">Nick</th>
    <th>Kills</th>
    <th>Deaths</th>
    <th>Pickups</th>
    <th>BC Time</th>
    <th>BC Kills</th>
    <th>Score</th>
    % if show_elo:
      <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd == 'kh':
<thead class="kh ${pgstat.team_html_color()}">
  <tr>
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-5 medium-3">Nick</th>
    <th class="show-for-medium-up">Kills</th>
    <th class="show-for-medium-up">Deaths</th>
    <th class="show-for-medium-up">Pickups</th>
    <th>Caps</th>
    <th class="show-for-medium-up">Losses</th>
    <th class="show-for-medium-up">KC Kills</th>
    <th class="small-3 medium-1">Score</th>
    % if show_elo:
      <th class="show-for-medium-up">Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd in 'nb' 'nexball':
<thead class="nb ${pgstat.team_html_color()}">
  <tr>
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-2">Nick</th>
    <th>Goals</th>
    <th>Faults</th>
    <th>Score</th>
    % if show_elo:
      <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd == 'rc':
<thead>
  <tr>
    % if show_latency:
      <th class="show-for-medium-up medium-1">Ping</th>
    % endif
    <th class="small-2">Nick</th>
    <th>Laps</th>
    <th>Fastest Lap</th>
    <th>Time</th>
  </tr>
</thead>
% endif

</%def>

##### SCOREBOARD ROWS #####
<%def name="scoreboard_row(game_type_cd, pgstat)">
% if game_type_cd == 'as':
  <td>${pgstat.kills}</td>
  <td>${pgstat.deaths}</td>
  <td>${pgstat.suicides}</td>
  <td>${pgstat.collects}</td>
% endif

% if game_type_cd in 'ca' 'dm' 'duel' 'rune' 'tdm':
  <td class="small-3">${pgstat.kills}</td>
  <td class="show-for-medium-up">${pgstat.deaths}</td>
  <td class="show-for-medium-up">${pgstat.suicides}</td>
% endif

% if game_type_cd == 'cq':
  <td>${pgstat.kills}</td>
  <td>${pgstat.deaths}</td>
  <td>${pgstat.captures}</td>
  <td>${pgstat.drops}</td>
% endif

% if game_type_cd == 'cts':
  % if pgstat.fastest is not None:
    <td>${round(float(pgstat.fastest.seconds) + (pgstat.fastest.microseconds/1000000.0), 2)}</td>
  % else:
    <td>-</td>
  % endif

  <td>${pgstat.deaths}</td>
% endif

% if game_type_cd == 'ctf':
  <td class="show-for-medium-up">${pgstat.kills}</td>
  <td>${pgstat.captures}</td>
  <td class="show-for-medium-up">${pgstat.pickups}</td>
  <td class="show-for-medium-up">${pgstat.carrier_frags}</td>
  <td class="show-for-medium-up">${pgstat.returns}</td>
% endif

% if game_type_cd == 'dom':
  <td>${pgstat.kills}</td>
  <td>${pgstat.deaths}</td>
  <td>${pgstat.pickups}</td>
  <td>${pgstat.drops}</td>
% endif

% if game_type_cd in 'ft' 'freezetag':
  <td>${pgstat.kills}</td>
  <td>${pgstat.deaths}</td>
  <td>${pgstat.revivals}</td>
% endif

% if game_type_cd in 'ka' 'keepaway':
  <td>${pgstat.kills}</td>
  <td>${pgstat.deaths}</td>
  <td>${pgstat.pickups}</td>

  % if pgstat.time is not None:
    <td>${round(float(pgstat.time.seconds) + (pgstat.time.microseconds/1000000.0), 2)}</td>
  % else:
    <td>-</td>
  % endif

  <td>${pgstat.carrier_frags}</td>
% endif

% if game_type_cd == 'kh':
  <td class="show-for-medium-up">${pgstat.kills}</td>
  <td class="show-for-medium-up">${pgstat.deaths}</td>
  <td class="show-for-medium-up">${pgstat.pickups}</td>
  <td class="show-for-medium-up">${pgstat.captures}</td>
  <td class="show-for-medium-up">${pgstat.drops}</td>
  <td>${pgstat.carrier_frags}</td>
% endif

% if game_type_cd in 'nb' 'nexball':
  <td>${pgstat.captures}</td>
  <td>${pgstat.drops}</td>
% endif

% if game_type_cd == 'rc':
  <td>${pgstat.laps}</td>

  % if pgstat.fastest is not None:
    <td>${round(float(pgstat.fastest.seconds) + (pgstat.fastest.microseconds/1000000.0), 2)}</td>
  % else:
    <td>-</td>
  % endif

  % if pgstat.time is not None:
    <td>${round(float(pgstat.time.seconds) + (pgstat.time.microseconds/1000000.0), 2)}</td>
  % else:
    <td>-</td>
  % endif
% endif

</%def>
