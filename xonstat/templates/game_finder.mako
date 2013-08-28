<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
${nav.nav('games')}
</%block>

<%block name="css">
    ${parent.css()}
    <link href="/static/css/sprites.css" rel="stylesheet">
</%block>

<%block name="title">
Game Index
</%block>

% if len(recent_games) > 0:

##### ROW OF GAME TYPE ICONS #####
<div class="row">
  <div class="col-md-12 tabbable">
    <ul class="nav nav-tabs">
      % for gt in ('overall','duel','ctf','dm','tdm','ca','kh','ft','lms','as','dom','nb','cts','rc'):
      <li 
      % if game_type_cd == gt or (game_type_cd is None and gt == 'overall'):
      class="active"
      % endif
      >

      % if gt == 'overall':
      <a href="${request.route_url("game_index")}" alt="${gt}" title="" data-toggle="none">
      % else:
      <a href="${request.route_url("game_index", _query={'type':gt})}" alt="${gt}" title="" data-toggle="none">
      % endif
        <span class="sprite sprite-${gt}"> </span><br />
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
  <div class="col-md-12">
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th></th>
          <th>Type</th>
          <th>Server</th>
          <th>Map</th>
          <th>Time</th>
          <th>Winner</th>
        </tr>
      </thead>
      <tbody>
      % for rg in recent_games.items:
        <tr>
          <td class="tdcenter"><a class="btn btn-primary btn-sm" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">view</a></td>
          <td class="tdcenter"><span alt="${rg.game_type_cd}" class="sprite sprite-${rg.game_type_cd}" title="${rg.game_type_descr}"></span></td>
          <td><a href="${request.route_url('server_info', id=rg.server_id)}" title="Go to the detail page for this server">${rg.server_name}</a></td>
          <td><a href="${request.route_url('map_info', id=rg.map_id)}" title="Go to the map detail page for this map">${rg.map_name}</a></td>
          <td><span class="abstime" data-epoch="${rg.epoch}" title="${rg.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${rg.fuzzy_date}</span></td>
          <td>
            % if rg.player_id > 2:
            <a href="${request.route_url('player_info', id=rg.player_id)}" title="Go to the player info page for this player">${rg.nick_html_colors|n}</a></td>
            % else:
            ${rg.nick_html_colors|n}</td>
            % endif
        </tr>
        % endfor
        </tbody>
    </table>
  </div> <!-- /col-md-12 -->
</div> <!-- /row -->

<!-- navigation links -->
${navlinks("game_index", recent_games.page, recent_games.last_page, search_query=query)}
% endif
