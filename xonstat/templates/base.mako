<%namespace name="nav" file="nav.mako"/>
<%namespace name="footer" file="footer.mako" />

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="XonStat: Player statistics for the free and fast shooter Xonotic.">
    <meta name="author" content="Ant 'Antibody' Zucaro">

    <title>XonStat: Player Statistics for Xonotic</title>

    <link rel="shortcut icon" href="/static/favicon.ico">

    <%block name="css">
      <link href="/static/css/foundation.css" rel="stylesheet">
      <link href="/static/css/font-awesome.min.css" rel="stylesheet">
      <link href="/static/css/app.css" rel="stylesheet">
    </%block>

    <%block name="headjs">
      <script src="/static/js/vendor/modernizr.js"></script>
    </%block>
  </head>

  <body>
    <%block name="navigation">
      ${nav.nav("leaderboard")}
    </%block>

    <div class="row">
      <div class="small-1 large-12 columns" id="xonborder">
        <div id="title">
          <%block name="title"></%block>
        </div>

        ${self.body()}

      </div> <!-- /xonborder -->
    </div> <!-- /row -->

    ${footer.footer()}

    <%block name="js">
     <script type='text/javascript' src='//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'></script>
     <script src="/static/js/foundation.min.js"></script>
     <script>
       $(document).foundation();
     </script>
    </%block>

    <!-- RELATIVE TIME CONVERSION -->
    <script type="text/javascript">
    $('.abstime').each(function(i,e){
      var epoch = e.getAttribute('data-epoch');
      var d = new Date(0);
      d.setUTCSeconds(epoch);
      e.setAttribute('title', d.toDateString() + ' ' + d.toTimeString());  
    });
    </script>
  </body>
</html>
