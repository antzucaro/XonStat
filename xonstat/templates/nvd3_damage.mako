<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
${nav.nav('players')}
</%block>

<%block name="title">
Player Damage
</%block>

<%block name="css">
${parent.css()}
<link href="/static/css/sprites.css" rel="stylesheet">
<link href="/static/css/nv.d3.css" rel="stylesheet" type="text/css">

<style>
#damageChartSVG {
  height: 500px;
}
</style>
</%block>

<%block name="js">
<script src="/static/js/d3.v3.js"></script>
<script src="/static/js/nv.d3.min.js"></script>
<script src="/static/js/weaponCharts.js"></script>
<script>
// request initial weaponstats data
% if game_type_cd is not None:
    d3.json("${request.route_url('player_weaponstats_data_json', id=player_id, _query={'limit':limit, 'game_type':game_type_cd})}", drawDamageChart);
% else:
    d3.json("${request.route_url('player_weaponstats_data_json', id=player_id, _query={'limit':limit})}", drawDamageChart);
% endif

// redraw the SVG charts on a gametype icon click
% for gt in ('overall','duel','ctf','dm','tdm','ca','kh','ft','lms','as','dom','nb','cts','rc'):
d3.select('.${gt}').on("click", function() {
  // set class to active
  d3.select('.game_type.active').classed('active', false);
  this.className = "game_type ${gt} active";

  // have to remove the chart each time
  d3.select('#damageChartSVG .nvd3').remove();
  d3.json("${request.route_url('player_weaponstats_data_json', id=player_id, _query={'limit':limit, 'game_type':gt})}", drawDamageChart);
});
% endfor
</script>
</%block>

<div class="row">
  <div class="span12">

    <div id="damageChart">
      <svg id="damageChartSVG"></svg>
    </div>

  </div> <!-- end span12 -->
</div> <!-- end row -->

##### ROW OF GAME TYPE ICONS #####
<div class="row">
  <div class="span12 tabbable">
    <ul class="nav nav-tabs gametype-nav">
      % for gt in ('overall','duel','ctf','dm','tdm','ca','kh','ft','lms','as','dom','nb','cts','rc'):
      <li class="game_type ${gt}
      % if game_type_cd == gt or (game_type_cd is None and gt == 'overall'):
      active
      % endif
      ">
        <a href="#${gt}"><span class="sprite sprite-${gt}"> </span><br />
        ${gt} <br /></a>
      </li>
      % endfor
    </ul>
    <br />
  </div>
</div>
