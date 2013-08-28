<%def name="accuracy_graph(recent_weapons)">
### hitscan weapon data is available
% if 'nex' in recent_weapons or 'rifle' in recent_weapons or 'minstanex' in recent_weapons or 'uzi' in recent_weapons or 'shotgun' in recent_weapons:
<div class="row">
  <div class="col-dm-12">
    <h3>Accuracy</h3>

    <div id="acc-graph" class="flot" style="width:95%; height:200px;">
    </div>

    <div class="weapon-nav accuracy-nav">
      <ul>
      % for weapon in ['nex', 'rifle', 'minstanex', 'uzi', 'shotgun']:
        % if weapon in recent_weapons:
        <li>
        ### the nex is underscored first by default (until user selection)
        % if weapon == 'nex':
        <div class="acc-weap weapon-active">
        % else:
        <div class="acc-weap">
        % endif
          <span class="sprite sprite-${weapon}"></span>
          <p><small>${weapon}</small></p>
          <a href="${request.route_url('player_accuracy', id=player.player_id, _query={'weapon':weapon})}" title="Show ${weapon} accuracy"></a>
        </div>
        </li>
        % endif
      % endfor
      </ul>
    </div>

  </div> <!-- END col-dm-12 -->
</div> <!-- END ROW -->
% endif
</%def>
