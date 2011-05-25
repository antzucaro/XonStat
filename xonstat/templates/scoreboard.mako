<%def name="scoreboard(game_type_cd, pgstats)">
<table border="1" cellpadding="3">

##### CTF #####
% if game_type_cd == 'ctf':
    <tr class="scoreboard-header">
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

% for pgstat in pgstats:
    <tr>
        <td>
        % if pgstat.player_id > 2:
          <a href="${request.route_url("player_info", id=pgstat.player_id)}"
           title="Go to the info page for this player">
          <span class="nick">${pgstat.nick_html_colors()}</span>
          </a>
        % else:
          <span class="nick">${pgstat.nick_html_colors()}</span>
        % endif
        </td>
        <td style="background-color:${pgstat.team_html_color()};"></td>
        <td>${pgstat.kills}</td>
        <td>${pgstat.captures}</td>
        <td>${pgstat.pickups}</td>
        <td>${pgstat.carrier_frags}</td>
        <td>${pgstat.returns}</td>
        <td><span style="color:#FFFF00;">${pgstat.score}</span></td>
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

##### DM #####
% if game_type_cd == 'dm':
    <tr class="scoreboard-header">
        <td>Nick</td>
        <td>Kills</td>
        <td>Deaths</td>
        <td>Suicides</td>
        <td>Score</td>
        <td>Accuracy</td>
    </tr>

% for pgstat in pgstats:
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
        <td><span style="color:#FFFF00;">${pgstat.score}</span></td>
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

</table>
</%def>
