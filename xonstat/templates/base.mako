<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <title><%block name="title">XonStat - Player Statistics for Xonotic</%block></title>
        <%block name="css">
        <link rel="stylesheet" href="/static/css/normalize.css" type="text/css" media="screen" />
        <link rel="stylesheet" href="/static/css/style.css" type="text/css" media="screen" />
        </%block>
        <%block name="js">
        </%block>
    </head>
    <body>
        <div id="header">
            <%block name="header">
            <h1><a href="/" title="Home Page">XonStat</a></h1>
            <h3>Player Statistics for Xonotic</h3>
            </%block>
            <ul id="nav">
                <li><a href="/players" title="Player Index">players</a></li>
                <li><a href="/games" title="Game Index">games</a></li>
                <li><a href="/maps" title="Map Index">maps</a></li>
                <li><a href="" title="Server Index">servers</a></li>
            </ul>
        </div> <!-- END HEADER -->
        <div id="main">
            ${self.body()}
        </div> <!-- END MAIN -->
        <div id="footer">
            <%block name="footer">
            <p>XonStat is a open source (GPLv2) project created by Antibody. Fork it <a href="https://github.com/antzucaro/XonStat" title="Go to the project page">on Github!</a></p>
            </%block>
        </div> <!-- END FOOTER -->
    </body>
</html>
