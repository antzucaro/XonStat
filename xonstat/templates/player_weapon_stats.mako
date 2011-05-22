<%inherit file="base.mako"/>

<%block name="title">
Accuracy Information - ${parent.title()}
</%block>


% if pwstats is None or pgstat is None or game is None:
<h2>Sorry, I can't find those weapon stats!</h2>
<p>Assume the best, though. Really.</p>

% else:
<h2>Player Accuracy for ${pgstat.nick_html_colors()} in Game:</h2>
<table border="1" cellpadding="3">
    <tr>
        <td>Weapon</td>
        <td>Fired</td>
        <td>Hit</td>
        <td>Potential Damage</td>
        <td>Actual Damage</td>
        <td>Frags</td>
    </tr>

% for (pwstat, weapon) in pwstats:
    <tr>
        <td>${weapon.descr}</td>
        <td>${pwstat.fired}</td>
        <td>${pwstat.hit}</td>
        <td>${pwstat.max}</td>
        <td>${pwstat.actual}</td>
        <td>${pwstat.frags}</td>
    </tr>
% endfor
</table>
% endif
