<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
${nav.nav('servers')}
</%block>

<%block name="title">
% if server:
Server Information
% endif
</%block>

<%block name="css">
    ${parent.css()}
    <link href="/static/css/sprites.css" rel="stylesheet">
</%block>

% if server is None:
<h2>Sorry, that server wasn't found!</h2>

% else:
<div class="row">
  <div class="span12">
    <h2>${server.name}</h2>
    <p>
      IP Address: ${server.ip_addr} <br />
      Revision: ${server.revision} <br />
      Added <span class="abstime" data-epoch="${server.epoch()}" title="${server.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${server.fuzzy_date()}</span> <br />
    </p>
  </div>
</div>


<div class="row">
  <div class="span4">
    <h3>Top Scoring Players</h3>
      <table class="table table-hover table-condensed">
        <thead>
          <tr>
            <th style="width:40px;">#</th>
            <th style="width:150px;">Nick</th>
            <th style="width:90px;">Score</th>
          </tr>
        </thead>
        <tbody>
        <% i = 1 %>
        % for (score_player_id, score_nick, score_value) in top_scorers:
          <tr>
            <td>${i}</td>
            % if score_player_id != '-':
            <td class="nostretch" style="max-width:150px;"><a href="${request.route_url('player_info', id=score_player_id)}" title="Go to the player info page for this player">${score_nick|n}</a></td>
            % else:
            <td class="nostretch" style="max-width:150px;">${score_nick}</td>
            % endif
            <td>${score_value}</td>
          </tr>
        <% i = i+1 %>
        % endfor
        </tbody>
      </table>
      <p class="note">*Most active stats are from the past 7 days</p>
  </div> <!-- /span4 -->


  <div class="span4">
    <h3>Most Active Players</h3>
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th style="width:40px;">#</th>
          <th style="width:150px;">Nick</th>
          <th style="width:90px;">Playing Time</th>
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
          <td class="nostretch" style="max-width:150px;">${nick}</td>
          % endif
          <td>${alivetime}</td>
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
  </div> <!-- /span4 -->


  <div class="span4">
    <h3>Most Active Maps</h3>
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th style="width:40px;">#</th>
          <th style="width:150px;">Map</th>
          <th style="width:120px;"># Games</th>
        </tr>
      </thead>
      <tbody>
      <% i = 1 %>
      % for (map_id, name, count) in top_maps:
        <tr>
          <td>${i}</td>
          % if map_id != '-':
          <td class="nostretch" style="max-width:150px;"><a href="${request.route_url('map_info', id=map_id)}" title="Go to the map info page for ${name}">${name}</a></td>
          % else:
          <td class="nostretch" style="max-width:150px;">${name}</td>
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
    <h3>Most Recent Games</h2>
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th></th>
          <th>Type</th>
          <th>Map</th>
          <th>Time</th>
          <th>Winner</th>
        </tr>
      </thead>
      <tbody>
        % for rg in recent_games:
        <tr>
          <td class="tdcenter"><a class="btn btn-primary btn-small" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">View</a></td>
          <td class="tdcenter"><span class="sprite sprite-${rg.game_type_cd}" alt="${rg.game_type_cd}" title="${rg.game_type_descr}"></span></td>
          <td><a href="${request.route_url('map_info', id=rg.map_id)}" title="Go to the map detail page for this map">${rg.map_name}</a></td>
          <td><span class="abstime" data-epoch="${rg.epoch}" title="${rg.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${rg.fuzzy_date}</span></td>
          <td>
            % if rg.player_id > 2:
            <a href="${request.route_url('player_info', id=rg.player_id)}" title="Go to the player info page for this player">${rg.nick_html_colors|n}</a>
            % else:
            ${rg.nick_html_colors|n}
            % endif
          </td>
        </tr>
        % endfor
      </tbody>
    </table>
    <p><a href="${request.route_url('game_finder', _query={'server_id':server.server_id})}">More...</a></p>
  </div>
</div>
% endif


% endif
