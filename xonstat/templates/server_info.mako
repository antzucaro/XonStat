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

% if server is None:
  <h2>Sorry, that server wasn't found!</h2>

% else:
  <div class="row">
    <div class="small-12 columns">
      <h2>${server.name}</h2>
      <p>
        IP Address: 
        % if server.port is not None:
        ${server.ip_addr}:${server.port}
        % else:
        ${server.ip_addr}
        % endif
        <br />
        Revision: ${server.revision} <br />
        Added <span class="abstime" data-epoch="${server.epoch()}" title="${server.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${server.fuzzy_date()}</span> <br />
      </p>
    </div>
  </div>


  <div class="row">
    <div class="small-12 large-4 columns">
      <h5>Top Scoring Players</h5>
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th style="small-2">#</th>
            <th style="small-7">Nick</th>
            <th style="small-3">Score</th>
          </tr>
        </thead>
        <tbody>
        <% i = 1 %>
        % for (score_player_id, score_nick, score_value) in top_scorers:
          <tr>
            <td>${i}</td>
            % if score_player_id != '-':
              <td class="no-stretch"><a href="${request.route_url('player_info', id=score_player_id)}" title="Go to the player info page for this player">${score_nick|n}</a></td>
            % else:
              <td class="no-stretch">${score_nick}</td>
            % endif
            <td>${score_value}</td>
          </tr>
          <% i = i+1 %>
        % endfor
        </tbody>
      </table>
    </div>

    <div class="small-12 large-4 columns">
      <h5>Most Active Players</h5>
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th style="small-2">#</th>
            <th style="small-7">Nick</th>
            <th style="small-3">Play Time</th>
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
              <td class="no-stretch">${nick}</td>
            % endif
            <td>${alivetime}</td>
          </tr>
          <% i = i+1 %>
        % endfor
        </tbody>
      </table>
    </div>

    <div class="small-12 large-4 columns">
      <h5>Most Active Maps</h5>
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th style="small-2">#</th>
            <th style="small-7">Map</th>
            <th style="small-3"># Games</th>
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
              <td class="no-stretch">${name}</td>
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


  % if len(recent_games) > 0:
    <div class="row">
      <div class="small-12 columns">
        <h5>Most Recent Games</h5>
        <table class="table-hover table-condensed">
          <thead>
            <tr>
              <th class="small-1 text-center"></th>
              <th class="small-1">Type</th>
              <th class="show-for-medium-up small-3">Map</th>
              <th class="show-for-large-up small-3">Time</th>
              <th class="small-3">Winner</th>
            </tr>
          </thead>
          <tbody>
            % for rg in recent_games:
            <tr>
              <td class="text-center"><a class="tiny button" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">View</a></td>
              <td class="text-center"><span class="sprite sprite-${rg.game_type_cd}" alt="${rg.game_type_cd}" title="${rg.game_type_descr}"></span></td>
              <td class="show-for-medium-up"><a href="${request.route_url('map_info', id=rg.map_id)}" title="Go to the map detail page for this map">${rg.map_name}</a></td>
              <td class="show-for-large-up"><span class="abstime" data-epoch="${rg.epoch}" title="${rg.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${rg.fuzzy_date}</span></td>
              <td class="no-stretch">
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
        <p><a href="${request.route_url('game_index', _query={'server_id':server.server_id})}">More...</a></p>
      </div>
    </div>
  % endif
% endif
