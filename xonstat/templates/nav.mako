<%def name="nav(active='leaderboard', login_logout=False)">

<!-- HEADER NAVIGATION -->
<div class="contain-to-grid">

  <div class="row text-center">
    <div class="small-12 columns">

      <nav class="top-bar" data-topbar="" data-options="is_hover: false">
        <ul class="title-area">
          <li class="name show-for-medium-up">
            <h1><a href="http://www.xonotic.org">Xonotic</a></h1>
          </li>
          <li class="name show-for-small-only">
            <a href="/"><img src="/static/css/img/xonotic-icon-mono.png"></a>
          </li>
          <li class="toggle-topbar menu-icon"><a href="#"><span></span></a></li>
        </ul>

        <section class="top-bar-section">
          <!-- Left Nav Section -->
          <ul class="left">
            <li><a href="http://www.xonotic.org/download/" title="Download the game"><i class="fa fa-download"></i> Download</a></li>
            <li><a href="http://www.xonotic.org/media/" title="View screenshots and videos"><i class="fa fa-picture-o"></i> Media</a></li>
            <li><a href="http://forums.xonotic.org/" title="Visit the community forums"><i class="fa fa-comments"></i> Forums</a></li>
            <li><a href="http://www.xonotic.org/posts/" title="Read the blog"><i class="fa fa-book"></i> Blog</a></li>
            <li class="has-dropdown">
              <a href="/" title="View player statistics and recent games"><i class="fa fa-bar-chart"></i> Stats</a>
              <ul class="dropdown">
                <li><a href="${request.route_url('main_index')}" title="Leaderboard">Leaderboard</a></li>
                <li><a href="${request.route_url('player_index')}" title="Player Index">Players</a></li>
                <li><a href="${request.route_url('game_index')}" title="Game Index">Games</a></li>
                <li><a href="${request.route_url('server_index')}" title="Server Index">Servers</a></li>
                <li><a href="${request.route_url('map_index')}" title="Map Index">Maps</a></li>
                <li><a href="${request.route_url('search')}" title="Search">Search</a></li>
              </ul>
            </li>
            <li><a href="https://gitlab.com/groups/xonotic" title="Contribute to Xonotic"><i class="fa fa-wrench"></i> Contribute</a></li>
            <li><a href="https://gitlab.com/xonotic/xonotic/wikis/Halogenes_Newbie_Corner" title="Read the beginner's guide"><i class="fa fa-forward"></i> Guide</a></li>
          </ul>
        </section>
      </nav>

    </div>
  </div> <!-- END ROW -->
</div> <!-- END HEADER NAVIGATION -->

</%def>
