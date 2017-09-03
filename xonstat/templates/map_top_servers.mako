<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
  ${nav.nav('maps')}
</%block>

<%block name="title">
  Map Top Server Index
</%block>

% if not top_servers and last is not None:
  <h2 class="text-center">Sorry, no more servers!</h2>

% elif not top_servers and last is None:
  <h2 class="text-center">No servers found. Yikes, get playing!</h2>

% else:
  <div class="row">
    <div class="small-12 large-6 large-offset-3 columns">
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-2">#</th>
            <th class="small-7">Server</th>
            <th class="small-3">Games</th>
          </tr>
        </thead>
        <tbody>
        % for ts in top_servers:
          <tr>
            <td>${ts.rank}</td>
            <td class="no-stretch"><a href="${request.route_url('server_info', id=ts.server_id)}" title="Go to the server info page for this server">${ts.server_name}</a></td>
            <td>${ts.games}</td>
          </tr>
        % endfor
        </tbody>
      </table>
      <p class="text-center"><small>Note: these figures are from the past ${lifetime} days</small></p>
    </div>
  </div>

  % if len(top_servers) == 20:
    <div class="row">
      <div class="small-12 large-6 large-offset-3 columns">
        <ul class="pagination">
          <li>
            <a  href="${request.route_url('map_top_servers', id=map_id, _query=query)}" name="Next Page">Next <i class="fa fa-arrow-right"></i></a>
          </li>
        </ul>
      </div>
    </div>
  % endif

% endif
