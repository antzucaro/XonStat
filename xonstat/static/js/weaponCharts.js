var weapons = ["laser", "shotgun", "uzi", "grenadelauncher", "electro", "crylink",
               "nex", "hagar", "rocketlauncher", "minstanex", "rifle",  "fireball",
               "minelayer", "seeker", "tuba", "hlac", "hook", "porto"];

var drawDamageChart = function(data) {
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
      height = 300 - margin.top - margin.bottom;

  width -= margin.left - margin.right;

  // colors
  var colors = d3.scale.category20().domain(weapons);
  keyColor = function(d, i) {return colors(d.key)};

  var chart;
  nv.addGraph(function() {
    chart = nv.models.stackedAreaChart()
      .margin(margin)
      .width(width)
      .height(height)
      .x(function(d) { return games[d.game_id] })
      .y(function(d) { return d.actual })
      .tooltip(function(key, x, y, e, graph) {
        return '<h3>' + key + '</h3>' + '<p>' +  y + ' damage in game #' + x + '</p>'
      })
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

var drawAccuracyChart = function(data) {
  // the chart should fill the "accuracyChart" div
  var width = document.getElementById("accuracyChart").offsetWidth;

  // transform the dataset into something nvd3 can use
  var transformedData = d3.nest()
    .key(function(d) { return d.weapon_cd; }).entries(data.weapon_stats);

  // transform games list into a map such that games[game_id] = linear sequence
  var games = {};
  data.games.forEach(function(v,i){ games[v] = i; });

  // margin model
  var margin = {top: 20, right: 30, bottom: 30, left: 40},
      height = 300 - margin.top - margin.bottom;

  width -= margin.left - margin.right;

  // colors
  var colors = d3.scale.category20().domain(weapons);
  keyColor = function(d, i) {return colors(d.key)};

  var chart;
  nv.addGraph(function() {
    chart = nv.models.lineChart()
      .margin(margin)
      .width(width)
      .height(height)
      .x(function(d) { return games[d.game_id] })
      .y(function(d) {
        if(d.fired > 0) {
          return d.hit/d.fired;
        } else {
          return 0;
        }
      })
      .color(keyColor);

    chart.xAxis
      .axisLabel("Game ID")
      .showMaxMin(false)
      .ticks(5)
      .tickFormat(function(d) { return data.games[d]; });

    chart.yAxis
      .axisLabel('% Accuracy')
      .tickFormat(d3.format('2%'));

    d3.select('#accuracyChartSVG')
      .datum(transformedData)
      .transition().duration(500).call(chart);

    nv.utils.windowResize(chart.update);

    return chart;
  });
}
