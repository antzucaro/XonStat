<%inherit file="base.mako"/>
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="title">
Accuracy Information - ${parent.title()}
</%block>


% if weapon_stats is None or pgstat is None or game is None:
<h2>Sorry, I can't find those weapon stats!</h2>
<p>Assume the best, though. Really.</p>

% else:
<h2>Player Accuracy for <a href="${request.route_url("player_info", id=pgstat.player_id)}" title="Info page for this player">${pgstat.nick_html_colors()}</a> in Game <a href="" title="">${game.game_id}</a>:</h2>

## ACCURACY TABLE
% if weapon_stats:
${accuracy(weapon_stats)}
% endif

% endif
