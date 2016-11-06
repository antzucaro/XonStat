<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
  ${nav.nav('maps')}
</%block>

<%block name="title">
  Active Maps Index
</%block>

% if not top_maps and start is not None:
  <h2 class="text-center">Sorry, no more maps!</h2>

% elif not top_maps and start is None:
  <h2 class="text-center">No active maps found. Yikes, get playing!</h2>

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
        % for tm in top_maps:
          <tr>
            <td>${tm.sort_order}</td>
            <td class="no-stretch"><a href="${request.route_url('map_info', id=tm.map_id)}" title="Go to the map info page for ${tm.map_name}">${tm.map_name}</a></td>
            <td>${tm.games}</td>
          </tr>
        % endfor
        </tbody>
      </table>
      <p class="text-center"><small>Note: these figures are from the past 7 days</small>
    </div>
  </div>

% if len(top_maps) == 20:
<div class="row">
  <div class="small-12 large-6 large-offset-3 columns">
    <ul class="pagination">
      <li>
        <a href="${request.route_url('top_maps_index', _query=query)}" name="Next Page">Next <i class="fa fa-arrow-right"></i></a>
      </li>
    </ul>
  </div>
</div>
% endif

% endif
