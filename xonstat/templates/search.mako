<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
${nav.nav('games')}
</%block>

% if results == None:

<%block name="title">
Advanced Search
</%block>

<div class="row">
  <div class="span6 offset3">


    <form style="margin-top: 20px;" class="form-horizontal">
      <fieldset>

        <!-- Form submitted? -->
        <input type="hidden" name="fs" />

        <!-- Text input-->
        <div class="control-group">
          <label class="control-label">Nick</label>
          <div class="controls">
            <input id="nick" name="nick" type="text" placeholder="player nick" class="input-xlarge">
            <p class="help-block"></p>
          </div>
        </div>

        <!-- Text input-->
        <div class="control-group">
          <label class="control-label">Server</label>
          <div class="controls">
            <input id="server_name" name="server_name" type="text" placeholder="server name" class="input-xlarge">
            <p class="help-block"></p>
          </div>
        </div>

        <!-- Text input-->
        <div class="control-group">
          <label class="control-label">Map</label>
          <div class="controls">
            <input id="map_name" name="map_name" type="text" placeholder="map name" class="input-xlarge">
            <p class="help-block"></p>
          </div>
        </div>

        <!-- Multiple Checkboxes -->
        <div class="control-group">
          <label class="control-label">Game Types</label>
          <div class="controls">
            <label class="checkbox">
              <input type="checkbox" name="dm" value="Deathmatch">
              Deathmatch
            </label>
            <label class="checkbox">
              <input type="checkbox" name="duel" value="Duel">
              Duel
            </label>
            <label class="checkbox">
              <input type="checkbox" name="ctf" value="Capture The Flag">
              Capture The Flag
            </label>
            <label class="checkbox">
              <input type="checkbox" name="tdm" value="Team Deathmatch">
              Team Deathmatch
            </label>
          </div>
        </div>

        <!-- Button -->
        <div class="control-group">
          <label class="control-label"></label>
          <div class="controls">
            <button id="submit" name="submit" type="submit" class="btn btn-primary">Submit</button>
          </div>
        </div>

      </fieldset>
    </form>

  </div>
</div>


    % elif len(results) == 0:
<div class="row">
  <div class="span6 offset3">
    <h1 class="text-center">Sorry, nothing found!</h1>
  </div>
</div>
    % else:

<div class="row">
  <div class="span8 offset2">

##### player-only results #####
% if result_type == "player":
<table class="table table-hover table-condensed">
  <tr>
    <th>Player</th>
    <th>Joined</th>
  </tr>
  % for player in results:
  <tr>
    <td><a href="${request.route_url("player_info", id=player.player_id)}" name="Player info page for player #${player.player_id}">${player.nick_html_colors()|n}</a></td>
    <td><span class="abstime" data-epoch="${player.epoch()}" title="${player.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${player.joined_pretty_date()}</span></td>
  </tr>
  % endfor
</table>
% endif

##### server-only results #####
% if result_type == "server":
<table class="table table-hover table-condensed">
  <tr>
    <th>Server</th>
    <th>Created</th>
  </tr>
  % for server in results:
  <tr>
    <td><a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for server #${server.server_id}">${server.name}</a></td>
    <td><span class="abstime" data-epoch="${server.epoch()}" title="${server.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${server.fuzzy_date()}</span></td>
  </tr>
  % endfor
</table>
% endif

##### map-only results #####
% if result_type == "map":
<table class="table table-hover table-condensed">
  <tr>
    <th>Map</th>
    <th>Added</th>
  </tr>
  % for map in results:
  <tr>
    <td><a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for map #${map.map_id}">${map.name}</a></td>
    <td><span class="abstime" data-epoch="${map.epoch()}" title="${map.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${map.fuzzy_date()}</span></td>
  </tr>
  % endfor
</table>
% endif

##### game results #####
% if result_type == "game":
<table class="table table-hover table-condensed">
  <tr>
    <th></th>
    <th>Map</th>
    <th>Server</th>
    <th>Time</th>
  </tr>
  % for (game, server, gmap) in results:
  <tr>
    <td><a class="btn btn-primary btn-small" href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">View</a></td>
    <td><a href="${request.route_url("map_info", id=gmap.map_id)}" name="Map info page for map #${gmap.map_id}">${gmap.name}</a></td>
    <td><a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for server #${server.server_id}">${server.name}</a></td>
    <td><span class="abstime" data-epoch="${game.epoch()}" title="${game.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${game.fuzzy_date()}</span></td>
  </tr>
  % endfor
</table>
% endif

<!-- navigation links -->
${navlinks("search", results.page, results.last_page, search_query=query)}
</div>
</div>
% endif

<%block name="js">
${parent.js()}
</%block>


