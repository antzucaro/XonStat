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

          function plot_acc_graph(data) {
              var games = new Array();
              var avgs = new Array();
              var accs = new Array();

              var i=0;
              for(i=0; i < data.games; i++) {
                  avgs[i] = [i, data.avg];
                  accs[i] = [i, data.accs[i][1]];
                  games[i] = [i, data.accs[i][0]];
              }

              $.plot(
                  $("#acc-graph"), 
                  [ { data: avgs }, { data: accs }, ],
                  { yaxis: {ticks: 10, min: 0, max: 100 },
              });
          }

          $.ajax({
              url: '${request.route_url("player_accuracy", id=player.player_id)}',
              method: 'GET',
              dataType: 'json',
              success: plot_acc_graph
          });

          $(".acc-weap").click(function () {
              var dataurl = $(this).find('a').attr('href');

              $('.weapon-active').removeClass('weapon-active');
              $(this).addClass('weapon-active');

              $.ajax({
                  url: dataurl,
                  method: 'GET',
                  dataType: 'json',
                  success: plot_acc_graph
              });
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
  <div class="span8">
    <h2>${player.nick_html_colors()|n}</h2>
    <p>
       Member Since: <small>${player.create_dt.strftime('%m/%d/%Y at %I:%M %p')} </small><br />
       Last Seen: <small>${recent_games[0][1].fuzzy_date()} </small><br />
       Playing Time: <small>${total_stats['alivetime']} </small><br />
       % if total_games > 0 and total_stats['wins'] is not None:
       Win Percentage: <small>${round(float(total_stats['wins'])/total_games * 100, 2)}% (${total_stats['wins']} wins, ${total_games - total_stats['wins']} losses) </small><br />
       % endif
       % if total_stats['kills'] > 0 and total_stats['deaths'] > 0:
       Kill Ratio: <small>${round(float(total_stats['kills'])/total_stats['deaths'], 3)} (${total_stats['kills']} kills, ${total_stats['deaths']} deaths) </small><br />
       % endif
       <% games_breakdown_str = ', '.join(["{0} {1}".format(ng, gt) for (gt, ng) in games_breakdown]) %>
       Games Played: <small>${total_games} (${games_breakdown_str})</small><br />
       % if elos_display is not None and len(elos_display) > 0:
       Elo:
          <small>${', '.join(elos_display)} </small>
          <br />
          %if '*' in ', '.join(elos_display):
              <small><i>*preliminary Elo</i></small>
          %endif
      % endif
    </p>
  </div>
</div>


% if accs is not None:
<div class="row">
  <div class="span10">
    <h3>Accuracy</h3>
    <div id="acc-graph" style="width:800px; height:200px;">
    </div>

    <div class="weapon-nav">
      <ul>
        % if 'nex' in recent_weapons:
        <li>
          <div class="acc-weap weapon-active">
            <img src="${request.static_url("xonstat:static/images/nex.png")}" />
            <p><small>Nex</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query={'weapon':'nex'})}" title="Show nex accuracy"></a>
          </div>
        </li>
        % endif

        % if 'rifle' in recent_weapons:
        <li>
          <div class="acc-weap">
            <img src="${request.static_url("xonstat:static/images/rifle.png")}" />
            <p><small>Rifle</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query={'weapon':'rifle'})}" title="Show rifle accuracy"></a>
          </div>
        </li>
        % endif

        % if 'minstanex' in recent_weapons:
        <li>
          <div class="acc-weap">
            <img src="${request.static_url("xonstat:static/images/minstanex.png")}" />
            <p><small>Minstanex</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query={'weapon':'minstanex'})}" title="Show minstanex accuracy"></a>
          </div>
        </li>
        % endif

        % if 'uzi' in recent_weapons:
        <li>
          <div class="acc-weap">
            <img src="${request.static_url("xonstat:static/images/uzi.png")}" />
            <p><small>Uzi</small></p>
            <a href="${request.route_url('player_accuracy', id=player.player_id, _query={'weapon':'uzi'})}" title="Show uzi accuracy"></a>
          </div>
        </li>
        % endif

        % if 'shotgun' in recent_weapons:
        <li>
          <div class="acc-weap">
            <img src="${request.static_url("xonstat:static/images/shotgun.png")}" />
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
