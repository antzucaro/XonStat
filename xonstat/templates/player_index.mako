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
  <div class="span6 offset3">
    <form class="indexform" method="get" action="${request.route_url('search')}">
      <input type="hidden" name="fs" />
      <input class="indexbox" type="text" name="nick" />
      <input type="submit" value="search" />
    </form>
    <table class="table table-hover table-condensed">
      <tr>
        <th style="width:100px;">Player ID</th>
        <th>Nick</th>
        <th class="create-dt">Joined</th>
      </tr>
    % for player in players:
      <tr>
        <td>${player.player_id}</th>
        <td class="player-nick"><a href="${request.route_url("player_info", id=player.player_id)}" title="Go to this player's info page">${player.nick_html_colors()|n}</a></th>
        <td><span class="abstime" data-epoch="${player.epoch()}" title="${player.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${player.joined_pretty_date()}</span></th>
      </tr>
    % endfor
    </table>
% endif

    ${navlinks("player_index", players.page, players.last_page)}
  </div> <!-- /span4 -->
</div> <!-- /row -->
