<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
${nav.nav('maps')}
</%block>

<%block name="title">
Map Index
</%block>

% if not maps:
<h2>Sorry, no maps yet. Get playing!</h2>

% else:
<h2>Map Index</h2>
<form method="get" action="${request.route_url('search')}">
    <input type="hidden" name="fs" />
    <input type="text" name="map_name" />
    <input type="submit" value="search" />
</form>
<table id="map-index-table" border="1">
  <tr>
    <th>Name</th>
    <th>Added</th>
  </tr>
% for map in maps:
  <tr>
    <td><a href="${request.route_url("map_info", id=map.map_id)}" title="Go to this map's info page">${map.name}</a></th>
    <td>${map.create_dt.strftime('%m/%d/%Y at %H:%M')}</td>
</td>
  </tr>
% endfor
</table>
% endif

<!-- navigation links -->
${navlinks("map_index_paged", maps.page, maps.last_page)}
