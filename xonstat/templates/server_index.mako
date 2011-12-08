<%inherit file="base.mako"/>
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="title">
Map Index - ${parent.title()}
</%block>

% if not servers:
<h2>Sorry, no servers yet. Get playing!</h2>

% else:
<h2>Server Index</h2>
<table id="server-index-table" border="1">
  <tr>
    <th>Name</th>
    <th class="create-dt">Added</th>
  </tr>
% for server in servers:
  <tr>
    <td><a href="${request.route_url("server_info", id=server.server_id)}" title="Go to this server's info page">${server.name}</a></th>
    <td>${server.create_dt.strftime('%m/%d/%Y at %H:%M')}</td>
  </tr>
% endfor
</table>
% endif

<!-- navigation links -->
${navlinks("server_index_paged", servers.page, servers.last_page)}
