<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="title">
Map captimes
</%block>


<div class="row">
  <div class="span12">

    <h2>${map.name}</h2>
    <p><a href="${map_url}">Back to map info page</a></p>

    <h3>Fastest flag capture times:</h3>

    <table class="table table-bordered table-condensed">
      <thead>
        <tr>
           <th>Game</th>
           <th>Captime</th>
           <th>Nick</th>
           <th>Server</th>
           <th>Date</th>
        </tr>
      </thead>
      <tbody>
      % for ct in captimes:
        <tr>
          <td class="tdcenter"><a class="btn btn-primary btn-small" href="${request.route_url('game_info', id=ct.game_id)}" title="View detailed information about this game">view</a></td>
          <td>${ct.fastest_cap.total_seconds()} seconds</td>
          <td class="player-nick"><span class="nick">${ct.player_nick_html|n}</span></td>
          <td><a href="${request.route_url('server_info', id=ct.server_id)}" title="Go to the detail page for this server">${ct.server_name}</a></td>
          <td><span class="abstime" data-epoch="${ct.create_dt_epoch}" title="${ct.create_dt.strftime('%a, %d %b %Y %H:%M:%S UTC')}">${ct.create_dt_fuzzy}</span></td>
      % endfor
      </tbody>
    </table>

  </div>
</div>
