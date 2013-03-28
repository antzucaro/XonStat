<%inherit file="base.mako"/>
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="title">
% if game_type_cd == 'dm':
Deathmatch Rank Index
% elif game_type_cd == 'duel':
Duel Rank Index
% elif game_type_cd == 'tdm':
Team Deathmatch Rank Index
% elif game_type_cd == 'ctf':
Capture The Flag Rank Index
% endif
</%block>

<div class="row">
  <div class="span6 offset3">
    % if not ranks:
    <h2>Sorry, no ranks yet. Get some buddies together and start playing!</h2>

    % else:
    <table id="rank-index-table" class="table table-hover table-condensed" border="1">
      <tr>
        <th>Rank</th>
        <th>Nick</th>
        <th>Elo</th>
      </tr>
      <% i = 1 %>
      % for rank in ranks:
      <tr>
        <td>${rank.rank}</td>
        <td><a href="${request.route_url("player_info", id=rank.player_id)}" title="Go to this player's info page">${rank.nick_html_colors()|n}</a></th>
        <td>${round(rank.elo, 3)}</th>
      </tr>
      <% i += 1 %>
      % endfor
    </table>
  </div> <!-- /span6 -->
</div> <!-- /row -->

<div class="row">
  <div class="span6 offset3">
    <!-- navigation links -->
    ${navlinks("rank_index", ranks.page, ranks.last_page, game_type_cd=game_type_cd)}
  </div> <!-- /span6 -->
</div> <!-- /row -->
% endif
