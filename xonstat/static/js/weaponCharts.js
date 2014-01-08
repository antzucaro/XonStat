var weapons = ["laser", "shotgun", "uzi", "grenadelauncher", "minelayer", "electro",
    "crylink", "nex", "hagar", "rocketlauncher", "porto", "minstanex", "hook", "hlac",
    "seeker", "rifle", "tuba", "fireball"];

var weaponColors = ["#ff5933", "#b2b2b2", "#66e559", "#ff2600", "#bfbf00", "#597fff",
    "#d83fff", "#00e5ff", "#d87f59", "#ffbf33", "#7fff7f", "#a5a5ff", "#a5ffd8",
    "#ffa533", "#ff5959", "#d87f3f", "#d87f3f", "#33ff33"];

var colorScale = d3.scale.ordinal().domain(weapons).range(weaponColors);

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
  var margin = {top: 20, right: 30, bottom: 30, left: 60},
      height = 300 - margin.top - margin.bottom;

  width -= margin.left - margin.right;

  // colors
  keyColor = function(d, i) {return colorScale(d.key)};

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

  // get rid of empty values
  data.weapon_stats = data.weapon_stats.filter(function(e){ return e.fired > 0; });

  // transform the dataset into something nvd3 can use
  var transformedData = d3.nest()
    .key(function(d) { return d.weapon_cd; }).entries(data.weapon_stats);

  var findNumGames = function(weapon) {
    var numGames = transformedData.filter(function(e){return e.key == weapon})[0].values.length;
    if(numGames !== undefined) {
        return numGames;
    } else {
        return 0;
    }
  };

  // transform games list into a map such that games[game_id] = linear sequence
  var games = {};
  data.games.forEach(function(v,i){ games[v] = i; });

  // margin model
  var margin = {top: 20, right: 30, bottom: 30, left: 40},
      height = 300 - margin.top - margin.bottom;

  width -= margin.left - margin.right;

  // colors
  keyColor = function(d, i) {return colorScale(d.key)};

  var chart;
  nv.addGraph(function() {
    chart = nv.models.lineChart()
      .margin(margin)
      .width(width)
      .height(height)
      .forceY([0,1])
      .x(function(d) { return games[d.game_id] })
      .y(function(d) {
        if(d.fired > 0) {
          return d.hit/d.fired;
        } else {
          return 0;
        }
      })
      .tooltip(function(key, x, y, e, graph) {
        return '<h3>' + key + '</h3>' + '<p>' +  y + ' accuracy in game #' + x + ' <br /> ' + data.averages[key]  + '% average over ' + findNumGames(key) + ' games</p>';
      })
      .color(keyColor);

    chart.xAxis
      .axisLabel("Game ID")
      .showMaxMin(false)
      .ticks(5)
      .tickFormat(function(d) { return data.games[d]; });

    var yScale = d3.scale.linear().domain([0,1]).range([0,height]);
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
