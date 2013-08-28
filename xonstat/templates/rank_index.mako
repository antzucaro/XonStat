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
  <div class="col-md-6 col-md-offset-3">
    % if not ranks:
    <h2>Sorry, no ranks yet. Get some buddies together and start playing!</h2>

    % else:
    <table id="rank-index-table" class="table table-hover table-condensed" border="1">
      <tr>
        <th style="width:40px;">Rank</th>
        <th style="width:420px;">Nick</th>
        <th style="width:90px;">Elo</th>
      </tr>
      <% i = 1 %>
      % for rank in ranks:
      <tr>
        <td>${rank.rank}</td>
        <td class="nostretch" style="max-width:420px;"><a href="${request.route_url("player_info", id=rank.player_id)}" title="Go to this player's info page">${rank.nick_html_colors()|n}</a></th>
        <td>${int(round(rank.elo))}</th>
      </tr>
      <% i += 1 %>
      % endfor
    </table>
  </div> <!-- /col-md-6 -->
</div> <!-- /row -->

<div class="row">
  <div class="col-md-6 col-md-offset-3">
    <!-- navigation links -->
    ${navlinks("rank_index", ranks.page, ranks.last_page, game_type_cd=game_type_cd)}
  </div> <!-- /col-md-6 -->
</div> <!-- /row -->
% endif
