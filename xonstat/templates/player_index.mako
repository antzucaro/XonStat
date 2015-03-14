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
    <div class="small-12 large-6 large-offset-3 columns">

      <form method="get" action="${request.route_url('search')}">
        <div class="row">
          <div class="small-7 columns">
            <input type="hidden" name="fs" />
            <input type="text" name="nick" />
          </div>
          <div class="small-5 columns">
            <input type="submit" value="search" />
          </div>
        </div>
      </form>

      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-3">Player ID</th>
            <th class="small-5">Nick</th>
            <th class="small-3">Joined</th>
            <th class="small-1"></th>
          </tr>
        </thead>
      % for player in players:
        <tr>
          <td>${player.player_id}</th>
          <td class="no-stretch"><a href="${request.route_url("player_info", id=player.player_id)}" title="Go to this player's info page">${player.nick_html_colors()|n}</a></th>
          <td><span class="abstime" data-epoch="${player.epoch()}" title="${player.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${player.joined_pretty_date()}</span></th>
          <td class="text-center">
            <a href="${request.route_url("player_game_index", player_id=player.player_id, page=1)}" title="View recent games by this player">
              <i class="fa fa-list"></i>
            </a>
          </td>
        </tr>
      % endfor
      </table>

      ${navlinks("player_index", players.page, players.last_page)}
    </div>
  </div>
% endif
