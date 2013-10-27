<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
${nav.nav('players')}
</%block>

<%block name="title">
Active Players Index
</%block>

% if not top_players:
<h2>Sorry, no players yet. Get playing!</h2>

% else:
##### ACTIVE PLAYERS #####
<div class="row">
  <div class="span6 offset3">
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th style="width:40px;">#</th>
          <th style="width:150px;">Nick</th>
          <th class="play-time" style="width:90px;">Play Time</th>
        </tr>
      </thead>
      <tbody>
      ##### this is to get around the actual row_number/rank of the player not being in the actual query
      <% i = 1 + (top_players.page-1) * 25%>
      % for (player_id, nick, alivetime) in top_players.items:
        <tr>
          <td>${i}</td>
          % if player_id != '-':
          <td class="nostretch" style="max-width:150px;"><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${nick|n}</a></td>
          % else:
          <td class="nostretch" style="max-width:150px;">${nick|n}</td>
          % endif
          <td class="play-time">${alivetime}</td>
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
    <p class="note">*figures are from the past 7 days</p>
  </div> <!-- /span4 -->
% endif

${navlinks("top_players_by_time", top_players.page, top_players.last_page)}
  </div> <!-- /span4 -->
</div> <!-- /row -->
