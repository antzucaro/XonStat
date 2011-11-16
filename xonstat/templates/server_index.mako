<%inherit file="base.mako"/>

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

% if servers.previous_page:
<a href="${request.route_url("server_index_paged", page=servers.previous_page)}" name="Previous Page">Previous</a>
% endif
% if servers.next_page:
<a href="${request.route_url("server_index_paged", page=servers.next_page)}" name="Next Page">Next</a>
% endif
