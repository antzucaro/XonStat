<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="scoreboard.mako" import="scoreboard" />
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="navigation">
  ${nav.nav('games')}
</%block>

<%block name="css">
  ${parent.css()}
  <link href="/static/css/luma.css" rel="stylesheet">
</%block>

<%block name="foundation">
  <script>
  $(document).foundation({
      accordion: {
        multi_expand: true,
      }
    });
  </script>
</%block>

<%block name="title">
  Game Information
</%block>


% if game is None:
  <h2>Sorry, that game wasn't found!</h2>

% else:
  <div class="row">

    <div class="small-12 columns">
      <h3>Game #${game.game_id}</h3>
      <p>
        <span class="sprite sprite-${game.game_type_cd}"></span> ${gametype.descr} <br />
        Played ${game.fuzzy_date()} <span class="abstime" data-epoch="${game.epoch()}" title="${game.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}"> <i class="fa fa-info-circle"></i></span><br />
        Server: <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a><br />
        Map: <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a><br />
        % if game.duration is not None:
          Duration: ${"%s:%02d" % (game.duration.seconds/60, game.duration.seconds%60)}
        % endif
      </p>
    </div>

    % if teamscores:
      <div class="small-3 columns">
        <table class="table-condensed">
          <thead>
            <th>Team</th>
            <th>Score</th>
          </thead>
          <tbody>
            % for ts in teamscores:
              <tr class="${ts.team}"><td>${ts.team.capitalize()}</td><td>${ts.score}</td></tr>
            % endfor
          </tbody>
        </table>
      </div>
    % endif
  </div>

  ##### Games that have team scores push the scoreboard table to the right by
  ##### one column. 
  % if len(tgstats) == len(stats_by_team):
    % for tgstat in tgstats:
      <div class="row">

        <div class="small-1 columns teamscore">
          <div class="teamname ${tgstat.team_html_color()}">
            ${tgstat.team_html_color().capitalize()}
          </div>
          <div class="${tgstat.team_html_color()}">
            % if game.game_type_cd == 'ctf':
              ${tgstat.caps}
            % elif game.game_type_cd == 'ca':
              ${tgstat.rounds}
            % else:
              ${tgstat.score}
            % endif
          </div>
        </div>

        <div class="small-12 medium-11 columns game">
          ${scoreboard(game.game_type_cd, stats_by_team[tgstat.team], show_elo, show_latency)}
        </div>
      </div>
    % endfor

  ##### Games that do not have team scores use the full width
  % else:
    % for team in stats_by_team.keys():
      <div class="row">
        <div class="small-12 columns game">
          ${scoreboard(game.game_type_cd, stats_by_team[team], show_elo, show_latency)}
        </div>
      </div>
    % endfor
  % endif

  % if len(captimes) > 0:
    <div class="row">
      <div class="small-6 columns">
        <h3>Best Flag Capture Times</h3>
        <table class="table-hover table-condensed">
          <thead>
            <tr>
              <th>Nick</th>
              <th>Captime</th>
            </tr>
          </thead>
          <tbody>
          % for pgs in captimes:
          <tr>
            <td>
              % if pgs.player_id > 2:
              <a href="${request.route_url("player_info", id=pgs.player_id)}"
                title="Go to the info page for this player">
                <span class="nick">${pgs.nick_html_colors()|n}</span>
              </a>
              % else:
              <span class="nick">${pgs.nick_html_colors()|n}</span>
              % endif
            </td>
            <td>${round(float(pgs.fastest.seconds) + (pgs.fastest.microseconds/1000000.0), 2)}</td>
          </tr>
          % endfor
          </tbody>
        </table>
      </div>
    </div>
  % endif

  % if len(pgstats) > 0 and len(pwstats) > 0:
    <div class="row">
      <div class="small-12 medium-9 columns">
          <ul class="accordion" data-accordion>
            % for pgstat in pgstats:
              % if pgstat.player_game_stat_id in pwstats:
                <li class="accordion-navigation">
                  <a href="#accuracy-${pgstat.player_game_stat_id}">Accuracy for ${pgstat.nick_html_colors()|n}</a>
                  <div id="accuracy-${pgstat.player_game_stat_id}" class="content">
                    ${accuracy(pwstats[pgstat.player_game_stat_id])}
                  </div>
                </li>
              % endif
            % endfor
          </ul>
        </div>
      </div>
  % endif
% endif
