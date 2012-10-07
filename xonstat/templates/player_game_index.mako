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
    <table class="table table-bordered table-condensed">
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
      % for g in games.items:
        <tr>
           <td class="tdcenter"><a class="btn btn-primary btn-small" href="${request.route_url('game_info', id=g.game_id)}" title="View detailed information about this game">view</a></td>
           <td class="tdcenter"><img title="${g.game_type_cd}" src="/static/images/icons/24x24/${g.game_type_cd}.png" alt="${g.game_type_cd}" /></td>
           <td>${g.server_name}</td>
           <td>${g.map_name}</td>
           <td>
           % if g.team != None:
             % if g.team == g.winner:
             Win
             % else:
             Loss
             % endif
          % else:
            % if g.rank == 1:
            Win
            % else:
            Loss (#${g.rank})
            % endif
          % endif
           </td>
           <td><span class="abstime" data-epoch="${g.game_epoch}" title="${g.game_create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${g.game_fuzzy}</span></td>
           <td class="tdcenter">
             % if round(g.elo_delta,2) > 0:
             <span title="Elo went up by ${round(g.elo_delta,2)}"><i class="icon-arrow-up icon-white"></i></span>
             % elif round(g.elo_delta,2) < 0:
             <span title="Elo went down by ${round(g.elo_delta,2)}"><i class="icon-arrow-down icon-white"></i></span>
             % else:
             <span title="Elo did not change"><i class="icon-minus icon-white"></i></span>
             % endif
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
