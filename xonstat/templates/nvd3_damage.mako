<!DOCTYPE html>
<meta charset="utf-8">

<link href="/static/css/nv.d3.css" rel="stylesheet" type="text/css">

<style>

body {
  overflow-y:scroll;
}

text {
  font: 12px sans-serif;
}

#damageChartSVG, #chart2 {
  height: 500px;
}

</style>
<body>

  <div id="damageChart">
    <svg id="damageChartSVG"></svg>
  </div>

<script src="/static/js/d3.v3.min.js"></script>
<script src="/static/js/nv.d3.min.js"></script>
<script>
    var doDamageGraph = function(data){
        // the chart should fill the "damageChart" div
        var width = document.getElementById("damageChart").offsetWidth;

        // transform the dataset into something nvd3 can use
        var transformedData = d3.nest()
            .key(function(d) { return d.weapon_cd; }).entries(data.weapon_stats);

        // transform games list into a map such that games[game_id] = linear sequence
        var games = {};
        data.games.forEach(function(v,i){ games[v] = i; });

        // margin model
        var margin = {top: 20, right: 30, bottom: 30, left: 40},
            height = 500 - margin.top - margin.bottom;

        width -= margin.left - margin.right;

        // colors
        var colors = d3.scale.category20();
        keyColor = function(d, i) {return colors(d.key)};

        var chart;
        nv.addGraph(function() {
          chart = nv.models.stackedAreaChart()
                        .margin(margin)
                        .width(width)
                        .height(height)
                        .x(function(d) { return games[d.game_id] })
                        .y(function(d) { return d.actual })
                        .color(keyColor);

          chart.xAxis
              .axisLabel("Game ID")
              .showMaxMin(false)
              .ticks(5)
              .tickFormat(function(d) { return data.games[d]; });

          chart.yAxis
              .tickFormat(d3.format(',02d'));

          d3.select('#damageChartSVG')
            .datum(transformedData)
              .transition().duration(500).call(chart);

          nv.utils.windowResize(chart.update);

          return chart;
        });

    }

    % if game_type_cd is not None:
        d3.json("${request.route_url('player_damage_data_v2', id=player_id, _query={'limit':limit, 'game_type':game_type_cd})}", doDamageGraph);
    % else:
        d3.json("${request.route_url('player_damage_data_v2', id=player_id, _query={'limit':limit})}", doDamageGraph);
    % endif
</script>
