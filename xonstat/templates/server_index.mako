<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />
<%namespace file="navlinks.mako" import="navlinks" />

<%block name="navigation">
  ${nav.nav('servers')}
</%block>

<%block name="title">
  Server Index
</%block>

% if not servers:
  <h2>Sorry, no servers yet. Get playing!</h2>

% else:
  <div class="row">
    <div class="small-8 small-offset-2 columns">

      <form method="get" action="${request.route_url('search')}">
        <div class="row">
          <div class="small-7 columns">
            <input type="hidden" name="server_name" />
            <input type="text" name="nick" />
          </div>
          <div class="small-5 columns">
            <input type="submit" value="search" />
          </div>
        </div>
      </form>

      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-3">Server ID</th>
            <th class="small-5">Name</th>
            <th class="small-3">Added</th>
            <th class="small-1"></th>
          </tr>
        </thead>
      % for server in servers:
        <tr>
          <td>${server.server_id}</td>
          <td class="no-stretch"><a href="${request.route_url("server_info", id=server.server_id)}" title="Go to this server's info page">${server.name}</a></th>
          <td><span class="abstime" data-epoch="${server.epoch()}" title="${server.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${server.fuzzy_date()}</span></td>
          <td class="text-center">
            <a href="${request.route_url("game_index", _query={'server_id':server.server_id})}" title="View recent games on this server">
              <i class="fa fa-list"></i>
            </a>
          </td>
        </tr>
      % endfor
      </table>

      ${navlinks("server_index", servers.page, servers.last_page)}
    </div>
  </div>
% endif
