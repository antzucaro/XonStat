<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="accuracy.mako" import="accuracy" />

<%block name="navigation">
${nav.nav('players')}
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
       Playing Time: <small>${game_stats['total_alivetime']} </small><br />
       <% games_breakdown_str = ', '.join(["{0} {1}".format(ng, gt) for (gt, ng) in games_breakdown]) %>
       Games Played: <small>${total_games} (${games_breakdown_str})</small><br />
       Average Rank: <small>${game_stats['avg_rank']} </small><br />
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
% endif


% if game_stats:
<div class="row">
  <div class="span12">
    <h3>Overall Game Stats</h2>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
          <th>Score</th>
          <th>Carrier Kills</th>
          <th>Kills</th>
          <th>Collects</th>
          <th>Deaths</th>
          <th>Destroys</th>
          <th>Suicides</th>
          <th>Destroys (with key)</th>
          <th>Captures</th>
          <th>Pushes</th>
          <th>Pickups</th>
          <th>Pushed</th>
          <th>Drops</th>
          <th>Returns</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>${game_stats['total_score']}</td>
          <td>${game_stats['total_carrier_frags']}</td>
          <td>${game_stats['total_kills']}</td>
          <td>${game_stats['total_collects']}</td>
          <td>${game_stats['total_deaths']}</td>
          <td>${game_stats['total_destroys']}</td>
          <td>${game_stats['total_suicides']}</td>
          <td>${game_stats['total_destroys']}</td>
          <td>${game_stats['total_captures']}</td>
          <td>${game_stats['total_pushes']}</td>
          <td>${game_stats['total_pickups']}</td>
          <td>${game_stats['total_pushed']}</td>
          <td>${game_stats['total_drops']}</td>
          <td>${game_stats['total_returns']}</td>
        </tr>
      </tbody>
    </table>
    % endif
  </div>
</div>


% if weapon_stats:
<div class="row">
  <div class="span12">
    <h3>Overall Accuracy</h3>
    ${accuracy(weapon_stats)}
  </div>
</div>
% endif


##### RECENT GAMES (v2) ####
% if recent_games:
<div class="row">
  <div class="span6">
    <h3>Recent Games</h3>
    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
           <th>Game Type</th>
           <th>Map</th>
           <th>Result</th>
           <th>Played</th>
           <th>Permalink</th>
        </tr>
      </thead>
      <tbody>
      % for (gamestat, game, server, map) in recent_games:
        <tr>
           <td><img title="${game.game_type_cd}" src="/static/images/icons/24x24/${game.game_type_cd}.png" alt="${game.game_type_cd}" /></td>
           <td>${map.name}</td>
           <td>
           % if gamestat.team != None and gamestat.team == game.winner:
           Won (#${gamestat.rank})
           % elif gamestat.team != None and gamestat.team != game.winner:
           Lost (#${gamestat.rank})
               % else:
               #${gamestat.rank}
           % endif
           </td>
           <td>${game.fuzzy_date()}</td>
           <td><a class="recent_game_box" href="${request.route_url("game_info", id=game.game_id)}" name="Game info page for game #${game.game_id}">View</a></td>
        </tr>
      % endfor
      </tbody>
    </table>
    % if game_stats['total_games_played'] > 10:
    <a href="${request.route_url("player_game_index", player_id=player.player_id, page=1)}" title="Game index for ${player.nick}">More games played by ${player.nick_html_colors()|n}...</a>
    % endif
  </div>
</div>
% endif
