<%inherit file="base.mako"/>

<%block name="title">
Game Information - ${parent.title()}
</%block>


% if game is None:
<h2>Sorry, that game wasn't found!</h2>

% else:
<h2>Game Detail</h2>
<ul>
   <li>ID: ${game.game_id}</li>
   <li>Time: ${game.start_dt}</li>
   <li>Game Type: ${game.game_type_cd}</li>
   <li>Server: ${game.server_id}</li>
   <li>Map: ${game.map_id}</li>
   <li>Duration: ${game.duration}</li>
   <li>Winner: ${game.duration}</li>
</ul>
% endif
