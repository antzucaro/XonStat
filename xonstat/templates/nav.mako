<%def name="nav(active)">
    <div class="navbar navbar-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="i-bar"></span>
            <span class="i-bar"></span>
            <span class="i-bar"></span>
          </a>
          <header>
            <a class="brand" href="${request.route_url('main_index')}">
             <img src="/static/css/img/Xonotic_icon.png" /><h1>Xonotic Game Statistics</h1>
            </a>
            <h2>Xonotic is a fast-paced open-source GPL first person shooter</h2>
          </header>
          <div class="nav-collapse">
            <ul class="nav">
              <li 
                % if active=="leaderboard":
                class="active"
                % endif
                ><a href="${request.route_url('main_index')}" title="Leaderboard">Leaderboard</a></li>
              <li 
                % if active=="players":
                class="active"
                % endif
                ><a href="${request.route_url('player_index')}" title="Player Index">Players</a></li>
              <li 
                % if active=="games":
                class="active"
                % endif
                ><a href="${request.route_url('game_index')}" title="Game Index">Games</a></li>
              <li 
                % if active=="servers":
                class="active"
                % endif
                ><a href="${request.route_url('server_index')}" title="Server Index">Servers</a></li>
              <li 
                % if active=="maps":
                class="active"
                % endif
                ><a href="${request.route_url('map_index')}" title="Map Index">Maps</a></li>
            </ul>
            <form id="navsearch" action="${request.route_url('search')}" method="get">
              <input type="hidden" name="fs" />
              <input type="search" class="input-small" placeholder="search" name="sval"/>
              <select name="stype">
                <option>players</option>
                <option>servers</option>
                <option>maps</option>
              </select>
            [<a href="${request.route_url('search')}" title="Advanced search">+</a>]
            </form>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>
</%def>
