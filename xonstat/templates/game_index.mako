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
<div id="filter">
	<h2>Filter</h2>
	<input id="search" type="text" name="search" />
	<input id="show-bots" type="checkbox" class="checkbox" checked="checked" /><label for="show-bots" class="checkbox-label">Show Bots</label><br />
	<h3>Gametype</h3>
	<input id="game-ca" type="checkbox" class="checkbox" /><label for="game-ca" class="checkbox-label">CA</label><br />
	<input id="game-ctf" type="checkbox" class="checkbox" /><label for="game-ctf" class="checkbox-label">CTF</label><br />
	<input id="game-dm" type="checkbox" class="checkbox" /><label for="game-dm" class="checkbox-label">DM</label><br />
	<input id="game-freezetag" type="checkbox" class="checkbox" /><label for="game-freezetag" class="checkbox-label">Freezetag</label><br />
	<h3>Sort By</h3>
	<select id="sort-by">
		<option>Kills</option>
		<option>Deaths</option>
		<option>Suicides</option>
		<option>Time</option>
		<option>Score</option>
	</select>
</div>
<div id="recent-games-list">
	<h2>Recent Games</h2>
	% for (game, server, map) in games:
	<div class="game">
		<img src="/static/images/icons/48x48/${game.game_type_cd}.png"/><h3><a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a> on <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a> <span class="permalink">(<a href="${request.route_url('game_info', id=game.game_id)}" name="Permalink for game #${game.game_id}">permalink</a>)</span></h3>
	## show scoreboard using a def from another file
	${scoreboard(game.game_type_cd, pgstats[game.game_id])}
	</div>
% endfor

<!-- navigation links -->
${navlinks("game_index_paged", games.page, games.last_page)}

</div><!-- #recent-games-list -->
% endif

