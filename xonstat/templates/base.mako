<%namespace name="nav" file="nav.mako"/>
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

    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
    </style>
    <%block name="css">
    <link href="../assets/css/bootstrap-responsive.css" rel="stylesheet">
    <link href="/static/css/style.min.css" rel="stylesheet">
    </%block>
  </head>

  <body>
    <%block name="navigation">
    ${nav.nav("leaderboard")}
    </%block>

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
      <p class="pagination-centered">XonStat is an open source (GPLv2) project created by Antibody. Fork it <a href="https://github.com/antzucaro/XonStat" title="Go to the project page">on Github!</a></p>
      </%block>

      <%block name="js">
      <script src="/static/js/jquery-1.7.1.min.js"></script>
      <script src="/static/js/bootstrap-collapse.min.js"></script>
      </%block>
    </body>
</html>
