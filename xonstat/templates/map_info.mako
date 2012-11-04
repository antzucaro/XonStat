<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
${nav.nav('maps')}
</%block>

<%block name="title">
% if gmap:
Map Information
% endif

${parent.title()}
</%block>


% if gmap is None:
<h2>Sorry, that map wasn't found!</h2>

% else:
<h2>${gmap.name}</h2>
<p>
  Added <span class="abstime" data-epoch="${gmap.epoch()}" title="${gmap.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${gmap.fuzzy_date()}</span>
</p>
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
  </div>


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
</div>


<div class="span4">
  <h3>Most Active Servers</h3>
  <table class="table table-bordered table-condensed">
    <thead>
      <tr>
        <th>#</th>
        <th>Name</th>
        <th>Times Played</th>
      </tr>
    </thead>
    <tbody>
    <% i = 1 %>
    % for (server_id, name, times_played) in top_servers:
      <tr>
        <td>${i}</td>
        <td><a href="${request.route_url('server_info', id=server_id)}" title="Go to the server info page for this server">${name}</a></td>
        <td>${times_played}</td>
      </tr>
      <% i = i+1 %>
    % endfor
    </tbody>
</table>
</div>
</div> <!-- /row -->

% if len(captimes) > 0:
<div class="row">
  <div class="span6">
    <h3>Best Flag Capture Times</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
           <th>Nick</th>
           <th>Captime</th>
        </tr>
      </thead>
      <tbody>
      % for c in captimes:
        <tr>
          <td>
          % if c.player_id > 2:
            <a href="${request.route_url("player_info", id=c.player_id)}"
             title="Go to the info page for this player">
            <span class="nick">${c.nick_html_colors|n}</span>
            </a>
          % else:
            <span class="nick">${c.nick_html_colors|n}</span>
          % endif
          </td>
          <td>
            <a href="${request.route_url("game_info", id=c.game_id)}"
             title="View the game in which this cap was made">
              ${round(float(c.fastest_cap.seconds) + (c.fastest_cap.microseconds/1000000.0), 2)}
            </a>
          </td>
        </tr>
      % endfor
      </tbody>
    </table>
  </div>
</div>
% endif


<div class="row">
  <div class="span12">
    <h3>Recent Games</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th></th>
          <th>Type</th>
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
          <td><span class="abstime" data-epoch="${game.epoch()}" title="${game.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${game.fuzzy_date()}</span></td>
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
        </tr>
        % endif
    % endfor
        </tbody>
    </table>
  </div>
</div>


% endif
