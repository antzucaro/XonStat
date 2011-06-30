<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <title><%block name="title">XonStat - Player Statistics for Xonotic</%block></title>
        <%block name="css">
        <link rel="stylesheet" href="/static/css/style.css" type="text/css" media="screen" />
        <link rel="stylesheet" href="/static/css/tables.css" type="text/css" media="screen" />
        </%block>
    </head>
    <body>
		<div id="container"> 
			<header>
				<a href="/"><h1>Xonotic Game Statistics</h1></a>
				<h2>Xonotic is a fast-paced open-source GPL first person shooter</h2>
			</header>
			<div id="home" class="window"> 
				<h1 id="title">Player Statistics for Xonotic</h1> 
				<ul id="menu" class="nav clearfix">
					<li><a href="${request.route_url('main_index')}" title="Leaderboard">leaderboard</a></li>
					<li><a href="${request.route_url('player_index')}" title="Player Index">players</a></li>
					<li><a href="${request.route_url('game_index')}" title="Game Index">games</a></li>
					<li><a href="${request.route_url('map_index')}" title="Map Index">maps</a></li>
					<li class="last"><a href="${request.route_url('server_index')}" title="Server Index">servers</a></li>
				</ul>
				<div id="content" class="clearfix">
					${self.body()}
				</div> <!-- #home -->
			</div><!-- #content -->
			<div id="footer">
				<%block name="footer">
				<p>XonStat is a open source (GPLv2) project created by Antibody. Fork it <a href="https://github.com/antzucaro/XonStat" title="Go to the project page">on Github!</a></p>
				</%block>
			</div> <!-- #footer -->
		</div><!-- #container -->
        <%block name="js">
		<!-- production: <script src="//ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js"></script>
		<script>window.jQuery || document.write( '<script src="/static/js/scripts/jquery-1.6.1.min.js"><\/script>' )</script>-->
		<script src="/static/js/jquery-1.6.1.min.js"></script>
		<script src="/static/js/jquery.dataTables.min.js"></script>
		<script src="/static/js/default.js"></script>
        </%block>
    </body>
</html>
