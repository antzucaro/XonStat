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
    <img src="/static/css/img/xonotic-logo.png" />
    % if stat_line is None:
      <p class="statline">Tracking Xonotic statistics since October 2011.</p>
    % else:
      <p class="statline">Tracking ${stat_line|n} since October 2011.</p>
    % endif

    % if day_stat_line is not None:
      <p class="statline">${day_stat_line|n} in the past 24 hours.</p>
    % endif
  </div>
</%block>

##### RANKS #####
% if len(ranks) < 4:
  <div class="row">
    <div class="small-12 large-12 columns">
      <p class="text-center"><i class="icon-white icon-info-sign"> </i> You don't seem to have any ranks yet.</p>
    </div>
  </div>

% else:
  <div class="row">
    % for rs in ranks[:4]:
      % if len(rs) > 0:
        <div class="small-12 large-3 columns">
          % if rs[0].game_type_cd == 'duel':
            <h5>Duel Ranks <a href="${request.route_url('rank_index', game_type_cd=rs[0].game_type_cd)}" title="See more ${rs[0].game_type_cd} rankings"><i class="fa fa-plus-circle"></i></a></h5>
          % elif rs[0].game_type_cd == 'ctf':
            <h5>CTF Ranks <a href="${request.route_url('rank_index', game_type_cd=rs[0].game_type_cd)}" title="See more ${rs[0].game_type_cd} rankings"><i class="fa fa-plus-circle"></i></a></h5>
          % elif rs[0].game_type_cd == 'dm':
            <h5>DM Ranks <a href="${request.route_url('rank_index', game_type_cd=rs[0].game_type_cd)}" title="See more ${rs[0].game_type_cd} rankings"><i class="fa fa-plus-circle"></i></a></h5>
          % elif rs[0].game_type_cd == 'tdm':
            <h5>TDM Ranks <a href="${request.route_url('rank_index', game_type_cd=rs[0].game_type_cd)}" title="See more ${rs[0].game_type_cd} rankings"><i class="fa fa-plus-circle"></i></a></h5>
          % endif

          <table class="table-hover table-condensed">
            <thead>
              <tr>
                <th class="small-2">#</th>
                <th class="small-7">Nick</th>
                <th class="small-3">Elo</th>
              </tr>
            </thead>
            <tbody>
            <% i = 1 %>
            % for r in rs:
            <tr>
              <td>${i}</td>
              <td class="no-stretch"><a href="${request.route_url('player_info', id=r.player_id)}" title="Go to the player info page for this player">${r.nick_html_colors()|n}</a></td>
              <td>${int(round(r.elo))}</td>
            </tr>
            <% i = i+1 %>
            % endfor
            </tbody>
          </table>
    </div>
  % endif

  % endfor
</div>
% endif


##### ACTIVE PLAYERS #####
<div class="row">
  <div class="small-12 large-4 columns">
    <h5>Most Active Players <a href="${request.route_url('top_players_by_time', page=1)}" title="See more player activity"><i class="fa fa-plus-circle"></i></a></h5>
      <table class="table table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-2">#</th>
            <th class="small-7">Nick</th>
            <th class="small-3">Time</th>
          </tr>
        </thead>
        <tbody>
        <% i = 1 %>
        % for (player_id, nick, alivetime) in top_players:
          <tr>
            <td>${i}</td>
            % if player_id != '-':
            <td class="no-stretch"><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${nick|n}</a></td>
            % else:
            <td class="no-stretch" style="max-width:150px;">${nick|n}</td>
            % endif
            <td>${alivetime}</td>
          </tr>
          <% i = i+1 %>
        % endfor
        </tbody>
      </table>
  </div>


##### ACTIVE SERVERS #####
  <div class="small-12 large-4 columns">
    <h5>Most Active Servers <a href="${request.route_url('top_servers_by_players', page=1)}" title="See more server activity"><i class="fa fa-plus-circle"></i></a></h5>
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th class="small-2">#</th>
          <th class="small-7">Server</th>
          <th class="small-3">Games</th>
        </tr>
      </thead>
      <tbody>
      <% i = 1 %>
      % for (server_id, name, count) in top_servers:
        <tr>
          <td>${i}</td>
          % if server_id != '-':
          <td class="no-stretch"><a href="${request.route_url('server_info', id=server_id)}" title="Go to the server info page for ${name}">${name}</a></td>
          % else:
          <td>${name}</td>
          % endif
          <td>${count}</td>
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
  </div>


##### ACTIVE MAPS #####
  <div class="small-12 large-4 columns">
    <h5>Most Active Maps <a href="${request.route_url('top_maps_by_times_played', page=1)}" title="See more map activity"><i class="fa fa-plus-circle"></i></a></h5>
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th class="small-2">#</th>
          <th class="small-7">Map</th>
          <th class="small-3">Games</th>
        </tr>
      </thead>
      <tbody>
      <% i = 1 %>
      % for (map_id, name, count) in top_maps:
        <tr>
          <td>${i}</td>
          % if map_id != '-':
          <td class="no-stretch"><a href="${request.route_url('map_info', id=map_id)}" title="Go to the map info page for ${name}">${name}</a></td>
          % else:
          <td>${name}</td>
          % endif
          <td>${count}</td>
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
  </div>
</div>
<div class="row">
  <div class="small-12 columns">
    <small>*Most active stats are from the past 7 days</small>
  </div>
</div>


##### RECENT GAMES #####
% if len(recent_games) > 0:
<div class="row">
  <div class="small-12 columns">
    <h5>Recent Games <a href="${request.route_url('game_index')}"><i class="fa fa-plus-circle"></i></a></h5>
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th class="small-1 text-center"></th>
          <th class="small-1">Type</th>
          <th class="show-for-medium-up small-3">Server</th>
          <th class="show-for-medium-up small-2">Map</th>
          <th class="show-for-large-up small-2">Time</th>
          <th class="small-3">Winner</th>
        </tr>
      </thead>
      <tbody>
      % for rg in recent_games:
        <tr>
          <td class="text-center"><a class="button tiny" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">view</a></td>
          <td class="text-center"><span class="sprite sprite-${rg.game_type_cd}" alt="${rg.game_type_cd}" title="${rg.game_type_descr}"></span></td>
          <td class="show-for-medium-up no-stretch"><a href="${request.route_url('server_info', id=rg.server_id)}" title="Go to the detail page for this server">${rg.server_name}</a></td>
          <td class="show-for-medium-up"><a href="${request.route_url('map_info', id=rg.map_id)}" title="Go to the map detail page for this map">${rg.map_name}</a></td>
          <td class="show-for-large-up"><span class="abstime" data-epoch="${rg.epoch}" title="${rg.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${rg.fuzzy_date}</span></td>
          <td class="no-stretch">
            % if rg.player_id > 2:
            <a href="${request.route_url('player_info', id=rg.player_id)}" title="Go to the player info page for this player">${rg.nick_html_colors|n}</a></td>
            % else:
            ${rg.nick_html_colors|n}</td>
            % endif
        </tr>
        % endfor
        </tbody>
    </table>
  </div>
</div>
% endif
