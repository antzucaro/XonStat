<%inherit file="base.mako"/>

<%block name="title">
Main Page - ${parent.title()}
</%block>

<div id="sidebar" class="leaderboard left">

##### TOP PLAYERS #####
<h2>Top Players</h2>
<table id="top-players">
	<thead>
		<tr>
			<th>#</th>
			<th>Nick</th>
			<th>Score</th>
		</tr>
	</thead>
	<tbody>
	<% i = 1 %>
	% for (player_id, nick, score) in top_players:
		<tr>
			<td>${i}</td>
			% if player_id != '-':
			<td><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${nick|n}</a></td>
			% else:
			<td>${nick}</td>
			% endif
			<td>${score}</td>
		</tr>
		<% i = i+1 %>
	% endfor
	</tbody>
</table>

##### TOP SERVERS #####
<h2>Top Servers</h2>
<table id="top-servers">
	<thead>
		<tr>
			<th>#</th>
			<th>Server</th>
			<th>Games</th>
		</tr>
	</thead>
	<tbody>
	<% i = 1 %>
	% for (server_id, name, count) in top_servers:
		<tr>
			<td>${i}</td>
			% if server_id != '-':
			<td><a href="${request.route_url('server_info', id=server_id)}" title="Go to the server info page for ${name}">${name}</a></td>
			% else:
			<td>${name}</td>
			% endif
			<td>${count}</td>
		</tr>
		<% i = i+1 %>
	% endfor
	</tbody>
</table>

##### TOP MAPS #####
<h2>Top Maps</h2>
<table id="top-maps">
	<thead>
		<tr>
			<th>#</th>
			<th>Map</th>
			<th>Times Played</th>
		</tr>
	</thead>
	<tbody>
	<% i = 1 %>
	% for (map_id, name, count) in top_maps:
		<tr>
			<td>${i}</td>
			% if map_id != '-':
			<td><a href="${request.route_url('map_info', id=map_id)}" title="Go to the map info page for ${name}">${name}</a></td>
			% else:
			<td>${name}</td>
			% endif
			<td>${count}</td>
		</tr>
		<% i = i+1 %>
	% endfor
	</tbody>
</table>
</div> <!-- END LEADERBOARD -->

<div id="main" class="right">

##### RECENT GAMES #####
<h2>Recent Games</h2>
<table id="recent-games">
	<thead>
		<tr>
			<th>Game #</th>
			<th>Type</th>
			<th>Server</th>
			<th>Map</th>
			<th>Time</th>
			<th>Winner</th>
		</tr>
	</thead>
	<tbody>
	% for (game, server, map) in recent_games:
		% if game != '-':
		<tr>
			<td><a href="${request.route_url('game_info', id=game.game_id)}" title="View detailed information about this game">${game.game_id}</a></td>
			<td>${game.game_type_cd}</td>
			<td><a href="${request.route_url('server_info', id=server.server_id)}" title="Go to the detail page for this server">${server.name}</a></td>
			<td><a href="${request.route_url('map_info', id=map.map_id)}" title="Go to the map detail page for this map">${map.name}</a></td>
			<td>${game.start_dt.strftime('%m/%d/%Y %H:%M')}</td>
			<td>${game.winner}</td>
		</tr>
		% else:
		<tr>
			<td>-</td>
			<td>-</td>
			<td>-</td>
			<td>-</td>
			<td>-</td>
			<td>-</td>
		</tr>
		% endif
    % endfor
    </tbody>
</table>
</div> <!-- END RECENT GAMES -->
