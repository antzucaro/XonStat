<%def name="damage_graph(recent_weapons)">
### splash weapon info is available
% if 'rocketlauncher' in recent_weapons or 'grenadelauncher' in recent_weapons or 'electro' in recent_weapons or 'crylink' in recent_weapons or 'laser' in recent_weapons:
<div class="row">
  <div class="col-md-12">
    <h3>Damage Efficiency</h3>

    <div id="dmg-graph" class="flot" style="width:95%; height:200px;">
    </div>

    <div class="weapon-nav damage-nav">
      <ul>
      % for weapon in ['rocketlauncher', 'grenadelauncher', 'electro', 'crylink', 'hagar', 'laser']:
        % if weapon in recent_weapons:
        <li>
        ### the rocketlauncher is underscored first by default (until user selection)
        % if weapon == 'rocketlauncher':
          <div class="dmg-weap weapon-active">
        % else:
          <div class="dmg-weap">
        % endif
            <span class="sprite sprite-${weapon}"></span>
            <p><small>${weapon}</small></p>
            <a href="${request.route_url('player_damage', id=player.player_id, _query={'weapon':weapon})}" title="Show ${weapon} efficiency"></a>
          </div>
        </li>
        % endif
      % endfor
      </ul>
    </div>

  </div> <!-- END col-md-12 -->
</div> <!-- END ROW -->
% endif
</%def>
