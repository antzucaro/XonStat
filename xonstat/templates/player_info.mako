<%inherit file="base.mako"/>

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

% if recent_games:
<h2>Recent Games</h2>
<ul>
% for (gamestat, game, server, map) in recent_games:
   <li><a href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">#${game.game_id}:</a> <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a> on <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a></li>
% endfor
</ul>
<a href="${request.route_url("player_game_index", player_id=player.player_id, page=1)}" title="Game index for ${player.nick}">More games</a> played by ${player.nick_html_colors()}...
% endif


% if weapon_stats:
<h2>Accuracy</h2>
<table border="1" cellpadding="3">
<tr>
    <td></td>
    <td>Weapon</td>
    <td>Hit</td>
    <td>Fired</td>
    <td>Hit %</td>
    <td>Actual Damage</td>
    <td>Potential Damage</td>
    <td>Damage %</td>
</tr>
% for weapon_stat in weapon_stats:
<%
if weapon_stat[2] > 0: 
    damage_pct = round(float(weapon_stat[1])/weapon_stat[2]*100, 2)
else:
    damage_pct = 0
if weapon_stat[4] > 0: 
    hit_pct = round(float(weapon_stat[3])/weapon_stat[4]*100, 2)
else:
    hit_pct = 0
%>
<tr>
    <td>[IMAGE]</td>
    <td>${weapon_stat[0]}</td>
    <td>${weapon_stat[3]}</td>
    <td>${weapon_stat[4]}</td>
    <td>${hit_pct}%</td>
    <td>${weapon_stat[1]}</td>
    <td>${weapon_stat[2]}</td>
    <td>${damage_pct}%</td>
</tr>
% endfor
</table>

% endif
