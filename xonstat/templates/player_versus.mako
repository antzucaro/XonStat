<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
  ${nav.nav('players')}
</%block>

<div class="row">
  <div class="small-5 columns text-right">
    <h3>${p1.nick_html_colors()|n}</h3>
  </div>

  <div class="small-2 columns text-center">
    <h3>vs</h3>
  </div>

  <div class="small-5 columns text-left">
    <h3>${p2.nick_html_colors()|n}</h3>
  </div>
</div>

<div class="row">
  <div class="small-5 columns text-right">
    <h3>${p1_wins}</h3>
  </div>

  <div class="small-2 columns text-center">
    <h3>wins</h3>
  </div>

  <div class="small-5 columns text-left">
    <h3>${p2_wins}</h3>
  </div>
</div>

% if len(recent_games) > 0:
<div class="row">
  <div class="small-12 columns">
    <h5>Recent Games</h5>
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
