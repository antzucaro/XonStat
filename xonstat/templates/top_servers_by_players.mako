<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
  ${nav.nav('servers')}
</%block>

<%block name="title">
  Active Servers Index
</%block>

% if not top_servers:
  <h2>Sorry, no servers yet. Get playing!</h2>

% else:
##### ACTIVE SERVERS #####
  <div class="row">
    <div class="small-12 large-6 large-offset-3 columns">
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-2">#</th>
            <th class="small-7">Server</th>
            <th class="small-3">Games</th>
          </tr>
        </thead>
        <tbody>
        ##### this is to get around the actual row_number/rank of the server not being in the actual query
        <% i = 1 + (top_servers.page-1) * 25%>
        % for (server_id, name, count) in top_servers.items:
          <tr>
            <td>${i}</td>
            % if server_id != '-':
            <td class="no-stretch"><a href="${request.route_url('server_info', id=server_id)}" title="Go to the server info page for ${name}">${name}</a></td>
            % else:
            <td class="no-stretch">${name}</td>
            % endif
            <td>${count}</td>
          </tr>
          <% i = i+1 %>
        % endfor
        </tbody>
      </table>
      <small>*figures are from the past 7 days<small>
    </div>
  </div>

  <div class="row">
    <div class="small-12 large-6 large-offset-3 columns">
      ${navlinks("top_servers_by_players", top_servers.page, top_servers.last_page)}
    </div>
  </div>

% endif
