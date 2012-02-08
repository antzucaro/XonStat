<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="scoreboard.mako" import="scoreboard" />
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="navigation">
${nav.nav('games')}
</%block>

<%block name="js">
      <script src="/static/js/jquery-1.7.1.min.js"></script>
      <script src="/static/js/bootstrap-collapse.min.js"></script>
      <script>
        $(".collapse").collapse()
      </script>
</%block>

<%block name="title">
Game Information
</%block>


% if game is None:
<h2>Sorry, that game wasn't found!</h2>

% else:
<div class="row">
  <div class="span6">
    <h2>Game Detail</h2>
    <p>
      Played on: ${game.start_dt.strftime('%m/%d/%Y at %I:%M %p')}<br />
      Game Type: ${game.game_type_cd}<br />
      Server: <a href="${request.route_url("server_info", id=server.server_id)}" name="Server info page for ${server.name}">${server.name}</a><br />
      Map: <a href="${request.route_url("map_info", id=map.map_id)}" name="Map info page for ${map.name}">${map.name}</a><br />
    </p>
  </div>
</div>

<div class="row">
  <div class="span12">
    <h3>Scoreboard</h3>
    ${scoreboard(game.game_type_cd, pgstats)}
  </div>
</div>

% if len(pgstats) > 0:
<div class="row">
  <div class="span12">
    <h3>Accuracy Information</h3>
    <div class="accordion" id="acc-accordion">
    % for pgstat in pgstats:
    % if pgstat.player_game_stat_id in pwstats:
      <div class="accordion-group">
        <div class="accordion-heading">
          <a class="accordion-toggle" data-toggle="collapse" data-parent="#acc-accordion" href="#${pgstat.player_game_stat_id}">
          Accuracy for ${pgstat.nick_html_colors()|n}
          </a>
        </div>
        <div id="${pgstat.player_game_stat_id}" class="accordion-body collapse in">
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
