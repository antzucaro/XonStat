<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
${nav.nav('players')}
</%block>

<%block name="js">
${parent.js()}
<script src="https://login.persona.org/include.js" type="text/javascript"></script>
<script type="text/javascript">${request.persona_js}</script>
</%block>

<%block name="title">
Login
</%block>

<div class="row">
  <div class="span12">
  Hello ${user}
  ${request.persona_button}
  </div>
</div>
