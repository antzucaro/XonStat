<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>XonStat: Player Statistics for Xonotic</title>
    <meta name="description" content="">
    <meta name="author" content="">

    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <link href="/static/css/style.css" rel="stylesheet">
    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
    </style>
    <%block name="css">
    <link href="../assets/css/bootstrap-responsive.css" rel="stylesheet">
    </%block>
  </head>

  <body>

    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="i-bar"></span>
            <span class="i-bar"></span>
            <span class="i-bar"></span>
          </a>
          <a class="brand" href="#"><img src="/static/css/img/Xonotic_icon.png" /></a>
          <div class="nav-collapse">
            <ul class="nav">
              <li class="active"><a href="${request.route_url('main_index')}" title="Leaderboard">Leaderboard</a></li>
              <li><a href="${request.route_url('player_index')}" title="Player Index">Players</a></li>
              <li><a href="${request.route_url('game_index')}" title="Game Index">Games</a></li>
              <li><a href="${request.route_url('server_index')}" title="Server Index">Servers</a></li>
              <li><a href="${request.route_url('map_index')}" title="Map Index">Maps</a></li>
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>

    <div class="container">

      <%block name="hero_unit">
      </%block>

      <div class="row">
        <div class="span12" id="xonborder">
          <div id="title"><%block name="title"></%block></div>
            ${self.body()}
        </div> <!-- /xonborder -->
      </div> <!-- /main row -->

      <%block name="footer">
        <p>XonStat is an open source (GPLv2) project created by Antibody. Fork it <a href="https://github.com/antzucaro/XonStat" title="Go to the project page">on Github!</a></p>
      </%block>
      <%block name="js">
      </%block>
    </body>
</html>
