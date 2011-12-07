<%inherit file="base.mako"/>

<%block name="title">
Player Index - ${parent.title()}
</%block>

% if not players:
<h2>Sorry, no players yet. Get playing!</h2>

% else:
<h2>Player Index</h2>
<table id="player-index-table" border="1">
  <tr>
    <th>Nick</th>
    <th class="create-dt">Joined</th>
  </tr>
% for player in players:
  <tr>
    <td><a href="${request.route_url("player_info", id=player.player_id)}" title="Go to this player's info page">${player.nick_html_colors()|n}</a></th>
    <td>${player.joined_pretty_date()}</th>
  </tr>
% endfor
</table>
% endif

<!-- pagination -->
<a class="pagination" href="${request.route_url("player_index_paged", page=1)}" name="First Page"><<</a>

% if players.previous_page:
<a class="pagination" href="${request.route_url("player_index_paged", page=players.previous_page)}" name="Previous Page"><</a>
% endif

% for page in pages_to_link:
<a class="pagination" href="${request.route_url("player_index_paged", page=page)}" name="Go to page ${page}">${page}</a>
% endfor

% if players.next_page:
<a class="pagination" href="${request.route_url("player_index_paged", page=players.next_page)}" name="Next Page">></a>
% endif

<a class="pagination" href="${request.route_url("player_index_paged", page=players.last_page)}" name="Last Page">>></a>

(Page <a href="${request.route_url("player_index_paged", page=players.page)}" name="Go to page ${players.page}">${players.page}</a> of <a href="${request.route_url("player_index_paged", page=players.last_page)}" name="Last Page">${players.last_page}</a>)
