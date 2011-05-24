<%inherit file="base.mako"/>

<%block name="title">
Game Index - ${parent.title()}
</%block>

% if not games:
<h2>Sorry, no games yet. Get playing!</h2>

% else:
<h2>Recent Games</h2>
% for (game, server, map) in games:
<p>
   <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a> on <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a> (<a href="${request.route_url('game_info', id=game.game_id)}" name="Permalink for game #${game.game_id}">permalink</a> for this game)
<table border="1" cellpadding="3">

############################ CTF Game ############################
% if game.game_type_cd == 'ctf':
    <tr>
        <td>Nick</td>
        <td>Team</td>
        <td>Kills</td>
        <td>Captures</td>
        <td>Pickups</td>
        <td>Flag Carrier Kills</td>
        <td>Returns</td>
        <td>Score</td>
        <td>Accuracy</td>
    </tr>

% for pgstat in pgstats[game.game_id]:
    <tr>
        <td>
        % if pgstat.player_id > 2:
          <a href="${request.route_url("player_info", id=pgstat.player_id)}"
           title="Go to the info page for this player">
          ${pgstat.nick_html_colors()}
          </a>
        % else:
          ${pgstat.nick_html_colors()}
        % endif
        </td>
        <td style="background-color:${pgstat.team_html_color()};"></td>
        <td>${pgstat.kills}</td>
        <td>${pgstat.captures}</td>
        <td>${pgstat.pickups}</td>
        <td>${pgstat.carrier_frags}</td>
        <td>${pgstat.returns}</td>
        <td>${pgstat.score}</td>
        <td>
        % if pgstat.player_id > 1:
          <a href="${request.route_url("player_weapon_stats", game_id=pgstat.game_id, pgstat_id=pgstat.player_game_stat_id)}"
           title="View weapon accuracy details for this player in this game">
          View
          </a>
        % endif
        </td>
    </tr>
% endfor
% endif


############################ DM Game ############################
% if game.game_type_cd == 'dm':
    <tr>
        <td>Nick</td>
        <td>Kills</td>
        <td>Deaths</td>
        <td>Suicides</td>
        <td>Score</td>
        <td>Accuracy</td>
    </tr>

% for pgstat in pgstats[game.game_id]:
    <tr>
        <td>
        % if pgstat.player_id > 2:
          <a href="${request.route_url("player_info", id=pgstat.player_id)}"
           title="Go to the info page for this player">
          ${pgstat.nick_html_colors()}
          </a>
        % else:
          ${pgstat.nick_html_colors()}
        % endif
        </td>
        <td>${pgstat.kills}</td>
        <td>${pgstat.deaths}</td>
        <td>${pgstat.suicides}</td>
        <td>${pgstat.score}</td>
        <td>
        % if pgstat.player_id > 1:
          <a href="${request.route_url("player_weapon_stats", game_id=pgstat.game_id, pgstat_id=pgstat.player_game_stat_id)}"
           title="View weapon accuracy details for this player in this game">
          View
          </a>
        % endif
        </td>
    </tr>
% endfor
% endif


############################ TDM Game ############################
% if game.game_type_cd == 'tdm':
    <tr>
        <td>Nick</td>
        <td>Team</td>
        <td>Kills</td>
        <td>Deaths</td>
        <td>Suicides</td>
        <td>Score</td>
        <td>Accuracy</td>
    </tr>

% for pgstat in pgstats[game.game_id]:
    <tr>
        <td>
        % if pgstat.player_id > 2:
          <a href="${request.route_url("player_info", id=pgstat.player_id)}"
           title="Go to the info page for this player">
          ${pgstat.nick_html_colors()}
          </a>
        % else:
          ${pgstat.nick_html_colors()}
        % endif
        </td>
        <td style="background-color:${pgstat.team_html_color()};"></td>
        <td>${pgstat.kills}</td>
        <td>${pgstat.deaths}</td>
        <td>${pgstat.suicides}</td>
        <td>${pgstat.score}</td>
        <td>
        % if pgstat.player_id > 1:
          <a href="${request.route_url("player_weapon_stats", game_id=pgstat.game_id, pgstat_id=pgstat.player_game_stat_id)}"
           title="View weapon accuracy details for this player in this game">
          View
          </a>
        % endif
        </td>
    </tr>
% endfor
% endif

############################ End gametype specific stuff ############################
</table>
% endfor
% endif

% if games.previous_page:
<a href="${request.route_url("game_index_paged", page=games.previous_page)}" name="Previous Page">Previous</a>
% endif
% if games.next_page:
<a href="${request.route_url("game_index_paged", page=games.next_page)}" name="Next Page">Next</a>
% endif
