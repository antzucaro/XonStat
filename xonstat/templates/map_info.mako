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
    <div class="small-12 large-4 columns">
      <h5>Top Scoring Players</h5>
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-2">#</th>
            <th class="small-7">Nick</th>
            <th class="small-4">Score</th>
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
            <th class="small-2">#</th>
            <th class="small-7">Nick</th>
            <th class="small-4">Time</th>
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
      <h5>Most Active Servers</h5>
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-2">#</th>
            <th class="small-7">Name</th>
            <th class="small-4"># Games</th>
          </tr>
        </thead>
        <tbody>
        <% i = 1 %>
        % for (server_id, name, times_played) in top_servers:
          <tr>
            <td>${i}</td>
            <td class="no-stretch" style="max-width:150px;"><a href="${request.route_url('server_info', id=server_id)}" title="Go to the server info page for this server">${name}</a></td>
            <td>${times_played}</td>
          </tr>
          <% i = i+1 %>
        % endfor
        </tbody>
      </table>
    </div>
  </div> <!-- /row -->

  <div class="row">
    <div class="small-12 columns">
      <small>*Most active stats are from the past 7 days</small>
    </div>
  </div>

  % if len(captimes) > 0:
  <div class="row">
    <div class="small-12 large-6 columns">
      <h5>Best Flag Capture Times <a href="${request.route_url('map_captimes', id=gmap.map_id)}" title="See more flag capture times for ${gmap.name}"><i class="fa fa-plus-circle"></i></a></h5>
      <table class="table-hover table-condensed">
        <thead>
          <tr>
             <th class="small-8">Nick</th>
             <th class="small-4">Captime</th>
          </tr>
        </thead>
        <tbody>
        % for c in captimes:
          <tr>
            <td class="no-stretch">
            % if c.player_id > 2:
              <a href="${request.route_url("player_info", id=c.player_id)}"
               title="Go to the info page for this player">
              <span>${c.nick_html_colors|n}</span>
              </a>
            % else:
              <span>${c.nick_html_colors|n}</span>
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

  % if len(recent_games) > 0:
  <div class="row">
    <div class="small-12 columns">
      <h5>Most Recent Games</h5>
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-1 text-center"></th>
            <th class="small-1">Type</th>
            <th class="show-for-medium-up small-3">Server</th>
            <th class="show-for-large-up small-3">Time</th>
            <th class="small-3">Winner</th>
          </tr>
        </thead>
        <tbody>
          % for rg in recent_games:
          <tr>
            <td class="text-center"><a class="tiny button" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">View</a></td>
            <td class="text-center"><span class="sprite sprite-${rg.game_type_cd}" alt="${rg.game_type_cd}" title="${rg.game_type_descr}"></span></td>
            <td class="show-for-medium-up"><a href="${request.route_url('server_info', id=rg.server_id)}" title="Go to the detail page for this server">${rg.server_name}</a></td>
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
      <p><a href="${request.route_url('game_index', _query={'map_id':gmap.map_id})}">More...</a></p>
    </div>
  </div>
  % endif

% endif
