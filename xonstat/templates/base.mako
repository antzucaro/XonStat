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
    <!-- <link href="/static/css/style.min.css" rel="stylesheet"> -->
    <link href="/static/css/style.css" rel="stylesheet">
    <link type="images/vnd.microsoft.icon" rel="shortcut icon" href="/static/favicon.ico">
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
      <p class="pagination-centered">XonStat is an open source (GPLv2) project created by Antibody. Fork it <a href="https://github.com/antzucaro/XonStat" title="Go to the project page">on Github!</a> <br />Questions? Check the <a href="https://github.com/antzucaro/XonStat/wiki/FAQ" title="FAQ">FAQ</a> first. <br />Issues? Log them either <a href="http://dev.xonotic.org/projects/xonstat" title="Xonotic Redmin Issue Tracker">here</a> or <a href="https://github.com/antzucaro/XonStat/issues" title="GitHub issue tracker">here</a> - I check both!</p>
      </%block>

      <%block name="js">
      </%block>

      <script type="text/javascript">
      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-30391685-1']);
      _gaq.push(['_trackPageview']);

      (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })();
    </script>

    </body>
</html>
