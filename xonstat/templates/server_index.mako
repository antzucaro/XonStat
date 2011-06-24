<%inherit file="base.mako"/>

<%block name="title">
Map Index - ${parent.title()}
</%block>

% if not servers:
<h2>Sorry, no servers yet. Get playing!</h2>

% else:
<h2>Server Index</h2>
<table border="1">
  <tr>
    <th>#</th>
    <th>Name</th>
    <th>IP Address</th>
  </tr>
% for server in servers:
  <tr>
    <td>${server.server_id}</th>
    <td><a href="${request.route_url("server_info", id=server.server_id)}" title="Go to this server's info page">${server.name}</a></th>
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
