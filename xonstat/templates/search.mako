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
    <div class="small-12 large-6 large-offset-3 columns">

      <form class="form-horizontal">
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
    <div class="small-12 large-6 large-offset-3 columns">
      <h1 class="text-center">Sorry, nothing found!</h1>
    </div>
  </div>

% else:

  ##### player-only results #####
  % if result_type == "player":
    <div class="row">
      <div class="small-12 large-8 large-offset-2 columns">
        <table class="table-hover table-condensed">
          <tr>
            <th class="small-2">ID</th>
            <th class="small-6">Nick</th>
            <th class="small-3">Joined</th>
            <th class="small-1"></th>
          </tr>
          % for player in results:
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
  % endif

  ##### server-only results #####
  % if result_type == "server":
    <div class="row">
      <div class="small-12 large-8 large-offset-2 columns">
        <table class="table-hover table-condensed">
          <tr>
            <th class="small-2">ID</th>
            <th class="small-6">Name</th>
            <th class="small-3">Added</th>
            <th class="small-1"></th>
          </tr>
          % for server in results:
            <tr>
              <td>${server.server_id}</td>
              <td><a href="${request.route_url("server_info", id=server.server_id)}" title="Go to this server's info page">${server.name}</a></th>
              <td><span class="abstime" data-epoch="${server.epoch()}" title="${server.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${server.fuzzy_date()}</span></td>
              <td class="text-center">
                <a href="${request.route_url("game_index", _query={'server_id':server.server_id})}" title="View recent games on this server">
                  <i class="fa fa-list"></i>
                </a>
              </td>
            </tr>
          % endfor
        </table>
  % endif

  ##### map-only results #####
  % if result_type == "map":
    <div class="row">
      <div class="small-12 large-8 large-offset-2 columns">
        <table class="table-hover table-condensed">
          <tr>
            <th class="small-2">ID</th>
            <th class="small-6">Name</th>
            <th class="small-3">Added</th>
            <th class="small-1"></th>
          </tr>
          % for map in results:
            <tr>
              <td>${map.map_id}</td>
              <td><a href="${request.route_url("map_info", id=map.map_id)}" title="Go to this map's info page">${map.name}</a></th>
              <td><span class="abstime" data-epoch="${map.epoch()}" title="${map.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${map.fuzzy_date()}</span></td>
               <td class="text-center">
                <a href="${request.route_url("game_index", _query={'map_id':map.map_id})}" title="View recent games on this map">
                  <i class="fa fa-list"></i>
                </a>
              </td>
            </tr>
          % endfor
        </table>
  % endif

  ##### game results #####
  % if result_type == "game":
  <div class="row">
    <div class="small-12 large-8 large-offset-2 columns">
      <table class="table-hover table-condensed">
        <tr>
          <th class="small-3"></th>
          <th class="small-3 medium-6">Map</th>
          <th class="small-3 medium-3">Server</th>
          <th class="small-3">Time</th>
        </tr>
        % for (game, server, gmap) in results:
          <tr>
            <td class="text-center"><a class="tiny button" href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">View</a></td>
            <td class="no-stretch"><a href="${request.route_url("map_info", id=gmap.map_id)}" name="Map info page for map #${gmap.map_id}">${gmap.name}</a></td>
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
