<%inherit file="base.mako"/>

<%block name="title">
% if gmap:
Map Information for ${gmap.name} - 
% endif

${parent.title()}
</%block>


% if gmap is None:
<h2>Sorry, that map wasn't found!</h2>

% else:
<h2>Map Detail</h2>
ID: ${gmap.map_id} <br />
Name: ${gmap.name} <br />
% endif
