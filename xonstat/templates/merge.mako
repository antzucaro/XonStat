<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
${nav.nav('players')}
</%block>

<h1>Player Merge</h1>

<h2>Merge two players below.</h2>

% if len(request.session.peek_flash("failure")) > 0:
<div class="row">
  <div class="span6">
    <div class="alert alert-error">
      <button type="button" class="close" data-dismiss="alert">&times;</button>
      ${request.session.pop_flash("failure")[0]}
    </div>
  </div>
</div>
% endif

% if len(request.session.peek_flash("success")) > 0:
<div class="row">
  <div class="alert alert-success">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    ${request.session.pop_flash("success")[0]}
  </div>
</div>
% endif

<div class="row">
  <div class="span6">
    <form style="margin-top:20px;" class="form-horizontal">
      <fieldset>

        <div class="control-group">
          <label class="control-label" for="w_pid">Winning Player</label>
          <div class="controls">
            <input id="w_pid" name="w_pid" placeholder="Player ID #" class="input-small" type="text">
            <p class="help-block">This player record will live on after the merge is complete.</p>
          </div>
        </div>

        <div class="control-group">
          <label class="control-label" for="l_pid">Losing Player</label>
          <div class="controls">
            <input id="l_pid" name="l_pid" placeholder="Player ID #" class="input-small" type="text">
            <p class="help-block">This player record will be deactivated when the merge is complete.</p>
          </div>
        </div>

        <!-- Form submitted? -->
        <input type="hidden" name="fs" />

        <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}"/>

        <!-- Button -->
        <div class="control-group">
          <label class="control-label"></label>
          <div class="controls">
            <button id="submit" name="submit" type="submit" class="btn btn-primary">Submit</button>
          </div>
        </div>

      </fieldset>
    </form>

  </div>
</div>
