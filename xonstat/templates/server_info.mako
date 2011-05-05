<%inherit file="base.mako"/>

<%block name="title">
% if server:
Server Information for ${server.name} - 
% endif

${parent.title()}
</%block>


% if server is None:
<h2>Sorry, that server wasn't found!</h2>

% else:
<h2>Server Detail</h2>
<ul>
   <li>ID: ${server.server_id}</li>
   <li>Name: ${server.name}</li>
   <li>Location: ${server.location}</li>
   <li>IP Address: ${server.ip_addr}</li>
   <li>Maximum Players: ${server.max_players}</li>
   <li>Public Key: ${server.public_key}</li>
   <li>Revision: ${server.revision}</li>
   <li>Pure Indicator: ${server.pure_ind}</li>
   <li>Active Indicator: ${server.active_ind}</li>
   <li>Created: ${server.create_dt}</li>
</ul>
% endif
