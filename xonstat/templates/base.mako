<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
   <head>
      <title><%block name="title">XonStat - The Xonotic Statistics Database</%block></title>
	  <%block name="css">
      <link rel="stylesheet" href="/static/css/style.css" type="text/css" media="screen" />
      </%block>
	  <%block name="js"/>
   </head>
   <body>
      <div id="header">
         <%block name="header">
         <h1>XonStat</h1>
         <h2>The Statistics Database for Xonotic</h2>
         <br />
         </%block>
	  </div>

	  ${self.body()}

	  <div id="footer">
         <%block name="footer"/>
	  </div>
   </body>
</html>
