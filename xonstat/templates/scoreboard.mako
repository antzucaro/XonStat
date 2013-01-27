<%def name="scoreboard(game_type_cd, pgstats, show_elo=False, show_latency=False)">
<table  class="table table-bordered table-condensed">
${scoreboard_header(game_type_cd, pgstats[0])}
  <tbody>
  % for pgstat in pgstats:
    <tr class="${pgstat.team_html_color()}">
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
      % if show_latency and pgstat.avg_latency is not None:
      <td>
        ${int(round(pgstat.avg_latency))}
      </td>
      % elif show_latency:
      <td></td>
      % endif
      ${scoreboard_row(game_type_cd, pgstat)}
      % if game_type_cd != 'cts':
      <td>${pgstat.score}</td>
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
      <th class="nick">Nick</th>
      % if show_latency:
      <th class="ping">Ping</th>
      % endif
      <th class="kills">Kills</th>
      <th class="deaths">Deaths</th>
      <th class="suicides">Suicides</th>
      <th class="objectives">Objectives</th>
      <th class="score">Score</th>
      % if show_elo:
      <th>Elo Change</th>
      % endif
    </tr>
    </thead>
% endif

% if game_type_cd in 'ca' 'dm' 'duel' 'tdm':
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
      % if show_elo:
      <th>Elo Change</th>
      % endif
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
      % if show_elo:
      <th>Elo Change</th>
      % endif
    </tr>
    </thead>
% endif

% if game_type_cd == 'freezetag':
    <thead class="freezetag ${pgstat.team_html_color()}">
    <tr>
      <th class="nick">Nick</th>
      % if show_latency:
      <th class="ping">Ping</th>
      % endif
      <th class="kills">Kills</th>
      <th class="deaths">Deaths</th>
      <th class="suicides">Suicides</th>
      <th class="score">Score</th>
      % if show_elo:
      <th>Elo Change</th>
      % endif
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

% if game_type_cd in 'ca' 'dm' 'duel' 'tdm':
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
        <td>${round(float(pgstat.fastest.seconds) + (pgstat.fastest.microseconds/1000000.0), 2)}</td>
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

% if game_type_cd == 'freezetag':
        <td>${pgstat.kills}</td>
        <td>${pgstat.deaths}</td>
        <td>${pgstat.suicides}</td>
% endif
</%def>
