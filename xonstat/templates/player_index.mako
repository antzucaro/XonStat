<%inherit file="base.mako"/>

<%block name="title">
Player Index - ${parent.title()}
</%block>

% if not players:
<h2>Sorry, no players yet. Get playing!</h2>

% else:
<h2>Player Index</h2>
<table border="1">
  <tr>
    <th>#</th>
    <th>Nick</th>
    <th>Joined</th>
  </tr>
% for player in players:
  <tr>
    <td>${player.player_id}</th>
    <td><a href="${request.route_url("player_info", id=player.player_id)}" title="Go to this player's info page">${player.nick_html_colors()}</a></th>
    <td>${player.create_dt.strftime('%m/%d/%Y at %H:%M')}</th>
  </tr>
% endfor
</table>
% endif

% if players.previous_page:
<a href="${request.route_url("player_index_paged", page=players.previous_page)}" name="Previous Page">Previous</a>
% endif
% if players.next_page:
<a href="${request.route_url("player_index_paged", page=players.next_page)}" name="Next Page">Next</a>
% endif
