<%inherit file="base.mako"/>
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="title">
% if player:
Player Information for ${player.nick_html_colors()} - 
% endif

${parent.title()}
</%block>


% if player is None:
<h2>This player is so good we couldn't find him!</h2>
<p>Seriously though, he probably doesn't exist...just a figment of your imagination. Carry on then!</p>

% else:
<h2>${player.nick_html_colors()}</h2>
<p>
   Joined: ${player.create_dt.strftime('%m/%d/%Y at %I:%M %p')} <br />
</p>
% endif


##### STATS #####
% if game_stats:
<h2>Overall Game Stats</h2>
<table class="accuracy-table" border="1" cellpadding="3" align="center">
  <tr>
    <td>Playing Time</td><td>${game_stats['total_alivetime']}</td>
    <td>Drops</td><td>${game_stats['total_drops']}</td>
  </tr>
  <tr>
    <td>Average Rank</td><td>${game_stats['avg_rank']}</td>
    <td>Returns</td><td>${game_stats['total_returns']}</td>
  </tr>
  <tr>
    <td>Score</td><td>${game_stats['total_score']}</td>
    <td>Carrier Kills</td><td>${game_stats['total_carrier_frags']}</td>
  </tr>
  <tr>
    <td>Kills</td><td>${game_stats['total_kills']}</td>
    <td>Collects</td><td>${game_stats['total_collects']}</td>
  </tr>
  <tr>
    <td>Deaths</td><td>${game_stats['total_deaths']}</td>
    <td>Destroys</td><td>${game_stats['total_destroys']}</td>
  </tr>
  <tr>
    <td>Suicides</td><td>${game_stats['total_suicides']}</td>
    <td>Destroys (with key)</td><td>${game_stats['total_destroys']}</td>
  </tr>
  <tr>
    <td>Captures</td><td>${game_stats['total_captures']}</td>
    <td>Pushes</td><td>${game_stats['total_pushes']}</td>
  </tr>
  <tr>
    <td>Pickups</td><td>${game_stats['total_pickups']}</td>
    <td>Pushed</td><td>${game_stats['total_pushed']}</td>
  </tr>
</table>
% endif

##### ACCURACY #####
% if weapon_stats:
<h2>Overall Accuracy</h2>
${accuracy(weapon_stats)}
% endif


##### RECENT GAMES #####
% if recent_games:
<h2>Recent Games</h2>
% for (gamestat, game, server, map) in recent_games:
   <a href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">#${game.game_id}:</a> <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a> on <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a>
<br />
% endfor
<a href="${request.route_url("player_game_index", player_id=player.player_id, page=1)}" title="Game index for ${player.nick}">More games</a> played by ${player.nick_html_colors()}...
% endif

##### RECENT GAMES (v2) ####
<table class="accuracy-table" border="1" cellpadding="3" align="center">
<tr>
   <td>Game Type</td>
   <td>Map</td>
   <td>Result</td>
   <td>Played</td>
</tr>
% for (gamestat, game, server, map) in recent_games:
<tr>
   <td>${game.game_type_cd}</td>
   <td>${map.name}</td>
   <td>
   % if gamestat.team != None and gamestat.team == game.winner:
   Win
   % else:
   Loss
   % endif
   </td>
   <td>${game.start_dt}</td>
</tr>
% endfor
