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
  <div class="span12">
    <h2>${server.name}</h2>
    <p>
      IP Address: ${server.ip_addr} <br />
      Revision: ${server.revision} <br />
      Added <span title="${server.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${server.fuzzy_date()}</span> <br />
    </p>
  </div>
</div>


<div class="row">
  <div class="span4">
    <h3>Top Scoring Players</h3>
      <table class="table table-bordered table-condensed">
        <thead>
          <tr>
            <th>#</th>
            <th>Nick</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
        <% i = 1 %>
        % for (score_player_id, score_nick, score_value) in top_scorers:
          <tr>
            <td>${i}</td>
            % if score_player_id != '-':
            <td><a href="${request.route_url('player_info', id=score_player_id)}" title="Go to the player info page for this player">${score_nick|n}</a></td>
            % else:
            <td>${score_nick}</td>
            % endif
            <td>${score_value}</td>
          </tr>
        <% i = i+1 %>
        % endfor
        </tbody>
      </table>
  </div> <!-- /span4 -->


  <div class="span4">
    <h3>Most Active Players</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th>#</th>
          <th>Nick</th>
          <th>Playing Time</th>
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
          <td>${nick}</td>
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
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th>#</th>
          <th>Map</th>
          <th># Games</th>
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



<div class="row">
  <div class="span12">
    <h3>Recent Games</h2>
    <table class="table table-bordered table-condensed">
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
      % for (game, srv, map, pgstat) in recent_games:
        % if game != '-':
        <tr>
          <td><a class="btn btn-primary btn-small" href="${request.route_url('game_info', id=game.game_id)}" title="View detailed information about this game">View</a></td>
          <td class="gt_icon"><img title="${game.game_type_cd}" src="/static/images/icons/24x24/${game.game_type_cd}.png" alt="${game.game_type_cd}" /></td>
          <td><a href="${request.route_url('map_info', id=map.map_id)}" title="Go to the map detail page for this map">${map.name}</a></td>
          <td><span title="${game.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${game.fuzzy_date()}</span></td>
          <td>
          % if pgstat.player_id > 2:
            <a href="${request.route_url('player_info', id=pgstat.player_id)}" title="Go to the player info page for this player">${pgstat.nick_html_colors()|n}</a>
          </td>
          % else:
            ${pgstat.nick_html_colors()|n}
          </td>
          % endif
        </tr>
            % else:
            <tr>
              <td>-</td>
              <td>-</td>
              <td>-</td>
              <td>-</td>
              <td>-</td>
            </tr>
            % endif
        % endfor
        </tbody>
    </table>
  </div>
</div>


% endif
