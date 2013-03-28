<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
${nav.nav('games')}
</%block>

<%block name="title">
Recent Games
</%block>

% if not games:
<h2>Sorry, no games yet. Get playing!</h2>

% else:
<div class="row">
  <div class="span12">
    <h3>Recent Games by ${player.nick_html_colors()|n}</h3>
  </div>
</div>
<div class="row">
  <div class="span12">
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th></th>
          <th>Type</th>
          <th>Server</th>
          <th>Map</th>
          <th>Result</th>
          <th>Played</th>
          <th>Elo</th>
        </tr>
      </thead>
      <tbody>
      % for rg in games.items:
      <tr>
        <td class="tdcenter"><a class="btn btn-primary btn-small" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">view</a></td>
        <td class="tdcenter"><img title="${rg.game_type_cd}" src="/static/images/icons/24x24/${rg.game_type_cd}.png" alt="${rg.game_type_cd}" /></td>
        <td>${rg.server_name}</td>
        <td>${rg.map_name}</td>
        <td>
          % if rg.team != None:
          % if rg.team == rg.winner:
          Win
          % else:
          Loss
          % endif
          % else:
          % if rg.rank == 1:
          Win
          % else:
          Loss (#${rg.rank})
          % endif
          % endif
        </td>
        <td><span class="abstime" data-epoch="${rg.epoch}" title="${rg.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${rg.fuzzy_date}</span></td>
        <td class="tdcenter">
          <a href="${request.route_url('game_info', id=rg.game_id, _query={'show_elo':1})}" title="View detailed information about this game">
            % if rg.elo_delta is not None:
            % if round(rg.elo_delta,2) > 0:
            <span title="Elo went up by ${round(rg.elo_delta,2)}"><i class="glyphicon glyphicon-arrow-up"></i></span>
            % elif round(rg.elo_delta,2) < 0:
            <span title="Elo went down by ${round(-rg.elo_delta,2)}"><i class="glyphicon glyphicon-arrow-down"></i></span>
            % else:
            <span title="Elo did not change"><i class="glyphicon glyphicon-minus"></i></span>
            % endif
            % else:
            <span title="Elo did not change"><i class="glyphicon glyphicon-minus"></i></span>
            % endif
          </a>
        </td>
      </tr>
      % endfor
      </tbody>
    </table>
  </div>
</div>

<!-- navigation links -->
${navlinks("player_game_index", games.page, games.last_page, player_id=player_id)}
% endif
