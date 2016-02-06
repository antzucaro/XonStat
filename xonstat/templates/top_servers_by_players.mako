<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
  ${nav.nav('servers')}
</%block>

<%block name="title">
  Active Servers Index
</%block>

% if not top_servers and start is not None:
  <h2 class="text-center">Sorry, no more servers!</h2>

% elif not top_servers and start is None:
  <h2 class="text-center">No active servers found. Yikes, get playing!</h2>

% else:
##### ACTIVE SERVERS #####
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
            <td>${ts.sort_order}</td>
            <td class="no-stretch"><a href="${request.route_url('server_info', id=ts.server_id)}" title="Go to the server info page for ${ts.server_name}">${ts.server_name}</a></td>
            <td>${ts.games}</td>
          </tr>
        % endfor
        </tbody>
      </table>
      <p class="text-center"><small>Note: these figures are from the past 7 days</small>
    </div>
  </div>

% if len(top_servers) == 20:
<div class="row">
  <div class="small-12 large-6 large-offset-3 columns">
    <ul class="pagination">
      <li>
        <a  href="${request.route_url('top_servers_index', _query=query)}" name="Next Page">Next <i class="fa fa-arrow-right"></i></a>
      </li>
    </ul>
  </div>
</div>
% endif

% endif
