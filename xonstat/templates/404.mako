<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
  ${nav.nav('games')}
</%block>

<h1>HTTP 404</h1>

% if 0 <= rand < 30:
  <h2>Well this is <i>awkward</i>...I couldn't find what you were looking for!</h2>
  <p>(better get back to playing then, <b>hm</b>?)</p>
% endif

% if 30 <= rand < 40:
  <h2>Whoa there! Looks like you've taken a wrong turn.</h2>
  <p>(no one <i>tries</i> to get on highway 404, <b>no one</b>.)</p>
% endif

% if 40 <= rand < 50:
  <h2>There's nothing to see here. *waves hand*</h2>
  <p>(did Mirio put you up to this?)</p>
% endif

% if 50 <= rand < 60:
  <h2>Hey, you! Watch out - kojn's behind you!</h2>
  <p>(he killed this page, apparently)</p>
% endif

% if 60 <= rand < 70:
  <h2>Samual must have destroyed this page.</h2>
  <p>(it wasn't pulling its own weight anyway)</p>
% endif

% if 70 <= rand < 80:
  <h2>divVerent has encrypted this page so hard you'll never decipher it.</h2>
  <p>(either that or you've hit the wrong page or something)</p>
% endif

% if 80 <= rand < 90:
  <h2>merlijn was unhappy with this page, so he removed it from the server.</h2>
  <p>(after yelling at me about it, of course)</p>
% endif

% if 90 <= rand <= 100:
  <h2>Morphed is modeling this page. It's gonna be awesome.</h2>
  <p>(until then, you'll probably want to get in a game or two)</p>
% endif
