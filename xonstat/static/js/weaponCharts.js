// Colors assigned to the various weapons
var weaponColors = {
  "laser": "#ff5933", 
  "shotgun": "#1f77b4", 
  "uzi": "#b9e659", 
  "grenadelauncher": "#ff2600", 
  "minelayer": "#bfbf00", 
  "electro": "#597fff",
  "crylink": "#d940ff", 
  "nex": "#00e6ff", 
  "hagar": "#d98059", 
  "rocketlauncher": "#ffbf33", 
  "porto": "#7fff7f", 
  "minstanex": "#d62728", 
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
  data.addColumn('number', 'Uzi');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Nex');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Minstanex');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Rifle');
  data.addColumn({type: 'string', role: 'tooltip'});

  var flattened = flatten(weaponData);

  for(i in weaponData.games) {
    var game_id = weaponData.games[i];
    var sg = accuracyValue(flattened[game_id], "shotgun");
    var sgTT = accuracyTooltip("shotgun", sg, weaponData.averages);
    var uzi = accuracyValue(flattened[game_id], "uzi");
    var uziTT = accuracyTooltip("uzi", uzi, weaponData.averages); 
    var nex = accuracyValue(flattened[game_id], "nex");
    var nexTT = accuracyTooltip("nex", nex, weaponData.averages);
    var mn = accuracyValue(flattened[game_id], "minstanex");
    var mnTT = accuracyTooltip("minstanex", mn, weaponData.averages);
    var rifle = accuracyValue(flattened[game_id], "rifle");
    var rifleTT = accuracyTooltip("rifle", rifle, weaponData.averages); 

    data.addRow([game_id.toString(), sg, sgTT, uzi, uziTT, nex,
            nexTT, mn, mnTT, rifle, rifleTT]);
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
      1: { color: weaponColors["uzi"] },
      2: { color: weaponColors["nex"] },
      3: { color: weaponColors["minstanex"] },
      4: { color: weaponColors["rifle"] }
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
  data.addColumn('number', 'Uzi');
  data.addColumn({type: 'string', role: 'tooltip'});
  data.addColumn('number', 'Nex');
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
  data.addColumn('number', 'Rocket Launcher');
  data.addColumn({type: 'string', role: 'tooltip'});

  var flattened = flatten(weaponData);

  for(i in weaponData.games) {
    var game_id = weaponData.games[i];
    var sg = damageValue(flattened[game_id], "shotgun");
    var sgTT = damageTooltip("shotgun", sg);
    var uzi = damageValue(flattened[game_id], "uzi");
    var uziTT = damageTooltip("uzi", uzi); 
    var nex = damageValue(flattened[game_id], "nex");
    var nexTT = damageTooltip("nex", nex);
    var mn = damageValue(flattened[game_id], "minstanex");
    var mnTT = damageTooltip("minstanex", mn);
    var rifle = damageValue(flattened[game_id], "rifle");
    var rifleTT = damageTooltip("rifle", rifle); 
    var mortar = damageValue(flattened[game_id], "grenadelauncher");
    var mortarTT = damageTooltip("grenadelauncher", mortar);
    var electro = damageValue(flattened[game_id], "electro");
    var electroTT = damageTooltip("electro", electro); 
    var crylink = damageValue(flattened[game_id], "crylink");
    var crylinkTT = damageTooltip("crylink", crylink);
    var hagar = damageValue(flattened[game_id], "hagar");
    var hagarTT = damageTooltip("hagar", hagar);
    var rl = damageValue(flattened[game_id], "rocketlauncher");
    var rlTT = damageTooltip("rocketlauncher", rl); 

    data.addRow([
      game_id.toString(), 
      sg, sgTT,
      uzi, uziTT,
      nex, nexTT, 
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
      1: { color: weaponColors["uzi"] },
      2: { color: weaponColors["nex"] },
      3: { color: weaponColors["rifle"] },
      4: { color: weaponColors["grenadelauncher"] },
      5: { color: weaponColors["electro"] },
      6: { color: weaponColors["crylink"] },
      7: { color: weaponColors["hagar"] },
      8: { color: weaponColors["rocketlauncher"] }
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
