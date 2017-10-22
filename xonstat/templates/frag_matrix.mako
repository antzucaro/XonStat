<%def name="frag_matrix(pgstats, matrix_by_pgstat_id)">

## Displays a frag matrix table, in scoreboardpos order from top to bottom and left to right

<table>
  <thead>
    <th></th>
    % for pgstat in pgstats:
    <th><span class="rotated">${pgstat.nick_html_colors()|n}</span></th>
    % endfor
  </thead>

  % for fragger in pgstats:
  <tr>
    <td class="bg">${fragger.nick_html_colors()|n}</td>
    % for victim in pgstats:
    <%
      pgfm = matrix_by_pgstat_id.get(fragger.player_game_stat_id)

      victim_pgfm = matrix_by_pgstat_id.get(victim.player_game_stat_id)
      if victim_pgfm:
        victim_index = str(victim_pgfm.player_index)
      else:
        victim_index = "-1"
    %>

    % if pgfm:
    <td>${pgfm.matrix.get(victim_index, 0)}</td>
    % else:
    <td>0</td>
    % endif
    % endfor
  </tr>
  % endfor
</table>

</%def>
