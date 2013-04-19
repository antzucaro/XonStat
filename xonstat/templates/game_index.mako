<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="scoreboard.mako" import="scoreboard" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="css">
${parent.css()}
<link href="/static/css/sprites.css" rel="stylesheet">
</%block>

<%block name="navigation">
${nav.nav('games')}
</%block>

<%block name="title">
Game Index
</%block>

% if not games:
<h2>Sorry, no 
  % if game_type_descr:
  ${game_type_descr}
  % endif
  games yet. Get playing!</h2>

% else:
<div class="row">
  <div class="span12">
    <h2>Recent 
    % if game_type_descr:
    ${game_type_descr}
    % endif
      Games</h2>
  </div>
</div>
<div class="row">
  <div class="span12 tabbable">
    <ul class="nav nav-tabs">
      % for gt in ('overall','duel','ctf','dm','tdm','ca','kh','ft','lms','as','dom','nb','cts','rc'):
      ##% for gt in ('overall','duel','ctf','dm','tdm','ca','kh','ft','lms','as','dom','nb','cts','rc'):
      <li>
      % if gt == 'overall':
      <a href="${request.route_url("game_index")}" alt="${gt}" title="" data-toggle="none">
      % else:
      <a href="${request.route_url("game_index", _query={'game_type_cd':gt})}" alt="${gt}" title="" data-toggle="none">
      % endif
        <span class="sprite sprite-${gt}"> </span><br />
        ${gt} <br />
      </a>
      </li>
      % endfor
    </ul>
  </div>
  <div class="span12 offset1 tab-content">
    % for rg in games.items:
    <div class="game">
      <img src="/static/images/icons/48x48/${rg.game_type_cd}.png" width="30" height="30" alt="${rg.game_type_cd}" title="${rg.game_type_descr}"/>
      <h4><a href="${request.route_url("map_info", id=rg.map_id)}" name="Map info page for ${rg.map_name}">${rg.map_name}</a> on <a href="${request.route_url("server_info", id=rg.server_id)}" name="Server info page for ${rg.server_name}">${rg.server_name}</a> <span class="permalink">(<a href="${request.route_url('game_info', id=rg.game_id)}" name="Permalink for game #${rg.game_id}">permalink</a>)</span></h4>
      <span class="clear"></span>
      ${scoreboard(rg.game_type_cd, pgstats[rg.game_id])}
    </div>
    % endfor
  </div>
</div>

<div class="row">
  <div class="span10 offset1">
    <!-- navigation links -->
    ${navlinks("game_index", games.page, games.last_page, search_query=request.GET)}
  </div>
</div>
% endif

