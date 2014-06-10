<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
${nav.nav('players')}
</%block>

<h1>Player Merge</h1>

<h2>Merge two players below. The destination player_id is on the right.</h2>
<p>(the destination player_id is the one that lives on after the merge)</p>
