<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
  ${nav.nav('maps')}
</%block>

<%block name="title">
  Active Maps Index
</%block>

% if not top_maps:
<h2>Sorry, no maps yet. Get playing!</h2>

% else:
##### ACTIVE SERVERS #####
  <div class="row">
    <div class="small-12 large-6 large-offset-3 columns">
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-2">#</th>
            <th class="small-7">Map</th>
            <th class="small-3">Games</th>
          </tr>
        </thead>
        <tbody>
        ##### this is to get around the actual row_number/rank of the map not being in the actual query
        <% i = 1 + (top_maps.page-1) * 25%>
        % for (map_id, name, count) in top_maps:
          <tr>
            <td>${i}</td>
            % if map_id != '-':
            <td class="no-stretch"><a href="${request.route_url('map_info', id=map_id)}" title="Go to the map info page for ${name}">${name}</a></td>
            % else:
            <td class="nostretch">${name}</td>
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
      ${navlinks("top_maps_by_times_played", top_maps.page, top_maps.last_page)}
    </div>
  </div>

% endif
