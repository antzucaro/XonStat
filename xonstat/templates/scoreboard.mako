<%def name="scoreboard(game_type_cd, pgstats)">
<table class="scoreboard">
${scoreboard_header(game_type_cd, pgstats[0])}
	<tbody>
	% for pgstat in pgstats:
		<tr class="${pgstat.team_html_color()}">
			<td>
			% if pgstat.player_id > 2:
			  <a href="${request.route_url("player_info", id=pgstat.player_id)}"
			   title="Go to the info page for this player">
			  <span class="nick">${pgstat.nick_html_colors()|n}</span>
			  </a>
			% else:
			  <span class="nick">${pgstat.nick_html_colors()|n}</span>
			% endif
			</td>
		${scoreboard_row(game_type_cd, pgstat)}
			<td>${pgstat.score}</td>
			<td>
			% if pgstat.player_id > 1:
			  <a href="${request.route_url("game_info", id=pgstat.game_id)}#accuracy-${pgstat.player_game_stat_id}"
			   title="View weapon accuracy details for this player in this game">
			  View
			  </a>
			% endif
			</td>
		</tr>
	% endfor
	</tbody>
</table>
</%def>

##### SCOREBOARD HEADER #####
<%def name="scoreboard_header(game_type_cd, pgstat)">
% if game_type_cd == 'dm' or game_type_cd == 'tdm':
    <thead>
		<tr>
			<th class="nick">Nick</th>
			<th class="kills">Kills</th>
			<th class="deaths">Deaths</th>
			<th class="suicides">Suicides</th>
			<th class="score">Score</th>
			<th class="accuracy">Accuracy</th>
		</tr>
    </thead>
% endif

% if game_type_cd == 'ctf':
    <thead class="ctf ${pgstat.team_html_color()}">
		<tr>
			<th class="nick">Nick</th>
			<th class="kills">Kills</th>
			<th class="captures">Captures</th>
			<th class="pickups">Pickups</th>
			<th class="fck" title="Flag Carrier Kill">FCK</th>
			<th class="returns">Returns</th>
			<th class="score">Score</th>
			<th class="accuracy">Accuracy</th>
		</tr>
    </thead>
% endif

% if game_type_cd == 'ca':
    <thead class="ca ${pgstat.team_html_color()}">
		<tr>
			<th class="nick">Nick</th>
			<th class="kills">Kills</th>
			<th class="score">Score</th>
			<th class="accuracy">Accuracy</th>
		</tr>
    </thead>
% endif

% if game_type_cd == 'freezetag':
    <thead class="freezetag ${pgstat.team_html_color()}">
		<tr>
			<th class="nick">Nick</th>
			<th class="kills">Kills</th>
			<th class="deaths">Deaths</th>
			<th class="suicides">Suicides</th>
			<th class="score">Score</th>
			<th class="accuracy">Accuracy</th>
		</tr>
    </thead>
% endif
</%def>

##### SCOREBOARD ROWS #####
<%def name="scoreboard_row(game_type_cd, pgstat)">
% if game_type_cd == 'dm' or game_type_cd == 'tdm':
        <td>${pgstat.kills}</td>
        <td>${pgstat.deaths}</td>
        <td>${pgstat.suicides}</td>
% endif

% if game_type_cd == 'ctf':
        <td>${pgstat.kills}</td>
        <td>${pgstat.captures}</td>
        <td>${pgstat.pickups}</td>
        <td>${pgstat.carrier_frags}</td>
        <td>${pgstat.returns}</td>
% endif

% if game_type_cd == 'ca':
        <td>${pgstat.kills}</td>
% endif

% if game_type_cd == 'freezetag':
        <td>${pgstat.kills}</td>
        <td>${pgstat.deaths}</td>
        <td>${pgstat.suicides}</td>
% endif
</%def>
