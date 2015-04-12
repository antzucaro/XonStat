<%def name="accuracy(weapon_stats)">

## Parameters: 
## weapon_stats is an array containing what we'll call "weapon_stat"
## objects. These objects have the following attributes:
##
## [0] = Weapon description
## [1] = Weapon code
## [2] = Actual damage
## [3] = Max damage
## [4] = Hit
## [5] = Fired
## [6] = Frags

<table class="table-hover table-condensed">
  <thead>
    <th></th>
    <th class="show-for-medium-up">Weapon</th>
    <th class="show-for-medium-up">Frags</th>
    <th>Accuracy</th>
    <th>Damage</th>
  </thead>

  <%
    total_damage = 0
    for weapon_stat in weapon_stats:
      total_damage += weapon_stat[2]
    if total_damage == 0:
      total_damage = 1
  %>

  % for weapon_stat in weapon_stats:
    <%
      if weapon_stat[3] > 0: 
        damage_pct = round(float(weapon_stat[2])/weapon_stat[3]*100, 2)
      else:
        damage_pct = 0

      if weapon_stat[5] > 0: 
        hit_pct = round(float(weapon_stat[4])/weapon_stat[5]*100, 2)
      else:
        hit_pct = 0
    %>
    <tr>
      ## Note: the name of the image must match up with the weapon_cd 
      ## entry of that weapon, else this won't work
      <td><span class="sprite sprite-${weapon_stat[1]}"></span></td>
      <td class="show-for-medium-up">${weapon_stat[0]}</td>
      <td class="show-for-medium-up">${weapon_stat[6]}</td>
      <td>${weapon_stat[4]}/${weapon_stat[5]} (${hit_pct}%)</td>
      <td>${weapon_stat[2]} (${round(float(weapon_stat[2])/total_damage*100, 2)}%)</td>
    </tr>
  % endfor
</table>
</%def>
