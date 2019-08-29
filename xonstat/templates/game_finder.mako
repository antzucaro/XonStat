<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
${nav.nav('games')}
</%block>

<%block name="title">
Game Index
</%block>

##### ROW OF GAME TYPE ICONS #####
<div class="row">
  <div class="small-12 columns">
    <ul class="tabs">
      % for gt, url in game_type_links:
        <li class="text-center tab-title
          % if game_type_cd == gt or (game_type_cd is None and gt == 'overall'):
            active
          % endif
          "
        >
          <a href="${url}" alt="${gt}" title="Show only ${gt} games">
            <span class="sprite sprite-${gt}"></span><br />
            ${gt} <br />
          </a>
        </li>
      % endfor
    </ul>
    <br />
  </div>
</div>

##### RECENT GAMES TABLE #####
<div class="row">
  <div class="small-12 columns">
    % if len(recent_games) > 0:
    <table class="table-hover table-condensed">
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
          <td class="text-center"><i class="sprite sprite-${rg.game_type_cd}" title="${rg.game_type_descr}"></i></td>
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
    % else:
    <h2>No more games to show!</h2>
    % endif
  </div>
</div>

% if len(recent_games) == 20:
<div class="row">
  <div class="small-12 columns">
    <ul class="pagination">
      <li>
        <a  href="${request.route_url('game_index', _query=query)}" name="Next Page">Next <i class="fa fa-arrow-right"></i></a>
      </li>
    </ul>
  </div>
</div>
% endif
