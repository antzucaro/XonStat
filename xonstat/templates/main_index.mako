<%inherit file="base.mako"/>

<%block name="title">
Main Page - ${parent.title()}
</%block>

<table>
<tr>
<th>Nick</th>
<th>Score</th>
</tr>
% for (player_id, nick, score) in top_players:
<tr>
<td>${nick}</td>
<td>${score}</td>
</tr>
% endfor

% for i in range(10 - len(top_players)):
<tr>
<td>-</td>
<td>-</td>
</tr>
% endfor
</table>
