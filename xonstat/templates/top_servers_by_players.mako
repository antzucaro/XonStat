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
  <div class="span6 offset3">
    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th style="width:40px;">#</th>
          <th style="width:180px;">Server</th>
          <th style="width:60px;">Games</th>
        </tr>
      </thead>
      <tbody>
      ##### this is to get around the actual row_number/rank of the server not being in the actual query
      <% i = 1 + (top_servers.page-1) * 25%>
      % for (server_id, name, count) in top_servers.items:
        <tr>
          <td>${i}</td>
          % if server_id != '-':
          <td class="nostretch" style="max-width:180px;"><a href="${request.route_url('server_info', id=server_id)}" title="Go to the server info page for ${name}">${name}</a></td>
          % else:
          <td class="nostretch" style="max-width:180px;">${name}</td>
          % endif
          <td>${count}</td>
        </tr>
        <% i = i+1 %>
      % endfor
      </tbody>
    </table>
    <p class="note">*figures are from the past 7 days</p>
  </div> <!-- /span4 -->
% endif

${navlinks("top_servers_by_players", top_servers.page, top_servers.last_page)}
  </div> <!-- /span4 -->
</div> <!-- /row -->
