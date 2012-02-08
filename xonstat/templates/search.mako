<%inherit file="base.mako"/>
<%namespace file="navlinks.mako" import="navlinks" />

% if results == None:
<h2>Advanced Search</h2>
<form action="${request.route_url("search")}" method="get">
    <input type="hidden" name="fs" />
    <table style="border: none;" id="search_form" border="0">
        <tr>
            <td style="text-align:right; border: none;">Nick:</td>
            <td style="border: none;"><input type="text" name="nick" /></td>
        </tr>
        <tr style="border: none;">
            <td style="text-align:right; border: none;">Server:</td>
            <td style="border: none;"><input type="text" name="server_name" /></td>
        </tr>
        <tr style="border: none;">
            <td style="text-align:right; border: none;">Map:</td>
            <td style="border: none;"><input type="text" name="map_name" /></td>
        </tr>
        <tr style="border: none;">
            <td style="text-align:right; border: none;">Game Type:</td>
            <td style="border: none;">
                <input type="checkbox" name="dm" />Deathmatch<br/>
                <input type="checkbox" name="duel" />Duel<br/>
                <input type="checkbox" name="ctf" />Capture The Flag<br/>
                <input type="checkbox" name="tdm" />Team Deathmatch<br/>
            </td>
        </tr>
        <tr style="border: none;">
            <td style="text-align:right; border: none;"></td>
            <td style="border: none;"><input type="submit" value="search" /></td>
        </tr>
    </table>
    </form>
% elif len(results) == 0:
    <h1>Sorry, nothing found!</h1>
% else:

##### player-only results #####
% if result_type == "player":
<table>
    <tr>
        <th>Player</th>
        <th>Joined</th>
    </tr>
    % for player in results:
    <tr>
        <td><a href="${request.route_url("player_info", id=player.player_id)}" name="Player info page for player #${player.player_id}">${player.nick_html_colors()|n}</a></td>
        <td>${player.joined_pretty_date()}</td>
    </tr>
    % endfor
</table>
% endif

##### server-only results #####
% if result_type == "server":
<table>
    <tr>
        <th>Server</th>
        <th>Created</th>
    </tr>
    % for server in results:
    <tr>
        <td><a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for server #${server.server_id}">${server.name}</a></td>
        <td>${server.create_dt.strftime('%m/%d/%Y at %I:%M %p')}</td>
    </tr>
    % endfor
</table>
% endif

##### map-only results #####
% if result_type == "map":
<table>
    <tr>
        <th>Map</th>
        <th>Added</th>
    </tr>
    % for map in results:
    <tr>
        <td><a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for map #${map.map_id}">${map.name}</a></td>
        <td>${map.create_dt.strftime('%m/%d/%Y at %I:%M %p')}</td>
    </tr>
    % endfor
</table>
% endif

##### game results #####
% if result_type == "game":
<table>
    <tr>
        <th>Game ID</th>
        <th>Map</th>
        <th>Server</th>
        <th>Played On</th>
    </tr>
    % for (game, server, gmap) in results:
    <tr>
        <td><a href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">${game.game_id}</a></td>
        <td><a href="${request.route_url("map_info", id=gmap.map_id)}" name="Map info page for map #${gmap.map_id}">${gmap.name}</a></td>
        <td><a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for server #${server.server_id}">${server.name}</a></td>
        <td>${game.create_dt.strftime('%m/%d/%Y at %I:%M %p')}</td>
    </tr>
    % endfor
</table>
% endif

<!-- navigation links -->
${navlinks("search_paged", results.page, results.last_page, _query=query)}
% endif

<%block name="js">
${parent.js()}
</%block>


