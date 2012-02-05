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

<table class="table table-bordered table-condensed">
<thead>
    <th></th>
    <th>Weapon</th>
    <th>Hit</th>
    <th>Fired</th>
    <th>Hit %</th>
    <th>Actual Damage</th>
    <th>Potential Damage</th>
    <th>Damage %</th>
</thead>
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
    <td><img src="${request.static_url("xonstat:static/images/%s.png" % weapon_stat[1])}" /></td>
    <td>${weapon_stat[0]}</td>
    <td>${weapon_stat[4]}</td>
    <td>${weapon_stat[5]}</td>
    <td>${hit_pct}%</td>
    <td>${weapon_stat[2]}</td>
    <td>${weapon_stat[3]}</td>
    <td>${damage_pct}%</td>
</tr>
% endfor
</table>
</%def>
