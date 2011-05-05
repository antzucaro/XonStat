<html>
   <head>
      <title><%block name="title">XonStat - The Xonotic Statistics Database</%block></title>
	  <%block name="css"/>
	  <%block name="js"/>
   </head>
   <body>
      <div id="header">
         <%block name="header"/>
	  </div>

	  ${self.body()}

	  <div id="footer">
         <%block name="footer"/>
	  </div>
   </body>
</html>
