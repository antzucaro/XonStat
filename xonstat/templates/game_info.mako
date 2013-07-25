<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="scoreboard.mako" import="scoreboard" />
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="navigation">
${nav.nav('games')}
</%block>

<%block name="css">
${parent.css()}
<link href="/static/css/sprites.css" rel="stylesheet">
</%block>

<%block name="js">
${parent.js()}
<script>
$(".collapse").collapse();

// show accordion only when loaded to prevent rollup from being seen
$("#acc-accordion").css('display', '');
</script>
</%block>

<%block name="title">
Game Information
</%block>


% if game is None:
<h2>Sorry, that game wasn't found!</h2>

% else:
<div class="row">
  <h2>Game Detail</h2>
  <div class="span8 game-detail">
    <img width="64" height="64" src="/static/images/icons/48x48/${game.game_type_cd}.png" alt="${game.game_type_cd}"/>
    <p>
    Played: <span class="abstime" data-epoch="${game.epoch()}" title="${game.start_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${game.fuzzy_date()}</span><br />
    Game Type: ${gametype.descr} (${game.game_type_cd})<br />
    Server: <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a><br />
    Map: <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a><br />
    % if game.duration is not None:
    Duration: ${"%s:%02d" % (game.duration.seconds/60, game.duration.seconds%60)}
    % endif
    </p>
    <span class="clear"></span>
  </div>
  % if teamscores:
  <div class="span3 teamscores">
    <table class="table table-condensed">
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

% if len(tgstats) == len(stats_by_team):
## if we have teamscores in the db
% for tgstat in tgstats:
<div class="row">
  <div class="span1 teamscore">
  <div class="teamname ${tgstat.team_html_color()}">
  ${tgstat.team_html_color().capitalize()}
  </div>
  <div class="${tgstat.team_html_color()}">
  % if game.game_type_cd == 'ctf':
  ${tgstat.caps}
  % elif game.game_type_cd == 'ca':
  ${tgstat.rounds}
## dom -> ticks, rc -> laps, nb -> goals, as -> objectives
  % else:
  ${tgstat.score}
  % endif
  </div>
  </div>
  <div class="span10 game">
  ${scoreboard(game.game_type_cd, stats_by_team[tgstat.team], show_elo, show_latency)}
  </div>
</div>
% endfor
% else:
% for team in stats_by_team.keys():
<div class="row">
  <div class="span12 game">
  ${scoreboard(game.game_type_cd, stats_by_team[team], show_elo, show_latency)}
  </div>
</div>
% endfor
% endif

% if len(captimes) > 0:
<div class="row">
  <div class="span6">
    <h3>Best Flag Capture Times</h3>
    <table class="table table-hover table-condensed">
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
  <div class="span12">
    <h3>Accuracy Information</h3>
    <div class="accordion" id="acc-accordion" style="display:none;">
      % for pgstat in pgstats:
      % if pgstat.player_game_stat_id in pwstats:
      <div class="accordion-group">
        <div class="accordion-heading">
          <a class="accordion-toggle" data-toggle="collapse" data-parent="#acc-accordion" href="#accuracy-${pgstat.player_game_stat_id}">
            Accuracy for ${pgstat.nick_html_colors()|n}
          </a>
        </div>
        <div id="accuracy-${pgstat.player_game_stat_id}" class="accordion-body collapse in">
          <div class="accordion-inner">
            ${accuracy(pwstats[pgstat.player_game_stat_id])}
          </div>
        </div>
      </div>
      % endif
      % endfor
    </div>
  </div>
  % endif

</div>
% endif
