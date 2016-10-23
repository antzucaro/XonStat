<%inherit file="base.mako"/>
<%namespace name="nav" file="nav.mako" />

<%block name="navigation">
  ${nav.nav('servers')}
</%block>

<%block name="title">
  Server Top Scorer Index
</%block>

% if not top_scorers and last is not None:
  <h2 class="text-center">Sorry, no more players!</h2>

% elif not top_scorers and last is None:
  <h2 class="text-center">No players found. Yikes, get playing!</h2>

% else:
  <div class="row">
    <div class="small-12 large-6 large-offset-3 columns">
      <table class="table-hover table-condensed">
        <thead>
          <tr>
            <th class="small-2">#</th>
            <th class="small-7">Nick</th>
            <th class="small-3">Score</th>
          </tr>
        </thead>
        <tbody>
        % for ts in top_scorers:
          <tr>
            <td>${ts.rank}</td>
            <td class="no-stretch"><a href="${request.route_url('player_info', id=ts.player_id)}" title="Go to the player info page for this player">${ts.nick|n}</a></td>
            <td>${ts.total_score}</td>
          </tr>
        % endfor
        </tbody>
      </table>
      <p class="text-center"><small>Note: these figures are from the past ${lifetime} days</small>
    </div>
  </div>

  % if len(top_scorers) == 20:
    <div class="row">
      <div class="small-12 large-6 large-offset-3 columns">
        <ul class="pagination">
          <li>
            <a  href="${request.route_url('server_top_scorers', id=server_id, _query=query)}" name="Next Page">Next <i class="fa fa-arrow-right"></i></a>
          </li>
        </ul>
      </div>
    </div>
  % endif

% endif
