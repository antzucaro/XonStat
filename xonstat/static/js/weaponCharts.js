// Colors assigned to the various weapons
var weaponColors = {
  "arc": "#7c9ceb", 
  "laser": "#f7717b", 
  "blaster": "#f7717b", 
  "shotgun": "#849ba8", 
  "uzi": "#81f13d", 
  "machinegun": "#81f13d", 
  "grenadelauncher": "#fd7865", 
  "mortar": "#fd7865", 
  "minelayer": "#fd7865", 
  "electro": "#6899f2",
  "crylink": "#ea6ff9", 
  "nex": "#75c3d5", 
  "vortex": "#75c3d5", 
  "hagar": "#e39160", 
  "rocketlauncher": "#e9be57", 
  "devastator": "#e9be57", 
  "porto": "#6899f2", 
  "minstanex": "#978ed2", 
  "vaporizer": "#978ed2", 
  "hook": "#81f13d", 
  "hlac": "#e5965b",
  "seeker": "#f7717b", 
  "rifle": "#e39160", 
  "tuba": "#e9be57", 
  "fireball": "#f0855f"
};

// these weapons are used in the damage chart
var damageWeapons = new Set(["vortex", "machinegun", "shotgun",
        "arc", "uzi", "nex", "minstanex", "rifle", "grenadelauncher", "minelayer",
        "rocketlauncher", "hlac", "seeker", "fireball",  
        "mortar", "electro", "crylink", "hagar", "devastator"]);

// these weapons are used in the accuracy chart
var accuracyWeapons = new Set(["vortex", "machinegun", "shotgun", "vaporizer",
        "arc", "uzi", "nex", "minstanex", "rifle"]);

// draw an accuracy chart into the given element id
function drawAccuracyChart(id, data) {

    // transform games list into a map such that games[game_id] = linear sequence
    var games = {};
    data.games.forEach(function(v,i){ games[v] = i; });

    // for use in filtering out weapons that were not fired
    function wasFired(e) { return e.fired != 0; }

    // for use in filtering out splash-damage weapons
    function isAccuracyWeapon(e) { return accuracyWeapons.has(e.weapon_cd); }

    // transform it into something NVD3 can use
    var accuracyData = d3.nest().key(function(d) { return d.weapon_cd; })
        .entries(data.weapon_stats.filter(isAccuracyWeapon).filter(wasFired));

    nv.addGraph(function() {
      var chart = nv.models.lineChart()
        .useInteractiveGuideline(false)
        .forceY([0,1])
        .showLegend(true)
        .showYAxis(true)
        .showXAxis(true)
        .color(function(d){ return weaponColors[d.key]; })
        .x(function(d) { return games[d.game_id] })
        .y(function(d) { return d.fired > 0 ? d.hit/d.fired : 0; })
      ;

      chart.tooltip.contentGenerator(function(key, y, e, graph) {
          return "<table><tr><td>" +
              key.point.weapon_cd + ": " +
              Math.round(key.point.y*100) + "% (" +
              Math.round(data.averages[key.point.weapon_cd]) + "% avg)" + 
              "</td></tr></table>";
      });

      chart.lines.dispatch.on("elementClick", function(e) { 
          window.location.href = "http://stats.xonotic.org/game/" + e.point.game_id.toString();
      });

      chart.yAxis
          .axisLabel('Accuracy')
          .tickFormat(d3.format('2%'));

      chart.xAxis
          .axisLabel('Games')
          .tickFormat(function(e) { return ''; });

      d3.select("#accuracyChartSVG")
          .datum(accuracyData)
          .call(chart);

      nv.utils.windowResize(function() { chart.update() });
      return chart;
    });
};

// draw an damage chart into the given element id
function drawDamageChart(id, data) {
    
    // transform games list into a map such that games[game_id] = linear sequence
    var games = {};
    data.games.forEach(function(v,i){ games[v] = i; });

    // for use in filtering out splash-damage weapons
    function isDamageWeapon(e) { return damageWeapons.has(e.weapon_cd); }

    // transform it into something NVD3 can use
    var damageData = d3.nest().key(function(d) { return d.weapon_cd; })
        .entries(data.weapon_stats.filter(isDamageWeapon));

    nv.addGraph(function() {
        var chart = nv.models.multiBarChart()
          .reduceXTicks(true)   //If 'false', every single x-axis tick label will be rendered.
          .rotateLabels(0)      //Angle to rotate x-axis labels.
          .showControls(true)   //Allow user to switch between 'Grouped' and 'Stacked' mode.
          .groupSpacing(0.1)    //Distance between each group of bars.
          .showXAxis(true)
          .stacked(true)
          .color(function(d){ return weaponColors[d.key]; })
          .x(function(d) { return games[d.game_id] })
          .y(function(d) { return d.actual; })
        ;

        chart.tooltip.contentGenerator(function(key, y, e, graph) {

            var txt = "<table><tr><td>" +
                key.data.weapon_cd  + ": " + key.data.actual + " HP damage";

            if (key.data.frags > 0) {
                if(key.data.frags > 1) {
                    txt += " (" + key.data.frags + " frags)";
                } else {
                    txt += " (" + key.data.frags + " frag)";
                }
            }
            txt += "</td></tr></table>";

            return txt;
        });

        chart.multibar.dispatch.on("elementClick", function(e) { 
            window.location.href = "http://stats.xonotic.org/game/" + e.data.game_id.toString();
        });

        chart.xAxis
            .axisLabel('Games')
            .tickFormat(function(e){ return '';});

        chart.yAxis
            .axisLabel('Damage (HP)')
            .tickFormat(d3.format(',d'));

        d3.select('#damageChartSVG')
            .datum(damageData)
            .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
    });
};
