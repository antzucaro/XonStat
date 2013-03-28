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
<div class="row">
  <div class="span6 offset3">
    <form class="indexform" method="get" action="${request.route_url('search')}">
      <input type="hidden" name="fs" />
      <input class="indexbox" type="text" name="map_name" />
      <input type="submit" value="search" />
    </form>
    <table class="table table-hover table-condensed">
      <tr>
        <th>Name</th>
        <th>Added</th>
      </tr>
    % for map in maps:
      <tr>
        <td><a href="${request.route_url("map_info", id=map.map_id)}" title="Go to this map's info page">${map.name}</a></th>
        <td><span class="abstime" data-epoch="${map.epoch()}" title="${map.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${map.fuzzy_date()}</span></td>
    </td>
      </tr>
    % endfor
    </table>
    % endif

    <!-- navigation links -->
    ${navlinks("map_index", maps.page, maps.last_page)}
  </div> <!-- /span4 -->
</div> <!-- /row -->
