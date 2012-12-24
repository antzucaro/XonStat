<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="navigation">
${nav.nav('players')}
</%block>

<%block name="css">
    ${parent.css()}
    <link href="/static/css/sprites.css" rel="stylesheet">
</%block>

<%block name="js">
    % if player is not None:
      <script src="/static/js/jquery-1.7.1.min.js"></script>
      <script src="/static/js/jquery.flot.min.js"></script>
      <script src="/static/js/bootstrap-tab.js"></script>
      <script type="text/javascript">
      $(function () {
        $('#gbtab li').click(function(e) {
            e.preventDefault();
            $(this).tab('show');
        })

        $('#gbtab a:first').tab('show');
      })
      </script>

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
                    previousLabel = item.series.label;
                    previousPoint = item.dataIndex;

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
  <div id="gbtabcontainer" class="tabbable tabs-below">
      <div class="tab-content">
      % for g in games_played:
        <div class="tab-pane fade in 
        % if g.game_type_cd == 'overall':
          active
        % endif
        " id="tab-${g.game_type_cd}">
          <div class="span5">
            <p>
            % if g.game_type_cd in overall_stats:
            Last Played: <small><span class="abstime" data-epoch="${overall_stats[g.game_type_cd].last_played_epoch}" title="${overall_stats[g.game_type_cd].last_played.strftime('%a, %d %b %Y %H:%M:%S UTC')}"> ${overall_stats[g.game_type_cd].last_played_fuzzy} </span> <br /></small>
            % endif

            Games Played: <small>${g.games} <br /></small>

            Playing Time: <small>${overall_stats[g.game_type_cd].total_playing_time} <br /></small>

            % if g.game_type_cd in fav_maps:
            Favorite Map: <small>${fav_maps[g.game_type_cd].map_name} <br /></small>
            % endif
            </p>
          </div>
          <div class="span5">
            <p>
              Win Percentage: <small>${round(g.win_pct,2)}% (${g.wins} wins, ${g.losses} losses) <br /></small>

            % if g.game_type_cd in overall_stats:
              % if overall_stats[g.game_type_cd].k_d_ratio is not None:
              Kill Ratio: <small>${round(overall_stats[g.game_type_cd].k_d_ratio,2)} (${overall_stats[g.game_type_cd].total_kills} kills, ${overall_stats[g.game_type_cd].total_deaths} deaths) <br /></small>
              % endif
            % endif

            % if g.game_type_cd in elos:
              % if g.game_type_cd == 'overall':
              Best Elo: <small>${round(elos[g.game_type_cd].elo,2)} (${elos[g.game_type_cd].game_type_cd}, ${elos[g.game_type_cd].games} games) <br /></small>
              % else:
              Elo: <small>${round(elos[g.game_type_cd].elo,2)} (${elos[g.game_type_cd].games} games) <br /></small>
              % endif
            % endif

            % if g.game_type_cd in ranks:
              % if g.game_type_cd == 'overall':
              Best Rank: <small>${ranks[g.game_type_cd].rank} of ${ranks[g.game_type_cd].max_rank} (${ranks[g.game_type_cd].game_type_cd}, percentile: ${round(ranks[g.game_type_cd].percentile,2)})<br /></small>

              % else:
              Rank: <small>${ranks[g.game_type_cd].rank} of ${ranks[g.game_type_cd].max_rank} (percentile: ${round(ranks[g.game_type_cd].percentile,2)})<br /></small>
              % endif
            % endif

            % if g.game_type_cd == 'ctf':
              % if  overall_stats[g.game_type_cd].cap_ratio is not None:
                Cap Ratio: <small>${round(overall_stats[g.game_type_cd].cap_ratio,2)} (${overall_stats[g.game_type_cd].total_captures} captures, ${overall_stats[g.game_type_cd].total_pickups} pickups) <br /></small>
              % endif
            % endif
            </p>
          </div>
        </div>
      % endfor
      </div>
  </div>
</div>
<div class="row">
  <div class="span12">
      <ul id="gbtab" class="nav nav-tabs">
      % for g in games_played:
        <li>
          <a href="#tab-${g.game_type_cd}" data-toggle="tab">
            <span class="sprite sprite-${g.game_type_cd}"> </span><br />
            ${g.game_type_cd} <br />
            <small>(${g.games})</small>
          </a>
        </li>
      % endfor
      </ul>
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
            <span class="sprite sprite-nex"></span>
            <p><small>Nex</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query={'weapon':'nex'})}" title="Show nex accuracy"></a>
          </div>
        </li>
        % endif

        % if 'rifle' in recent_weapons:
        <li>
          <div class="acc-weap">
            <span class="sprite sprite-rifle"></span>
            <p><small>Rifle</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query={'weapon':'rifle'})}" title="Show rifle accuracy"></a>
          </div>
        </li>
        % endif

        % if 'minstanex' in recent_weapons:
        <li>
          <div class="acc-weap">
            <span class="sprite sprite-minstanex"></span>
            <p><small>Minstanex</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query={'weapon':'minstanex'})}" title="Show minstanex accuracy"></a>
          </div>
        </li>
        % endif

        % if 'uzi' in recent_weapons:
        <li>
          <div class="acc-weap">
            <span class="sprite sprite-uzi"></span>
            <p><small>Uzi</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query={'weapon':'uzi'})}" title="Show uzi accuracy"></a>
          </div>
        </li>
        % endif

        % if 'shotgun' in recent_weapons:
        <li>
          <div class="acc-weap">
            <span class="sprite sprite-shotgun"></span>
            <p><small>Shotgun</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query={'weapon':'shotgun'})}" title="Show shotgun accuracy"></a>
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
            <span class="sprite sprite-rocketlauncher"></span>
            <p><small>Rocket</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query={'weapon':'rocketlauncher'})}" title="Show rocket launcher efficiency"></a>
          </div>
        </li>
        % endif

        % if 'grenadelauncher' in recent_weapons:
        <li>
          <div class="dmg-weap">
            <span class="sprite sprite-grenadelauncher"></span>
            <p><small>Mortar</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query={'weapon':'grenadelauncher'})}" title="Show mortar damage efficiency"></a>
          </div>
        </li>
        % endif

        % if 'electro' in recent_weapons:
        <li>
          <div class="dmg-weap">
            <span class="sprite sprite-electro"></span>
            <p><small>Electro</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query={'weapon':'electro'})}" title="Show electro damage efficiency"></a>
          </div>
        </li>
        % endif

        % if 'crylink' in recent_weapons:
        <li>
          <div class="dmg-weap">
            <span class="sprite sprite-crylink"></span>
            <p><small>Crylink</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query={'weapon':'crylink'})}" title="Show crylink damage efficiency"></a>
          </div>
        </li>
        % endif

        % if 'hagar' in recent_weapons:
        <li>
          <div class="dmg-weap">
            <span class="sprite sprite-hagar"></span>
            <p><small>Hagar</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query={'weapon':'hagar'})}" title="Show hagar damage efficiency"></a>
          </div>
        </li>
        % endif

        % if 'laser' in recent_weapons:
        <li>
          <div class="dmg-weap">
            <span class="sprite sprite-laser"></span>
            <p><small>Laser</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query={'weapon':'laser'})}" title="Show laser damage efficiency"></a>
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
           <th>Elo</th>
        </tr>
      </thead>
      <tbody>
      % for rg in recent_games:
        <tr>
           <td class="tdcenter"><a class="btn btn-primary btn-small" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">view</a></td>
           <td class="tdcenter"><span class="sprite sprite-${rg.game_type_cd}" alt="${rg.game_type_cd}"></span></td>
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
                 <span title="Elo went up by ${round(rg.elo_delta,2)}"><i class="icon-arrow-up icon-white"></i></span>
                 % elif round(rg.elo_delta,2) < 0:
                 <span title="Elo went down by ${round(-rg.elo_delta,2)}"><i class="icon-arrow-down icon-white"></i></span>
                 % else:
                 <span title="Elo did not change"><i class="icon-minus icon-white"></i></span>
                 % endif
               % else:
                 <span title="Elo did not change"><i class="icon-minus icon-white"></i></span>
               % endif
             </a>
           </td>
        </tr>
      % endfor
      </tbody>
    </table>
    % if total_games > 10:
    <p><a href="${request.route_url("player_game_index", player_id=player.player_id, page=1)}" title="Game index for ${player.nick}">More...</a></p>
    % endif
  </div>
</div>
% endif
% endif
