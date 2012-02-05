<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
${nav.nav('players')}
</%block>

<%block name="title">
Player Index
</%block>

% if not players:
<h2>Sorry, no players yet. Get playing!</h2>

% else:
<div class="row">
  <div class="span6">
    <form method="get" action="${request.route_url('search')}">
      <input type="hidden" name="fs" />
      <input type="text" name="nick" />
      <input type="submit" value="search" />
    </form>
    <table class="table table-bordered table-condensed">
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

    ${navlinks("player_index_paged", players.page, players.last_page)}
  </div> <!-- /span4 -->
</div> <!-- /row -->
