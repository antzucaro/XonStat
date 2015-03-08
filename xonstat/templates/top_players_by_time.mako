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
    <div class="small-12 large-6 large-offset-3">
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-2">#</th>
            <th class="small-7">Nick</th>
            <th class="small-3">Play Time</th>
          </tr>
        </thead>

        <tbody>
        ##### this is to get around the actual row_number/rank of the player not being in the actual query
        <% i = 1 + (top_players.page-1) * 25%>
        % for (player_id, nick, alivetime) in top_players.items:
          <tr>
            <td>${i}</td>
            % if player_id != '-':
            <td class="no-stretch"><a href="${request.route_url('player_info', id=player_id)}" title="Go to the player info page for this player">${nick|n}</a></td>
            % else:
            <td class="no-stretch">${nick|n}</td>
            % endif
            <td>${alivetime}</td>
          </tr>
          <% i = i+1 %>
        % endfor
        </tbody>
      </table>
      <small>*figures are from the past 7 days</small>
    </div>
  </div>

  <div class="row">
    <div class="small-12 large-6 large-offset-3">
      ${navlinks("top_players_by_time", top_players.page, top_players.last_page)}
    </div>
  </div>
% endif
