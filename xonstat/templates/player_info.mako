<%inherit file="base.mako"/>
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="css">
${parent.css()}
<link rel="stylesheet" href="/static/css/colorbox.css" type="text/css" media="screen" />
</%block>

<%block name="js">
${parent.js()}
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.5.2/jquery.min.js"></script>
<script src="/static/js/jquery.colorbox-min.js"></script>
<script>
$(document).ready(function(){
    $(".recent_game_box").colorbox({width:"80%", height:"80%", iframe:true});
});
</script>
</%block>

<%block name="title">
% if player:
Player Information for ${player.nick_strip_colors()} - 
% endif

${parent.title()}
</%block>


% if player is None:
<h2>This player is so good we couldn't find him!</h2>
<p>Seriously though, he probably doesn't exist...just a figment of your imagination. Carry on then!</p>

% else:
<h2>${player.nick_html_colors()|n}</h2>
<p>
   Member Since: ${player.create_dt.strftime('%m/%d/%Y at %I:%M %p')} <br />
   Last Seen: ${recent_games[0][1].fuzzy_date()} <br />
   Playing Time: ${game_stats['total_alivetime']} <br />
   Games Played: ${game_stats['total_games_played']} <br />
   Average Rank: ${game_stats['avg_rank']} <br />
</p>
% endif


##### STATS #####
% if game_stats:
<h2>Overall Game Stats</h2>
<table border="1" cellpadding="3">
  
  <tr>
    <th>Score</td><td>${game_stats['total_score']}</td>
    <th>Carrier Kills</td><td>${game_stats['total_carrier_frags']}</td>
  </tr>
  <tr>
    <th>Kills</td><td>${game_stats['total_kills']}</td>
    <th>Collects</td><td>${game_stats['total_collects']}</td>
  </tr>
  <tr>
    <th>Deaths</td><td>${game_stats['total_deaths']}</td>
    <th>Destroys</td><td>${game_stats['total_destroys']}</td>
  </tr>
  <tr>
    <th>Suicides</td><td>${game_stats['total_suicides']}</td>
    <th>Destroys (with key)</td><td>${game_stats['total_destroys']}</td>
  </tr>
  <tr>
    <th>Captures</td><td>${game_stats['total_captures']}</td>
    <th>Pushes</td><td>${game_stats['total_pushes']}</td>
  </tr>
  <tr>
    <th>Pickups</td><td>${game_stats['total_pickups']}</td>
    <th>Pushed</td><td>${game_stats['total_pushed']}</td>
  </tr>
  <tr>
    <th>Drops</td><td>${game_stats['total_drops']}</td>
    <th>Returns</td><td>${game_stats['total_returns']}</td>
  </tr>
</table>
% endif

##### ACCURACY #####
% if weapon_stats:
<h2>Overall Accuracy</h2>
${accuracy(weapon_stats)}
% endif


##### RECENT GAMES (v2) ####
% if recent_games:
<h2>Recent Games</h2>
<table border="1" cellpadding="3">
<tr class='table-header'>
   <td>Game Type</td>
   <td>Map</td>
   <td>Result</td>
   <td>Played</td>
   <td>Permalink</td>
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
   <td>${game.fuzzy_date()}</td>
   <td><a class="recent_game_box" href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">View</a></td>
</tr>
% endfor
</table>
<a href="${request.route_url("player_game_index", player_id=player.player_id, page=1)}" title="Game index for ${player.nick}">More games</a> played by ${player.nick_html_colors()|n}...
% endif
