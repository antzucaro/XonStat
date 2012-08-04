<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="navigation">
${nav.nav('players')}
</%block>

<%block name="js">
    % if player is not None:
      <script src="/static/js/jquery-1.7.1.min.js"></script>
      <script src="/static/js/jquery.flot.min.js"></script>
      <script type="text/javascript">
      $(function () {

          // plot the accuracy graph
          function plot_acc_graph(data) {
              var games = new Array();
              var avgs = new Array();
              var accs = new Array();

              var i=0;
              for(i=0; i < data.games; i++) {
                  avgs[i] = [i, data.avg];
                  accs[i] = [i, data.accs[i][1]];
                  game_link = '/game/' + data.accs[i][0];
                  j = data.games - i;
                  games[i] = [i, '<a href="' + game_link + '">' + j + '</a>'];
              }

              $.plot(
                  $("#acc-graph"), 
                  [ { label: 'average', data: avgs, hoverable: true, clickable: false }, 
                    { label: 'accuracy', data: accs, lines: {show:true}, points: {show:false}, hoverable: true, clickable: true }, ],
                  { yaxis: {ticks: 10, min: 0, max: 100 },
                    xaxis: {ticks: games},
                    grid: { hoverable: true, clickable: true },
              });
          }

          // plot the damage graph
          function plot_dmg_graph(data) {
              var games = new Array();
              var avgs = new Array();
              var dmgs = new Array();

              var i=0;
              for(i=0; i < data.games; i++) {
                  avgs[i] = [i, data.avg];
                  dmgs[i] = [i, data.dmgs[i][1]];
                  game_link = '/game/' + data.dmgs[i][0];
                  j = data.games - i;
                  games[i] = [i, '<a href="' + game_link + '">' + j + '</a>'];
              }

              $.plot(
                  $("#dmg-graph"), 
                  [ { label: 'average', data: avgs, hoverable: true, clickable: false }, 
                    { label: 'efficiency', data: dmgs, lines: {show:true}, points: {show:false}, hoverable: true, clickable: true }, ],
                  { yaxis: {ticks: 10, min: 0 },
                    xaxis: {ticks: games},
                    grid: { hoverable: true, clickable: true },
              });
          }

          function showTooltip(x, y, contents) {
            $('<div id="tooltip">' + contents + '</div>').css( {
                position: 'absolute',
                display: 'none',
                top: y - 35,
                left: x + 10,
                border: '1px solid #fdd',
                padding: '2px',
                'background-color': '#333333',
                opacity: 0.80
            }).appendTo("body").fadeIn(200);
          }

          var previousPoint = null;
          var previousLabel = null;
          $('#acc-graph').bind("plothover", function (event, pos, item) {
              if (item) {
                  if ((previousLabel != item.series.label) || (previousPoint != item.dataIndex)) {
                    previousPoint = item.dataIndex;
                    previousLabel = item.series.label;

                    $("#tooltip").remove();
                    var x = item.datapoint[0].toFixed(2),
                        y = item.datapoint[1].toFixed(2);

                    showTooltip(item.pageX, item.pageY, y + "%");
                  }
              }
              else {
                  $("#tooltip").remove();
                  previousPoint = null;
                  previousLabel = null;
              }
          });

          $('#dmg-graph').bind("plothover", function (event, pos, item) {
              if (item) {
                  if ((previousLabel != item.series.label) || (previousPoint != item.dataIndex)) {
                    previousPoint = item.dataIndex;
                    previousLabel = item.series.label;

                    $("#tooltip").remove();
                    var x = item.datapoint[0].toFixed(2),
                        y = item.datapoint[1].toFixed(2);

                    showTooltip(item.pageX, item.pageY, y);
                  }
              }
              else {
                  $("#tooltip").remove();
                  previousPoint = null;
                  previousLabel = null;
              }
          });

          // bind click events to the weapon images
          $(".acc-weap").click(function () {
              var dataurl = $(this).find('a').attr('href');

              $('.accuracy-nav').find('.weapon-active').removeClass('weapon-active');
              $(this).addClass('weapon-active');

              $.ajax({
                  url: dataurl,
                  method: 'GET',
                  dataType: 'json',
                  success: plot_acc_graph
              });
          });

          $(".dmg-weap").click(function () {
              var dataurl = $(this).find('a').attr('href');

              $('.damage-nav').find('.weapon-active').removeClass('weapon-active');
              $(this).addClass('weapon-active');

              $.ajax({
                  url: dataurl,
                  method: 'GET',
                  dataType: 'json',
                  success: plot_dmg_graph
              });
          });

          // populate the graphs with the default weapons
          $.ajax({
              url: '${request.route_url("player_accuracy", id=player.player_id)}',
              method: 'GET',
              dataType: 'json',
              success: plot_acc_graph
          });

          $.ajax({
              url: '${request.route_url("player_damage", id=player.player_id)}',
              method: 'GET',
              dataType: 'json',
              success: plot_dmg_graph
          });
      })
      </script>
    % endif
</%block>

<%block name="title">
Player Information
</%block>


% if player is None:
<h2>This player is so good we couldn't find him!</h2>
<p>Seriously though, he probably doesn't exist...just a figment of your imagination. Carry on then!</p>

% else:
<div class="row">
  <div class="span12">
    <h2>${player.nick_html_colors()|n}</h2>
  </div>
</div>

<div class="row">
  <div class="span6">
    <p>
      Member Since: <small>${player.create_dt.strftime('%m/%d/%Y at %I:%M %p')} </small><br />

      Last Seen: <small>${recent_games[0][1].fuzzy_date()} </small><br />

      Playing Time: <small>${total_stats['alivetime']} hours
      % if total_stats['alivetime'] > total_stats['alivetime_month']:
          % if total_stats['alivetime_month'] > total_stats['alivetime_week']:
              (${total_stats['alivetime_month']} hours this month; ${total_stats['alivetime_week']} hours this week)
          % else:
              (${total_stats['alivetime_month']} hours this month)
          % endif
      % endif
      </small><br />

      <% games_breakdown_str = ', '.join(["{0} {1}".format(ng, gt) for (gt, ng) in games_breakdown]) %>
      Games Played: <small>${total_games} (${games_breakdown_str})</small><br />

      % if fav_map is not None:
      Favorite Maps: <small>
      <% map_list = fav_map[:3] %>
      % for mapinfo in map_list:
          % if mapinfo != map_list[-1]:
              <% delim = ", " %>
          % else:
              <% delim = "" %>
          % endif
          <a href="${request.route_url('map_info', id=mapinfo['id'])}" title="view map info">${mapinfo['name']}</a>${delim}
      % endfor
      </small><br />
      % endif

      % if fav_weapon is not None:
      Favorite Weapons: <small>
      <% wpn_list = fav_weapon[:2] %>
      % for wpninfo in wpn_list:
          % if wpninfo != wpn_list[-1]:
              <% delim = ", " %>
          % else:
              <% delim = "" %>
          % endif
          ${wpninfo['name']}${delim}
      % endfor
      </small><br />
      % endif
    </p>
  </div>
  <div class="span6">
    <p>
       % if total_games > 0 and total_stats['wins'] is not None:
       Win Percentage: <small>${round(float(total_stats['wins'])/total_games * 100, 2)}% (${total_stats['wins']} wins, ${total_games - total_stats['wins']} losses) </small><br />
       % endif

       % if total_stats['kills'] > 0 and total_stats['deaths'] > 0:
       Kill Ratio: <small>${round(float(total_stats['kills'])/total_stats['deaths'], 3)} (${total_stats['kills']} kills, ${total_stats['deaths']} deaths, ${total_stats['suicides']} suicides) </small><br />
       % endif

       % if elos_display is not None and len(elos_display) > 0:
       Elo:
          <small>${', '.join(elos_display)} </small>
          <br />
          %if '*' in ', '.join(elos_display):
              <small><i>*preliminary Elo</i></small><br />
          %endif
      % endif

      % if ranks_display != '':
      Ranks: <small>${ranks_display}</small><br />
      % endif
    </p>
  </div>
</div>


% if 'nex' in recent_weapons or 'rifle' in recent_weapons or 'minstanex' in recent_weapons or 'uzi' in recent_weapons or 'shotgun' in recent_weapons:
<div class="row">
  <div class="span10">
    <h3>Accuracy</h3>
    <div id="acc-graph" class="flot" style="width:900px; height:200px;">
    </div>

    <div class="weapon-nav accuracy-nav">
      <ul>
        % if 'nex' in recent_weapons:
        <li>
          <div class="acc-weap weapon-active">
            <img src="${request.static_url("xonstat:static/images/nex.png")}" />
            <p><small>Nex</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query=[('weapon','nex')])}" title="Show nex accuracy"></a>
          </div>
        </li>
        % endif

        % if 'rifle' in recent_weapons:
        <li>
          <div class="acc-weap">
            <img src="${request.static_url("xonstat:static/images/rifle.png")}" />
            <p><small>Rifle</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query=[('weapon','rifle')])}" title="Show rifle accuracy"></a>
          </div>
        </li>
        % endif

        % if 'minstanex' in recent_weapons:
        <li>
          <div class="acc-weap">
            <img src="${request.static_url("xonstat:static/images/minstanex.png")}" />
            <p><small>Minstanex</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query=[('weapon','minstanex')])}" title="Show minstanex accuracy"></a>
          </div>
        </li>
        % endif

        % if 'uzi' in recent_weapons:
        <li>
          <div class="acc-weap">
            <img src="${request.static_url("xonstat:static/images/uzi.png")}" />
            <p><small>Uzi</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query=[('weapon','uzi')])}" title="Show uzi accuracy"></a>
          </div>
        </li>
        % endif

        % if 'shotgun' in recent_weapons:
        <li>
          <div class="acc-weap">
            <img src="${request.static_url("xonstat:static/images/shotgun.png")}" />
            <p><small>Shotgun</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query=[('weapon','shotgun')])}" title="Show shotgun accuracy"></a>
          </div>
        </li>
        % endif
      </ul>
    </div>

  </div>
</div>
% endif


% if 'rocketlauncher' in recent_weapons or 'grenadelauncher' in recent_weapons or 'electro' in recent_weapons or 'crylink' in recent_weapons or 'laser' in recent_weapons:
<div class="row">
  <div class="span10">
    <h3>Damage Efficiency</h3>
    <div id="dmg-graph" class="flot" style="width:900px; height:200px;">
    </div>

    <div class="weapon-nav damage-nav">
      <ul>
        % if 'rocketlauncher' in recent_weapons:
        <li>
          <div class="dmg-weap weapon-active">
            <img src="${request.static_url("xonstat:static/images/rocketlauncher.png")}" />
            <p><small>Rocket</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query=[('weapon','rocketlauncher')])}" title="Show rocket launcher efficiency"></a>
          </div>
        </li>
        % endif

        % if 'grenadelauncher' in recent_weapons:
        <li>
          <div class="dmg-weap">
            <img src="${request.static_url("xonstat:static/images/grenadelauncher.png")}" />
            <p><small>Mortar</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query=[('weapon','grenadelauncher')])}" title="Show mortar damage efficiency"></a>
          </div>
        </li>
        % endif

        % if 'electro' in recent_weapons:
        <li>
          <div class="dmg-weap">
            <img src="${request.static_url("xonstat:static/images/electro.png")}" />
            <p><small>Electro</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query=[('weapon','electro')])}" title="Show electro damage efficiency"></a>
          </div>
        </li>
        % endif

        % if 'crylink' in recent_weapons:
        <li>
          <div class="dmg-weap">
            <img src="${request.static_url("xonstat:static/images/crylink.png")}" />
            <p><small>Crylink</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query=[('weapon','crylink')])}" title="Show crylink damage efficiency"></a>
          </div>
        </li>
        % endif

        % if 'hagar' in recent_weapons:
        <li>
          <div class="dmg-weap">
            <img src="${request.static_url("xonstat:static/images/hagar.png")}" />
            <p><small>Hagar</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query=[('weapon','hagar')])}" title="Show hagar damage efficiency"></a>
          </div>
        </li>
        % endif

        % if 'laser' in recent_weapons:
        <li>
          <div class="dmg-weap">
            <img src="${request.static_url("xonstat:static/images/laser.png")}" />
            <p><small>Laser</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query=[('weapon','laser')])}" title="Show laser damage efficiency"></a>
          </div>
        </li>
        % endif

      </ul>
    </div>

  </div>
</div>
% endif


##### RECENT GAMES (v2) ####
% if recent_games:
<div class="row">
  <div class="span12">
    <h3>Recent Games</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
           <th></th>
           <th>Type</th>
           <th>Server</th>
           <th>Map</th>
           <th>Result</th>
           <th>Played</th>
        </tr>
      </thead>
      <tbody>
      % for (gamestat, game, server, map) in recent_games:
        <tr>
           <td><a class="btn btn-primary btn-small" href="${request.route_url('game_info', id=game.game_id)}" title="View detailed information about this game">view</a></td>
           <td style="width:20px;"><img title="${game.game_type_cd}" src="/static/images/icons/24x24/${game.game_type_cd}.png" alt="${game.game_type_cd}" /></td>
           <td>${server.name}</td>
           <td>${map.name}</td>
           <td>
           % if gamestat.team != None:
             % if gamestat.team == game.winner:
             Win
             % else:
             Loss
             % endif
          % else:
            % if gamestat.rank == 1:
            Win
            % else:
            Loss (#${gamestat.rank})
            % endif
          % endif
           </td>
           <td>${game.fuzzy_date()}</td>
        </tr>
      % endfor
      </tbody>
    </table>
    % if total_games > 10:
    <a href="${request.route_url("player_game_index", player_id=player.player_id, page=1)}" title="Game index for ${player.nick}">More games played by ${player.nick_html_colors()|n}...</a>
    % endif
  </div>
</div>
% endif
% endif
