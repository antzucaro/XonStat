<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
  ${nav.nav('servers')}
</%block>

<%block name="title">
  Server Top Map Index
</%block>

% if not top_maps and last is not None:
  <h2 class="text-center">Sorry, no more maps!</h2>

% elif not top_maps and last is None:
  <h2 class="text-center">No maps found. Yikes, get playing!</h2>

% else:
  <div class="row">
    <div class="small-12 large-6 large-offset-3 columns">
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-2">#</th>
            <th class="small-7">Map</th>
            <th class="small-3">Times Played</th>
          </tr>
        </thead>
        <tbody>
        % for tm in top_maps:
          <tr>
            <td>${tm.rank}</td>
            <td class="no-stretch"><a href="${request.route_url('map_info', id=tm.map_id)}" title="Go to the map info page for this map">${tm.name|n}</a></td>
            <td>${tm.times_played}</td>
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
            <a  href="${request.route_url('server_top_maps', id=server_id, _query=query)}" name="Next Page">Next <i class="fa fa-arrow-right"></i></a>
          </li>
        </ul>
      </div>
    </div>
  % endif

% endif
