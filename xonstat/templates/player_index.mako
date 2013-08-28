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
  <div class="col-md-6 col-md-offset-3">
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
        <th></th>
      </tr>
    % for player in players:
      <tr>
        <td>${player.player_id}</th>
        <td class="player-nick"><a href="${request.route_url("player_info", id=player.player_id)}" title="Go to this player's info page">${player.nick_html_colors()|n}</a></th>
        <td><span class="abstime" data-epoch="${player.epoch()}" title="${player.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${player.joined_pretty_date()}</span></th>
        <td class="tdcenter">
          <a href="${request.route_url("player_game_index", player_id=player.player_id, page=1)}" title="View recent games by this player">
            <i class="glyphicon glyphicon-list"></i>
          </a>
        </td>
      </tr>
    % endfor
    </table>
% endif

    ${navlinks("player_index", players.page, players.last_page)}
  </div> <!-- /col-md-4 -->
</div> <!-- /row -->
