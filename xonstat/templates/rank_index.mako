<%inherit file="base.mako"/>
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="title">
Rank Index - ${parent.title()}
</%block>

% if not ranks:
<h2>Sorry, no ranks yet. Get some buddies together and start playing!</h2>

% else:
<h2>
% if game_type_cd == 'dm':
Deathmatch 
% elif game_type_cd == 'duel':
Duel 
% elif game_type_cd == 'tdm':
Team Deathmatch 
% elif game_type_cd == 'ctf':
Capture The Flag 
% endif

Rank Index</h2>
<table id="rank-index-table" border="1">
  <tr>
    <th>Rank</th>
    <th>Nick</th>
    <th>Elo</th>
  </tr>
<% i = 1 %>
% for (rank, player) in ranks:
  <tr>
    <td>${i}</td>
    <td><a href="${request.route_url("player_info", id=rank.player_id)}" title="Go to this player's info page">${player.nick_html_colors()|n}</a></th>
    <td>${round(rank.elo, 3)}</th>
  </tr>
<% i += 1 %>
% endfor
</table>

<!-- navigation links -->
${navlinks("rank_index_paged", ranks.page, ranks.last_page)}
% endif
