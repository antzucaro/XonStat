<%inherit file="base.mako"/>

<%block name="title">
Leaderboard
</%block>

<%block name="css">
  ${parent.css()}
  <link href="/static/css/sprites.css" rel="stylesheet">
</%block>

<%block name="hero_unit">
  <div class="text-center">
    <img src="/static/css/img/web_background_l2.png" />
    % if stat_line is None:
    <p id="statline">Tracking Xonotic statistics since October 2011.</p>
    % else:
    <p id="statline">Tracking ${stat_line|n} since October 2011.</p>
    % endif

    % if day_stat_line is not None:
    <p id="statline">${day_stat_line|n} in the past 24 hours.</p>
    % endif
  </div>
</%block>

##### RANKS #####
% if len(ranks) < 4:
  <div class="row">
    <div class="span12">
      <p style="text-align: center;"><i class="icon-white icon-info-sign"> </i> You don't seem to have any ranks yet.</p>
    </div> <!-- span12 -->
  </div> <!-- row -->

% else:
  <div class="row">
    % for rs in ranks[:4]:
    % if len(rs) > 0:
    <div class="span3">
      % if rs[0].game_type_cd == 'duel':
      <h3>Duel Ranks</h3>
      % elif rs[0].game_type_cd == 'ctf':
      <h3>CTF Ranks</h3>
      % elif rs[0].game_type_cd == 'dm':
      <h3>DM Ranks</h3>
      % elif rs[0].game_type_cd == 'tdm':
      <h3>TDM Ranks</h3>
      % endif

      <table class="table table-hover table-condensed">
        <thead>
          <tr>
            <th style="width:40px;">#</th>
            <th style="width:150px;">Nick</th>
            <th style="width:60px;">Elo</th>
          </tr>
        </thead>
        <tbody>
        <% i = 1 %>
        % for r in rs:
        <tr>
          <td>${i}</td>
          <td class="nostretch" style="max-width:150px;"><a href="${request.route_url('player_info', id=r.player_id)}" title="Go to the player info page for this player">${r.nick_html_colors()|n}</a></td>
          <td>${int(round(r.elo))}</td>
        </tr>
        <% i = i+1 %>
        % endfor
        </tbody>
      </table>
      <p class="note"><a href="${request.route_url('rank_index', page=1, game_type_cd=rs[0].game_type_cd)}" title="See more ${rs[0].game_type_cd} rankings">More...</a></p>
    </div> <!-- /span4 -->
  % endif

  % endfor
</div> <!-- row -->
% endif


##### ACTIVE PLAYERS #####
<div class="row">
  <div class="span4">
    <h3>Most Active Players</h3>
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th style="width:40px;">#</th>
          <th style="width:150px;">Nick</th>
          <th class="play-time" style="width:90px;">Play Time</th>
        </tr>
      </thead>
      <tbody>
      <% i = 1 %>
      % for (player_id, nick, alivetime) in top_players:
        <tr>
          <td>${i}</td>
          % if player_id != '-':
          <td class="nostretch" style="max-width:150px;"><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${nick|n}</a></td>
          % else:
          <td class="nostretch" style="max-width:150px;">${nick|n}</td>
          % endif
          <td class="play-time">${alivetime}</td>
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
    <p class="note"><a href="${request.route_url('top_players_by_time', page=1)}" title="See more player activity">More...</a></p>
  </div> <!-- /span4 -->


##### ACTIVE SERVERS #####
  <div class="span4">
    <h3>Most Active Servers</h3>
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th style="width:40px;">#</th>
          <th style="width:180px;">Server</th>
          <th style="width:60px;">Games</th>
        </tr>
      </thead>
      <tbody>
      <% i = 1 %>
      % for (server_id, name, count) in top_servers:
        <tr>
          <td>${i}</td>
          % if server_id != '-':
          <td class="nostretch" style="max-width:180px;"><a href="${request.route_url('server_info', id=server_id)}" title="Go to the server info page for ${name}">${name}</a></td>
          % else:
          <td class="nostretch" style="max-width:180px;">${name}</td>
          % endif
          <td>${count}</td>
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
    <p class="note"><a href="${request.route_url('top_servers_by_players', page=1)}" title="See more server activity">More...</a></p>
  </div> <!-- /span4 -->


##### ACTIVE MAPS #####
  <div class="span4">
    <h3>Most Active Maps</h3>
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th style="width:40px;">#</th>
          <th style="width:180px;">Map</th>
          <th style="width:60px;">Games</th>
        </tr>
      </thead>
      <tbody>
      <% i = 1 %>
      % for (map_id, name, count) in top_maps:
        <tr>
          <td>${i}</td>
          % if map_id != '-':
          <td class="nostretch" style="max-width:180px;"><a href="${request.route_url('map_info', id=map_id)}" title="Go to the map info page for ${name}">${name}</a></td>
          % else:
          <td class="nostretch" style="max-width:180px;">${name}</td>
          % endif
          <td>${count}</td>
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
    <p class="note"><a href="${request.route_url('top_maps_by_times_played', page=1)}" title="See more map activity">More...</a></p>
  </div> <!-- /span4 -->
</div> <!-- /row -->
<row class="span12">
    <p class="note">*Most active stats are from the past 7 days</p>
</div>


##### RECENT GAMES #####
% if len(recent_games) > 0:
<div class="row">
  <div class="span12">
    <h3>Recent Games</h3>
    <table class="table table-hover table-condensed">
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
          <td class="tdcenter"><a class="btn btn-primary btn-small" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">view</a></td>
          <td class="tdcenter"><span class="sprite sprite-${rg.game_type_cd}" alt="${rg.game_type_cd}" title="${rg.game_type_descr}"></span></td>
          <td><a href="${request.route_url('server_info', id=rg.server_id)}" title="Go to the detail page for this server">${rg.server_name}</a></td>
          <td><a href="${request.route_url('map_info', id=rg.map_id)}" title="Go to the map detail page for this map">${rg.map_name}</a></td>
          <td><span class="abstime" data-epoch="${rg.epoch}" title="${rg.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${rg.fuzzy_date}</span></td>
          <td class="nostretch">
            % if rg.player_id > 2:
            <a href="${request.route_url('player_info', id=rg.player_id)}" title="Go to the player info page for this player">${rg.nick_html_colors|n}</a></td>
            % else:
            ${rg.nick_html_colors|n}</td>
            % endif
        </tr>
        % endfor
        </tbody>
    </table>
    <p><a href="${request.route_url('game_index')}">More...</a></p>
  </div> <!-- /span12 -->
</div> <!-- /row -->
% endif
