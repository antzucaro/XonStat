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
<link href="/static/css/nv.d3.css" rel="stylesheet" type="text/css">

<style>
body {
  overflow-y:scroll;
}

text {
  font: 12px sans-serif;
}

#damageChartSVG {
  height: 500px;
}
</style>
</%block>

<script src="/static/js/d3.v3.min.js"></script>

<%block name="js">
${parent.js()}
<script src="/static/js/d3.v3.js"></script>
<script src="/static/js/nv.d3.min.js"></script>
<script src="/static/js/weaponCharts.js"></script>
<script>
% if game_type_cd is not None:
    d3.json("${request.route_url('player_weaponstats_data_json', id=player_id, _query={'limit':limit, 'game_type':game_type_cd})}", drawDamageChart);
% else:
    d3.json("${request.route_url('player_weaponstats_data_json', id=player_id, _query={'limit':limit})}", drawDamageChart);
% endif
</script>
</%block>

<div class="row">
  <div class="span12">

    <div id="damageChart">
      <svg id="damageChartSVG"></svg>
    </div>

  </div>
</div>
