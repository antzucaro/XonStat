<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
${nav.nav('players')}
</%block>

<%block name="title">
Login
</%block>

<div class="row">
  <div class="span12">
  Hello ${user}
  </div>
</div>
