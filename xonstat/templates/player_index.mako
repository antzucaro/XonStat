<%inherit file="base.mako"/>
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="title">
Player Index - ${parent.title()}
</%block>

% if not players:
<h2>Sorry, no players yet. Get playing!</h2>

% else:
<h2>Player Index</h2>
<form method="get" action="${request.route_url('search')}">
    <input type="hidden" name="fs" />
    <input type="text" name="nick" />
    <input type="submit" value="search" />
</form>
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

<!-- navigation links -->
${navlinks("player_index_paged", players.page, players.last_page)}
