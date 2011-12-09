% if results == None:
<form action="${request.route_url("search")}" method="get">
    <input type="hidden" name="form.submitted" />
    Nick: <input type="text" name="nick" /> <br />
    <input type="submit" />
</form>
% endif

% if result_type == "player":
<table>
    <tr>
        <th>Player</th>
        <th>Joined</th>
    </tr>
    % for player in results:
    <tr>
        <td>${player.nick_html_colors()|n}</td>
        <td>${player.joined_pretty_date()}</td>
    </tr>
    % endfor
</table>
% endif
