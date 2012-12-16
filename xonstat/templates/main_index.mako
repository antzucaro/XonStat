<%inherit file="base.mako"/>

<%block name="title">
Leaderboard
</%block>

<%block name="css">
    ${parent.css()}
    <link href="/static/css/sprites.css" rel="stylesheet">
</%block>

<%block name="hero_unit">
      <div class="hero-unit">
        <img src="/static/css/img/web_background_l2.png" />
        % if summary_stats is None:
        <p id="statline">Tracking Xonotic statistics since October 2011.</p>
        % else:
        <p id="statline">Tracking <a href="${request.route_url('player_index')}">${summary_stats.total_players}</a> players, <a href="${request.route_url('game_index')}">${summary_stats.total_games}</a> games (${summary_stats.duel_games} duel, ${summary_stats.ctf_games} ctf, ${summary_stats.dm_games} dm), and <a href="${request.route_url('server_index')}">${summary_stats.total_servers}</a> servers since October 2011.</p>
        % endif
      </div>
</%block>

<div class="row">
  <div class="span4">
    ##### DUEL RANKS #####
    <h3>Duel Ranks</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th>#</th>
          <th>Nick</th>
          <th>Elo</th>
        </tr>
      </thead>
      <tbody>
      <% i = 1 %>
      % for (player_id, nick, elo) in duel_ranks:
        <tr>
          <td>${i}</td>
          % if player_id != '-':
          <td><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${nick|n}</a></td>
          % else:
          <td>${nick|n}</td>
          % endif
          % if elo != '-':
          <td>${round(elo, 3)}</td>
          % else:
          <td>${elo}</td>
          % endif
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
    <p class="note"><a href="${request.route_url('rank_index', page=1, game_type_cd='duel')}" title="See more duel rankings">More...</a></p>
  </div> <!-- /span4 -->

  <div class="span4">
    ##### CTF RANKS #####
    <h3>CTF Ranks</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th>#</th>
          <th>Nick</th>
          <th>Elo</th>
        </tr>
      </thead>
      <tbody>
      <% i = 1 %>
      % for (player_id, nick, elo) in ctf_ranks:
        <tr>
          <td>${i}</td>
          % if player_id != '-':
          <td><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${nick|n}</a></td>
          % else:
          <td>${nick|n}</td>
          % endif
          % if elo != '-':
          <td>${round(elo, 3)}</td>
          % else:
          <td>${elo}</td>
          % endif
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
    <p class="note"><a href="${request.route_url('rank_index', page=1, game_type_cd='ctf')}" title="See more CTF rankings">More...</a></p>
  </div> <!-- /span4 -->

  <div class="span4">
    ##### DM RANKS #####
    <h3>DM Ranks</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th>#</th>
          <th>Nick</th>
          <th>Elo</th>
        </tr>
      </thead>
      <tbody>
      <% i = 1 %>
      % for (player_id, nick, elo) in dm_ranks:
        <tr>
          <td>${i}</td>
          % if player_id != '-':
          <td><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${nick|n}</a></td>
          % else:
          <td>${nick|n}</td>
          % endif
          % if elo != '-':
          <td>${round(elo, 3)}</td>
          % else:
          <td>${elo}</td>
          % endif
        </tr>
        <% i = i+1 %>
      % endfor
    </tbody>
  </table>
  <p class="note"><a href="${request.route_url('rank_index', page=1, game_type_cd='dm')}" title="See more deathmatch rankings">More...</a></p>
  </div> <!-- /span4 -->
</div> <!-- /row -->

<div class="row">
  <div class="span4">
    <h3>Most Active Players</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th>#</th>
          <th>Nick</th>
          <th class="play-time">Play Time</th>
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
          <td>${nick|n}</td>
          % endif
          <td class="play-time">${alivetime}</td>
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
    <p class="note">*Most active stats are from the past 7 days</p>
  </div> <!-- /span4 -->

  <div class="span4">
    <h3>Most Active Servers</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th>#</th>
          <th>Server</th>
          <th>Games</th>
        </tr>
      </thead>
      <tbody>
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
      </tbody>
    </table>
  </div> <!-- /span4 -->

  <div class="span4">
    <h3>Most Active Maps</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th>#</th>
          <th>Map</th>
          <th>Games</th>
        </tr>
      </thead>
      <tbody>
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
      </tbody>
    </table>
  </div> <!-- /span4 -->
</div> <!-- /row -->

% if len(recent_games) > 0:
<div class="row">
  <div class="span12">
    <h3>Recent Games</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th></th>
          <th>Type</th>
          <th>Server</th>
          <th>Map</th>
          <th>Time</th>
          <th>Winner</th>
        </tr>
      </thead>
      <tbody>
      % for rg in recent_games:
        <tr>
          <td><a class="btn btn-primary btn-small" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">view</a></td>
          <!-- <td class="gt_icon"><img title="${rg.game_type_cd}" src="/static/images/icons/24x24/${rg.game_type_cd}.png" alt="${rg.game_type_cd}" /></td> -->
          <td><span class="sprite sprite-${rg.game_type_cd}" title="${rg.game_type_cd}"></span></td>
          <td><a href="${request.route_url('server_info', id=rg.server_id)}" title="Go to the detail page for this server">${rg.server_name}</a></td>
          <td><a href="${request.route_url('map_info', id=rg.map_id)}" title="Go to the map detail page for this map">${rg.map_name}</a></td>
          <td><span class="abstime" data-epoch="${rg.epoch}" title="${rg.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${rg.fuzzy_date}</span></td>
          <td>
            % if rg.player_id > 2:
            <a href="${request.route_url('player_info', id=rg.player_id)}" title="Go to the player info page for this player">${rg.nick_html_colors|n}</a></td>
            % else:
            ${rg.nick_html_colors|n}</td>
            % endif
        </tr>
        % endfor
        </tbody>
    </table>
  </div> <!-- /span12 -->
</div> <!-- /row -->
% endif
