<%def name="frag_matrix(pgstats, matrix_by_pgstat_id)">

## Displays a frag matrix table, in scoreboardpos order from top to bottom and left to right

<table class="table-hover table-condensed">
  <thead>
    <th></th>
    % for pgstat in pgstats:
    <th>${pgstat.nick_html_colors()|n}</th>
    % endfor
  </thead>

  % for fragger in pgstats:
  <tr>
    <td>${fragger.nick_html_colors()|n}</td>
    % for victim in pgstats:
    <%
      pgfm = matrix_by_pgstat_id.get(fragger.player_game_stat_id)

      victim_pgfm = matrix_by_pgstat_id.get(victim.player_game_stat_id)
      if victim_pgfm:
        victim_index = str(victim_pgfm.player_index)
      else:
        victim_index = "-1"
    %>
    <td>${pgfm.matrix.get(victim_index, 0)}</td>
    % endfor
  </tr>
  % endfor
</table>

</%def>
