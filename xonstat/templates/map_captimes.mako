<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
  ${nav.nav('maps')}
</%block>

<%block name="title">
  Map captimes
</%block>

% if len(captimes) == 0:
  <h2>Sorry, no caps yet. Get playing!</h2>
  <p><a href="${map_url}">Back to map info page</a></p>

% else:
  <div class="row">
    <div class="small-12 columns">

      <h2>${map.name}</h2>
      <p><a href="${request.route_url('map_info', id=map.map_id)}">Back to map info page</a></p>

      <h5>Fastest Flag Captures:</h5>

      <table class="table-bordered table-condensed">
        <thead>
          <tr>
            <th class="small-2 medium-1">Game</th>
            <th class="small-2">Captime</th>
            <th class="small-4">Nick</th>
            <th class="show-for-medium-up medium-3">Server</th>
            <th class="show-for-medium-up medium-2">Date</th>
          </tr>
        </thead>
        <tbody>
        % for ct in captimes.items:
          <tr>
            <td class="text-center"><a class="tiny button" href="${request.route_url('game_info', id=ct.game_id)}" title="View detailed information about this game">view</a></td>
            <td>${ct.fastest_cap.total_seconds()} seconds</td>
            <td class="no-stretch">
              % if ct.player_id > 2:
                <a href="${request.route_url('player_info', id=ct.player_id)}" title="Go to the player info page for this player">${ct.player_nick_html|n}</a>
              % else:
                ${rg.nick_html_colors|n}
              % endif
            </td>
            <td class="show-for-medium-up"><a href="${request.route_url('server_info', id=ct.server_id)}" title="Go to the detail page for this server">${ct.server_name}</a></td>
            <td class="show-for-medium-up"><span class="abstime" data-epoch="${ct.create_dt_epoch}" title="${ct.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${ct.create_dt_fuzzy}</span></td>
        % endfor
        </tbody>
      </table>
    </div>
  </div>

  <!-- navigation links -->
  ${navlinks("map_captimes", captimes.page, captimes.last_page, id=map_id, search_query=request.GET)}
% endif
