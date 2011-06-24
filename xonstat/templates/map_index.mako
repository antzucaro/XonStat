<%inherit file="base.mako"/>

<%block name="title">
Map Index - ${parent.title()}
</%block>

% if not maps:
<h2>Sorry, no maps yet. Get playing!</h2>

% else:
<h2>Map Index</h2>
<table border="1">
  <tr>
    <th>#</th>
    <th>Name</th>
  </tr>
% for map in maps:
  <tr>
    <td>${map.map_id}</th>
    <td><a href="${request.route_url("map_info", id=map.map_id)}" title="Go to this map's info page">${map.name}</a></th>
  </tr>
% endfor
</table>
% endif

% if maps.previous_page:
<a href="${request.route_url("map_index_paged", page=maps.previous_page)}" name="Previous Page">Previous</a>
% endif
% if maps.next_page:
<a href="${request.route_url("map_index_paged", page=maps.next_page)}" name="Next Page">Next</a>
% endif
