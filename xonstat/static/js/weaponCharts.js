// Colors assigned to the various weapons
var weaponColors = {
  "arc": "#b8e9ff", 
  "laser": "#ff5933", 
  "blaster": "#ff5933", 
  "shotgun": "#1f77b4", 
  "uzi": "#b9e659", 
  "machinegun": "#b9e659", 
  "grenadelauncher": "#ff2600", 
  "mortar": "#ff2600", 
  "minelayer": "#bfbf00", 
  "electro": "#597fff",
  "crylink": "#d940ff", 
  "nex": "#00e6ff", 
  "vortex": "#00e6ff", 
  "hagar": "#d98059", 
  "rocketlauncher": "#ffbf33", 
  "devastator": "#ffbf33", 
  "porto": "#7fff7f", 
  "minstanex": "#d62728", 
  "vaporizer": "#d62728", 
  "hook": "#a5ffd8", 
  "hlac": "#ffa533",
  "seeker": "#ff5959", 
  "rifle": "#9467bd", 
  "tuba": "#d87f3f", 
  "fireball": "#33ff33"
};

// Flatten the existing weaponstats JSON requests
// to ease indexing
var flatten = function(weaponData) {
  flattened = {}

  // each game is a key entry...
  weaponData.games.forEach(function(e,i) { flattened[e] = {}; });

  // ... with indexes by weapon_cd
  weaponData.weapon_stats.forEach(function(e,i) { flattened[e.game_id][e.weapon_cd] = e; });

  return flattened;
}

// Calculate the Y value for a given weapon stat
function accuracyValue(gameWeaponStats, weapon) {
  if (gameWeaponStats[weapon] == undefined) {
    return null;
  }
  var ws = gameWeaponStats[weapon];
  var pct = ws.fired > 0 ? Math.round((ws.hit / ws.fired) * 100) : 0;
  
  return pct;
}

// Calculate the tooltip text for a given weapon stat
function accuracyTooltip(weapon, pct, averages) {
  if (pct == null) {
    return null;
  }

  var tt = weapon + ": " + pct.toString() + "%";
  if (averages[weapon] != undefined) {
    return tt + " (" + averages[weapon].toString() + "% average)"; 
  }

  return tt;
}

// Draw the accuracy chart in the "accuracyChart" div id
function drawAccuracyChart(weaponData) {

  var data = new google.visualization.DataTable();
  data.addColumn('string', 'X');
  data.addColumn('number', 'Shotgun');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'MG');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Vortex');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Vaporizer');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Rifle');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Arc');
  data.addColumn({type: 'string', role: 'tooltip'});

  var flattened = flatten(weaponData);

  for(i in weaponData.games) {
    var game_id = weaponData.games[i];
    var sg = accuracyValue(flattened[game_id], "shotgun");
    var sgTT = accuracyTooltip("shotgun", sg, weaponData.averages);
    var mg = accuracyValue(flattened[game_id], "machinegun");
    var mgTT = accuracyTooltip("machinegun", mg, weaponData.averages); 
    var vortex = accuracyValue(flattened[game_id], "vortex");
    var vortexTT = accuracyTooltip("vortex", vortex, weaponData.averages);
    var mn = accuracyValue(flattened[game_id], "vaporizer");
    var mnTT = accuracyTooltip("vaporizer", mn, weaponData.averages);
    var rifle = accuracyValue(flattened[game_id], "rifle");
    var rifleTT = accuracyTooltip("rifle", rifle, weaponData.averages); 
    var arc = accuracyValue(flattened[game_id], "arc");
    var arcTT = accuracyTooltip("arc", arc, weaponData.averages); 

    data.addRow([game_id.toString(), sg, sgTT, mg, mgTT, vortex,
            vortexTT, mn, mnTT, rifle, rifleTT, arc, arcTT]);
  }

  var options = {
    backgroundColor: { fill: 'transparent' },
    lineWidth: 2,
    legend: { 
      textStyle: { color: "#666" }
    },
    hAxis: {
      title: 'Games',
      textPosition: 'none',
      titleTextStyle: { color: '#666' }
    },
    vAxis: {
      title: 'Percentage',
      titleTextStyle: { color: '#666' },
      minValue: 0,
      maxValue: 100,
      baselineColor: '#333',
      gridlineColor: '#333',
      ticks: [20, 40, 60, 80, 100]
    },
    series: {
      0: { color: weaponColors["shotgun"] },
      1: { color: weaponColors["machinegun"] },
      2: { color: weaponColors["vortex"] },
      3: { color: weaponColors["vaporizer"] },
      4: { color: weaponColors["rifle"] },
      5: { color: weaponColors["arc"] }
    }
  };

  var chart = new google.visualization.LineChart(document.getElementById('accuracyChart'));

  // a click on a point sends you to that games' page
  var accuracySelectHandler = function(e) {
    var selection = chart.getSelection()[0];
    if (selection != null && selection.row != null) {
      var game_id = data.getFormattedValue(selection.row, 0);
      window.location.href = "http://stats.xonotic.org/game/" + game_id.toString();
    }
  };
  google.visualization.events.addListener(chart, 'select', accuracySelectHandler);

  chart.draw(data, options);
}

// Calculate the damage Y value for a given weapon stat
function damageValue(gameWeaponStats, weapon) {
  if (gameWeaponStats[weapon] == undefined) {
    return null;
  }
  return gameWeaponStats[weapon].actual;
}

// Calculate the damage tooltip text for a given weapon stat
function damageTooltip(weapon, dmg) {
  if (dmg == null) {
    return null;
  }
  return weapon + ": " + dmg.toString() + " HP damage";
}

// Draw the damage chart into the "damageChart" div id
function drawDamageChart(weaponData) {

  var data = new google.visualization.DataTable();
  data.addColumn('string', 'X');
  data.addColumn('number', 'Shotgun');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Machine Gun');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Vortex');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Rifle');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Mortar');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Electro');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Crylink');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Hagar');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Devastator');
  data.addColumn({type: 'string', role: 'tooltip'});

  var flattened = flatten(weaponData);

  for(i in weaponData.games) {
    var game_id = weaponData.games[i];
    var sg = damageValue(flattened[game_id], "shotgun");
    var sgTT = damageTooltip("shotgun", sg);
    var mg = damageValue(flattened[game_id], "machinegun");
    var mgTT = damageTooltip("machinegun", mg); 
    var vortex = damageValue(flattened[game_id], "vortex");
    var vortexTT = damageTooltip("vortex", vortex);
    var mn = damageValue(flattened[game_id], "vaporizer");
    var mnTT = damageTooltip("vaporizer", mn);
    var rifle = damageValue(flattened[game_id], "rifle");
    var rifleTT = damageTooltip("rifle", rifle); 
    var mortar = damageValue(flattened[game_id], "mortar");
    var mortarTT = damageTooltip("mortar", mortar);
    var electro = damageValue(flattened[game_id], "electro");
    var electroTT = damageTooltip("electro", electro); 
    var crylink = damageValue(flattened[game_id], "crylink");
    var crylinkTT = damageTooltip("crylink", crylink);
    var hagar = damageValue(flattened[game_id], "hagar");
    var hagarTT = damageTooltip("hagar", hagar);
    var rl = damageValue(flattened[game_id], "devastator");
    var rlTT = damageTooltip("devastator", rl); 

    data.addRow([
      game_id.toString(), 
      sg, sgTT,
      mg, mgTT,
      vortex, vortexTT, 
      rifle, rifleTT,
      mortar, mortarTT,
      electro, electroTT,
      crylink, crylinkTT,
      hagar, hagarTT,
      rl, rlTT
    ]);
  }

  var options = {
    backgroundColor: { fill: 'transparent' },
    legend: { 
      position: 'top', 
      maxLines: 3,
      textStyle: { color: "#666" }
    },
    vAxis: {
      title: 'HP Damage',  
      titleTextStyle: {color: '#666'},
      baselineColor: '#333',
      gridlineColor: '#333',
    },
    hAxis: {
      title: 'Games',
      textPosition: 'none',
      titleTextStyle: { color: '#666' },
    },
    isStacked: true,
    series: {
      0: { color: weaponColors["shotgun"] },
      1: { color: weaponColors["machinegun"] },
      2: { color: weaponColors["vortex"] },
      3: { color: weaponColors["rifle"] },
      4: { color: weaponColors["mortar"] },
      5: { color: weaponColors["electro"] },
      6: { color: weaponColors["crylink"] },
      7: { color: weaponColors["hagar"] },
      8: { color: weaponColors["devastator"] }
    }
  };

  var chart = new google.visualization.ColumnChart(document.getElementById('damageChart'));

  // a click on a point sends you to that game's page
  var damageSelectHandler = function(e) {
    var selection = chart.getSelection()[0];
    if (selection != null && selection.row != null) {
      var game_id = data.getFormattedValue(selection.row, 0);
      window.location.href = "http://stats.xonotic.org/game/" + game_id.toString();
    }
  };
  google.visualization.events.addListener(chart, 'select', damageSelectHandler);

  chart.draw(data, options);
}
