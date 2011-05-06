<%inherit file="base.mako"/>

<%block name="title">
% if player:
Player Information for ${player.nick} - 
% endif

${parent.title()}
</%block>


% if player is None:
<h2>Sorry, that player wasn't found!</h2>

% else:
<h2>Player Detail</h2>
<ul>
   <li>Nickname: ${player.nick}</li>
   <li>ID: ${player.player_id}</li>
   <li>Location: ${player.location}</li>
   <li>Joined: ${player.create_dt}</li>
</ul>
% endif

% if recent_games:
<h2>Recent Games</h2>
<ul>
% for (game_id, server_name, map_name) in recent_games:
   <li>Game #${game_id} on ${server_name}: ${map_name}</li>
% endfor
</ul>
% endif
