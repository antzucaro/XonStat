<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="css">
  ${parent.css()}
  <link href="/static/css/luma.css" rel="stylesheet">
</%block>

<%block name="navigation">
  ${nav.nav('games')}
</%block>

<%block name="title">
  Recent Games
</%block>

% if not games:
  <h2>Sorry, no 
    % if game_type_descr:
      ${game_type_descr.lower()}
    % endif
    games yet for 
    <a href="${request.route_url('player_info', id=player.player_id)}">${player.nick_html_colors()|n}</a>. Get playing!
  </h2>

  <p><a href="${player_url}">Back to player info page</a></p>

% else:
  <div class="row">
    <div class="small-12 columns">
      <h5>Recent 
        % if game_type_descr:
        ${game_type_descr}
        % endif
        Games by 
        <a href="${request.route_url('player_info', id=player.player_id)}">
          ${player.nick_html_colors()|n}
        </a>
      </h5>
    </div>
  </div>

  <div class="row">
    <div class="small-12 columns">
      <ul class="tabs">
        % for game in games_played:
          % if not game.game_type_cd in ['cq']:
            <li class="text-center tab-title
              % if game.game_type_cd == game_type_cd or (game.game_type_cd == 'overall' and game_type_cd is None):
                active
              % endif
              "
            >
              % if game.game_type_cd == 'overall':
                <a href="${request.route_url("player_game_index", player_id=player.player_id)}" alt="${game.game_type_cd}" title="" data-toggle="none">
              % else:
                <a href="${request.route_url("player_game_index", player_id=player.player_id, _query={'type':game.game_type_cd})}" alt="${game.game_type_cd}" title="" data-toggle="none">
              % endif
              <span class="sprite sprite-${game.game_type_cd}"> </span><br />
              ${game.game_type_cd} <br />
              </a>
            </li>
          % endif
        % endfor
      </ul>
      <br />
    </div>
  </div>

  <div class="row">
    <div class="small-12 columns">
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-1 text-center"></th>
            <th class="small-1">Type</th>
            <th class="show-for-medium-up small-3">Server</th>
            <th class="small-2">Map</th>
            <th class="show-for-medium-up small-1">Result</th>
            <th class="show-for-medium-up small-2">Played</th>
            <th class="small-1">Elo</th>
          </tr>
        </thead>
        <tbody>
        % for rg in games.items:
        <tr>
          <td class="text-center"><a class="button tiny" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">view</a></td>
          <td class="text-center"><img title="${rg.game_type_cd}" src="/static/images/icons/24x24/${rg.game_type_cd}.png" alt="${rg.game_type_cd}" /></td>
          <td class="show-for-medium-up no-stretch"><a href="${request.route_url("server_info", id=rg.server_id)}" name="Server info page for ${rg.server_name}">${rg.server_name}</a></td>
          <td class="no-stretch"><a href="${request.route_url("map_info", id=rg.map_id)}" name="Map info page for ${rg.map_name}">${rg.map_name}</a></td>
          <td class="show-for-medium-up">
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
          <td class="show-for-medium-up"><span class="abstime" data-epoch="${rg.epoch}" title="${rg.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${rg.fuzzy_date}</span></td>
          <td class="text-center">
            <a href="${request.route_url('game_info', id=rg.game_id, _query={'show_elo':1})}" title="View detailed information about this game">
              % if rg.elo_delta is not None:
                % if round(rg.elo_delta,2) > 0:
                  <span class="eloup">+${round(rg.elo_delta,2)}</span>
                % elif round(rg.elo_delta,2) < 0:
                  <span class="elodown">${round(rg.elo_delta,2)}</span>
                % else:
                  <span class="eloneutral"><i class="fa fa-minus"></i></span>
                % endif
              % else:
                <span class="eloneutral"><i class="fa fa-minus"></i></span>
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
  ${navlinks("player_game_index", games.page, games.last_page, player_id=player_id, search_query=request.GET)}
% endif
