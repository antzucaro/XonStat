<%def name="scoreboard(game_type_cd, pgstats, show_elo=False, show_latency=False)">
<table  class="table-hover table-condensed">
  ${scoreboard_header(game_type_cd, pgstats[0])}
  <tbody>
  % for pgstat in pgstats:
    <tr class="${pgstat.team_html_color()}">
      % if show_latency and pgstat.avg_latency is not None:
        <td class="text-center">
          ${int(round(pgstat.avg_latency))}
        </td>
      % elif show_latency:
        <td class="text-center">-</td>
      % endif

      <td class="no-stretch">
        % if pgstat.player_id > 2:
          <a href="${request.route_url("player_info", id=pgstat.player_id)}"
            title="Go to the info page for this player">
            <span class="small-2">${pgstat.nick_html_colors()|n}</span>
          </a>
        % else:
          <span class="small-2">${pgstat.nick_html_colors()|n}</span>
        % endif
      </td>

      ${scoreboard_row(game_type_cd, pgstat)}

      % if game_type_cd != 'cts':
        <td class="player-score">${pgstat.score}</td>
      % endif

      % if show_elo:
        % if pgstat.elo_delta is not None:
          <td>${round(pgstat.elo_delta,2)}</td>
        % else:
          <td>-</td>
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
      <th class="small-1">Ping</th>
    % endif
    <th class="small-2">Nick</th>
    <th>Kills</th>
    <th>Deaths</th>
    <th>Suicides</th>
    <th>Objectives</th>
    <th>Score</th>
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
      <th class="small-1">Ping</th>
    % endif
    <th class="small-2">Nick</th>
    <th>Kills</th>
    <th>Deaths</th>
    <th>Suicides</th>
    <th>Score</th>
    % if show_elo:
      <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd == 'cq':
<thead>
  <tr>
    % if show_latency:
      <th class="small-1">Ping</th>
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
      <th class="small-1">Ping</th>
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
      <th class="small-1">Ping</th>
    % endif
    <th>Nick</th>
    <th>Kills</th>
    <th>Captures</th>
    <th>Pickups</th>
    <th title="Flag Carrier Kill">FCK</th>
    <th>Returns</th>
    <th>Score</th>
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
      <th class="small-1">Ping</th>
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
      <th class="small-1">Ping</th>
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
      <th class="small-1">Ping</th>
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
      <th class="small-1">Ping</th>
    % endif
    <th class="small-2">Nick</th>
    <th>Kills</th>
    <th>Deaths</th>
    <th>Pickups</th>
    <th>Captures</th>
    <th>Losses</th>
    <th>KC Kills</th>
    <th>Score</th>
    % if show_elo:
      <th>Elo Change</th>
    % endif
  </tr>
</thead>
% endif

% if game_type_cd in 'nb' 'nexball':
<thead class="nb ${pgstat.team_html_color()}">
  <tr>
    % if show_latency:
      <th class="small-1">Ping</th>
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
      <th class="small-1">Ping</th>
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
  <td>${pgstat.kills}</td>
  <td>${pgstat.deaths}</td>
  <td>${pgstat.suicides}</td>
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
  <td>${pgstat.kills}</td>
  <td>${pgstat.captures}</td>
  <td>${pgstat.pickups}</td>
  <td>${pgstat.carrier_frags}</td>
  <td>${pgstat.returns}</td>
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
  <td>${pgstat.kills}</td>
  <td>${pgstat.deaths}</td>
  <td>${pgstat.pickups}</td>
  <td>${pgstat.captures}</td>
  <td>${pgstat.drops}</td>
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
