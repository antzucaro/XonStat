<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="scoreboard.mako" import="scoreboard" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
${nav.nav('games')}
</%block>

<%block name="title">
Game Index
</%block>

% if not games:
<h2>Sorry, no games yet. Get playing!</h2>

% else:
<div class="row">
  <div class="span12">
    <h2>Recent Games</h2>
    % for (game, server, map) in games:
    <div class="game">
      <h4><img src="/static/images/icons/48x48/${game.game_type_cd}.png" width="30" height="30" /><a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a> on <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a> <span class="permalink">(<a href="${request.route_url('game_info', id=game.game_id)}" name="Permalink for game #${game.game_id}">permalink</a>)</span></h4>
      ${scoreboard(game.game_type_cd, pgstats[game.game_id])}
    </div>
    % endfor
  </div>
</div>

<!-- navigation links -->
${navlinks("game_index_paged", games.page, games.last_page)}
% endif

