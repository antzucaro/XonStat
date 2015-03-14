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
    <div class="small-6 small-offset-3 columns">

      <form method="get" action="${request.route_url('search')}">
        <div class="row">
          <div class="small-7 columns">
            <input type="hidden" name="fs" />
            <input type="text" name="map_name" />
          </div>
          <div class="small-5 columns">
            <input type="submit" value="search" />
          </div>
        </div>
      </form>

      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-3">ID</th>
            <th class="small-5">Name</th>
            <th class="small-3">Added</th>
            <th class="small-1"></th>
          </tr>
        </thead>
      % for map in maps:
        <tr>
          <td>${map.map_id}</td>
          <td class="no-stretch"><a href="${request.route_url("map_info", id=map.map_id)}" title="Go to this map's info page">${map.name}</a></th>
          <td><span class="abstime" data-epoch="${map.epoch()}" title="${map.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${map.fuzzy_date()}</span></td>
           <td class="text-center">
            <a href="${request.route_url("game_index", _query={'map_id':map.map_id})}" title="View recent games on this map">
              <i class="fa fa-list"></i>
            </a>
          </td>
      </td>
        </tr>
      % endfor
      </table>

      <!-- navigation links -->
      ${navlinks("map_index", maps.page, maps.last_page)}
    </div> <!-- /span4 -->
  </div> <!-- /row -->
% endif
