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
  <div class="small-12 large-6 large-offset-3 columns">
    % if not ranks:
      <h2>Sorry, no ranks yet. Get some buddies together and start playing!</h2>

    % else:
      <table class="table table-hover table-condensed" border="1">
        <tr>
          <th class="small-2">Rank</th>
          <th class="small-8">Nick</th>
          <th class="small-2">Elo</th>
        </tr>
        <% i = 1 %>
        % for rank in ranks:
        <tr>
          <td>${rank.rank}</td>
          <td class="no-stretch"><a href="${request.route_url("player_info", id=rank.player_id)}" title="Go to this player's info page">${rank.nick_html_colors()|n}</a></th>
          <td>${int(round(rank.elo))}</th>
        </tr>
        <% i += 1 %>
        % endfor
      </table>
    % endif
  </div>
</div>

<div class="row">
  <div class="small-12 large-6 large-offset-3 columns">
    <!-- navigation links -->
    ${navlinks("rank_index", ranks.page, ranks.last_page, game_type_cd=game_type_cd)}
  </div>
</div>
