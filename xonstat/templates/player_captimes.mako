<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
  ${nav.nav('players')}
</%block>

<%block name="title">
  Player captimes
</%block>

% if len(captimes) == 0:
  <h2>Sorry, no caps yet. Get playing!</h2>
  <p><a href="${request.route_url('player_info', id=player.player_id)}">Back to player info page</a></p>
% else:

  <div class="row">
    <div class="small-12 columns">
      <h4>Fastest Flag Captures by
        <a href="${request.route_url('player_info', id=player.player_id)}">
          ${player.nick_html_colors()|n}
        </a>
      </h4>

   
      <table class="table-hover table-condensed">
        <thead>
          <tr>
             <th class="small-2 medium-1">Game</th>
             <th class="small-2">Captime</th>
             <th class="small-3">Map</th>
             <th class="show-for-medium-up small-4">Server</th>
             <th class="show-for-medium-up small-2">Date</th>
          </tr>
        </thead>
        <tbody>
        % for ct in captimes.items:
          <tr>
            <td class="text-center"><a class="tiny button" href="${request.route_url('game_info', id=ct.game_id)}" title="View detailed information about this game">view</a></td>
            <td>${ct.fastest_cap.total_seconds()} seconds</td>
            <td><a href="${request.route_url('map_info', id=ct.map_id)}" title="Go to the detail page for this map">${ct.map_name}</a></td>
            <td class="show-for-medium-up"><a href="${request.route_url('server_info', id=ct.server_id)}" title="Go to the detail page for this server">${ct.server_name}</a></td>
            <td class="show-for-medium-up"><span class="abstime" data-epoch="${ct.create_dt_epoch}" title="${ct.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${ct.create_dt_fuzzy}</span></td>
        % endfor
        </tbody>
      </table>

      % if sort == "fastest":
          <p>* sorted by fastest - sort by <a href="${request.route_url('player_captimes', player_id=player.player_id, _query={"sort":"create_dt", "page":page})}">most recent</a> instead</p>
      % else:
          <p>* sorted by most recent - sort by <a href="${request.route_url('player_captimes', player_id=player.player_id, _query={"sort":"fastest", "page":page})}">fastest</a> instead</p>
      % endif

    </div>
  </div>

  <!-- navigation links -->
  ${navlinks("player_captimes", captimes.page, captimes.last_page, player_id=player_id, search_query=request.GET)}
% endif
