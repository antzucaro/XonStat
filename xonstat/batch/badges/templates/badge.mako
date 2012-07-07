<html>
  <head>
    <link href="../css/style.css" rel="stylesheet">
  </head>
  <body>
    <div id="badge">
      <div id="nick">
        <b>
          ${player.nick_html_colors()|n}
        </b>
      </div>

      <div id="games_played">
        <% games_breakdown_str = ', '.join(["{0} {1}".format(ng, gt) for (gt, ng) in games_breakdown]) %>
        ${total_games} (${games_breakdown_str})
      </div>

      <div id="win_percentage">
        % if total_games > 0 and total_stats['wins'] is not None:
          ${total_stats['wins']} wins, ${total_games - total_stats['wins']} losses (${round(float(total_stats['wins'])/total_games * 100, 2)}%)
        % endif
      </div>

      <div id="kill_ratio">
        % if total_stats['kills'] > 0 and total_stats['deaths'] > 0:
          ${total_stats['kills']} kills, ${total_stats['deaths']} deaths (${round(float(total_stats['kills'])/total_stats['deaths'], 3)})
        % endif
      </div>

      <div id="elo">
        % if elos_display is not None and len(elos_display) > 0:
         Elo: ${', '.join(elos_display[0:2])}
       % endif
      </div>

    </div>

  </body>
</html>
