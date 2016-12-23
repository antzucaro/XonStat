<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
    ##### Disable the login button until a replacement is implemented.
    ${nav.nav('players', False)}
</%block>

<%block name="css">
  ${parent.css()}
  <link href="/static/css/nv.d3.min.css" rel="stylesheet">
  <style>
    #damageChart, #accuracyChart {
      height: 300px;
    }
  </style>
</%block>

<%block name="js">
  ${parent.js()}
  <script type="text/javascript" src="/static/js/vendor/d3.min.js"></script>
  <script type="text/javascript" src="/static/js/vendor/nv.d3.min.js"></script>
  <script type="text/javascript" src="/static/js/weaponCharts.min.js"></script>
  ##### <script src="/static/js/weaponCharts.min.js"></script>
  <script type="text/javascript">

    // game type buttons
    % for g in games_played:
    $('#tab-${g.game_type_cd}').click(function() {
      $.getJSON("${request.route_url('player_weaponstats_data_json', id=player.player_id, _query={'limit':20, 'game_type':g.game_type_cd})}", function(data) {
        drawDamageChart("#damageChart", data);
        drawAccuracyChart("#accuracyChart", data);
      });
    });
    % endfor

    // weapon accuracy and damage charts
    $.getJSON("${request.route_url('player_weaponstats_data_json', id=player.player_id, _query={'limit':20})}", function(data) {
    
      if(data.games.length < 5) {
        d3.select(".row #damageChart").remove();
        d3.select(".row #accuracyChart").remove();
      }
      drawDamageChart("#damageChart", data);
      drawAccuracyChart("#accuracyChart", data);
    });
  </script>
</%block>

<%block name="title">
  Player Information
</%block>

<div class="row">
  <div class="small-12 columns">
    <h2> 
      ${player.nick_html_colors()|n} 
      % for medal in medals:
        <img src="/static/medals/${medal.image}" alt="${medal.alt}" title="${medal.alt}" />
      % endfor
    </h2>

    <h5>
      <i><span class="abstime" data-epoch="${player.epoch()}" title="${player.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">Joined ${player.fuzzy_date()}</span> (player #${player.player_id})</i>
      % if cake_day:
        <img src="/static/images/icons/24x24/cake.png" title="Happy cake day!" />
      % endif
    </h5>
  </div>
</div>

##### TABS #####
<div class="row">
  <div class="small-12 columns">
    <ul class="tabs text-center" data-tab>
      % for g in games_played:
        <li class="tab-title
          % if g.game_type_cd == 'overall':
            active
          % endif
        ">
          <a id="tab-${g.game_type_cd}" href="#tab-${g.game_type_cd}" title="${overall_stats[g.game_type_cd].game_type_descr}">
            <span class="sprite sprite-${g.game_type_cd}"></span><br />
            ${g.game_type_cd} <br />
            <small>(${g.games})</small>
          </a>
        </li>
      % endfor
    </ul>
  </div>
</div>

<div class="tabs-content">
  % for g in games_played:
    <div class="content
      % if g.game_type_cd == 'overall':
        active
      % endif
    " id="tab-${g.game_type_cd}">

        ##### LEFT PANE #####
        <div class="small-12 medium-6 columns">
          <p>
            % if g.game_type_cd in overall_stats:
              Last Played: <small><span class="abstime" data-epoch="${overall_stats[g.game_type_cd].last_played_epoch}" title="${overall_stats[g.game_type_cd].last_played.strftime('%a, %d %b %Y %H:%M:%S UTC')}"> ${overall_stats[g.game_type_cd].last_played_fuzzy} </span> <br /></small>
            % else:
            <small><br /></small>
            % endif

            Games Played: 
            % if g.game_type_cd == 'overall':
              <small><a href="${request.route_url("player_game_index", player_id=player.player_id)}" title="View recent games">
            % else:
              <small><a href="${request.route_url("player_game_index", player_id=player.player_id, _query={'type':g.game_type_cd})}" title="View recent ${overall_stats[g.game_type_cd].game_type_descr} games">
            % endif
            ${g.games}</a> <br /></small>

            Playing Time: <small>${overall_stats[g.game_type_cd].total_playing_time} <br /></small>

            % if g.game_type_cd in fav_maps:
              Favorite Map: <small><a href="${request.route_url("map_info", id=fav_maps[g.game_type_cd].map_id)}" title="Go to the detail page for this map">${fav_maps[g.game_type_cd].map_name}</a> <br /></small>
            % else:
              <small><br /></small>
            % endif

            % if g.game_type_cd == 'ctf':
              % if overall_stats[g.game_type_cd].total_captures is not None:
                <small><a href="${request.route_url("player_captimes", player_id=player.player_id)}">Fastest flag captures...</a> <br /></small>
              % else:
                <small><br /></small>
              % endif
            % else:
              <small><br /></small>
            % endif
          </p>
        </div>

        ##### RIGHT PANE #####
        <div class="small-12 medium-6 columns">
          <p>
            Win Percentage: <small>${round(g.win_pct,2)}% (${g.wins} wins, ${g.losses} losses) <br /></small>

            % if g.game_type_cd in overall_stats:
              % if overall_stats[g.game_type_cd].k_d_ratio is not None:
                Kill Ratio: <small>${round(overall_stats[g.game_type_cd].k_d_ratio,2)} (${overall_stats[g.game_type_cd].total_kills} kills, ${overall_stats[g.game_type_cd].total_deaths} deaths) <br /></small>
              % endif
            % else:
              <small><br /></small>
            % endif

            % if g.game_type_cd in elos:
              % if g.game_type_cd == 'overall':
                Best Elo: <small>${round(elos[g.game_type_cd].elo,2)} (${elos[g.game_type_cd].game_type_cd}, ${elos[g.game_type_cd].games} games) <br /></small>
              % else:
                Elo: <small>${round(elos[g.game_type_cd].elo,2)} (${elos[g.game_type_cd].games} games) <br /></small>
              % endif
            % else:
              <small><br /></small>
            % endif

            % if g.game_type_cd in ranks:
              % if g.game_type_cd == 'overall':
                Best Rank: 
                <small>
                  <a href="${request.route_url('rank_index', game_type_cd=ranks[g.game_type_cd].game_type_cd, _query={'page':(ranks[g.game_type_cd].rank-1)/20+1})}" title="Player rank page for this player">
                    ${ranks[g.game_type_cd].rank} of ${ranks[g.game_type_cd].max_rank}
                  </a>
                  (${ranks[g.game_type_cd].game_type_cd}, percentile: ${round(ranks[g.game_type_cd].percentile,2)}) 
                  <br />
                </small>
              % else:
                Rank: 
                <small>
                  <a href="${request.route_url('rank_index', game_type_cd=g.game_type_cd, _query={'page':(ranks[g.game_type_cd].rank-1)/20+1})}" title="Player rank page for this player">
                    ${ranks[g.game_type_cd].rank} of ${ranks[g.game_type_cd].max_rank}
                  </a>
                  (percentile: ${round(ranks[g.game_type_cd].percentile,2)})
                  <br />
                </small>
              % endif
            % else:
              <small><br /></small>
            % endif

            % if g.game_type_cd == 'ctf':
              % if overall_stats[g.game_type_cd].cap_ratio is not None:
                Cap Ratio: <small>${round(overall_stats[g.game_type_cd].cap_ratio,2)} (${overall_stats[g.game_type_cd].total_captures} captures, ${overall_stats[g.game_type_cd].total_pickups} pickups) <br /></small>
              % else:
                <small><br /></small>
              % endif
            % else:
              <small><br /></small>
            % endif
          </p>
        </div>
    </div>
  % endfor
</div>

##### ACCURACY CHART ####
<div class="row" id="accuracyChartRow">
  <div class="small-12 columns">
    <h5>Weapon Accuracy</h5>
    <noscript>
      Sorry, but you've disabled JavaScript! It is required to draw the accuracy chart.
    </noscript>
    <div id="accuracyChart">
      <svg id="accuracyChartSVG"></svg>
    </div>
  </div>
</div>

##### DAMAGE CHART ####
<div class="row" id="damageChartRow">
  <div class="small-12 columns">
    <h5>Weapon Damage</h5>
    <noscript>
      Sorry, but you've disabled JavaScript! It is required to draw the damage chart.
    </noscript>
    <div id="damageChart">
      <svg id="damageChartSVG"></svg>
    </div>
  </div> 
</div>

##### RECENT GAMES (v2) ####
% if recent_games:
  <div class="row">
    <div class="small-12 columns">
      <h5>Recent Games <a href="${request.route_url("player_game_index", player_id=player.player_id, page=1)}" title="Game index for ${player.stripped_nick}"><i class="fa fa-plus-circle"></i></a></h5>
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
        % for rg in recent_games:
          <tr>
            <td class="text-center"><a class="tiny button" href="${request.route_url('game_info', id=rg.game_id)}" title="View detailed information about this game">view</a></td>
            <td class="text-center"><span class="sprite sprite-${rg.game_type_cd}" alt="${rg.game_type_cd}" title="${rg.game_type_descr}"></span></td>
            <td class="show-for-medium-up no-stretch"><a href="${request.route_url('server_info', id=rg.server_id)}" title="Go to the detail page for this server">${rg.server_name}</a></td>
            <td class="no-stretch"><a href="${request.route_url('map_info', id=rg.map_id)}" title="Go to the detail page for this map">${rg.map_name}</a></td>
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
% endif
