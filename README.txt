This is XonStat, the application in front of xonstatdb. XonStat handles the submission of statistical information from the open source first person shooter Xonotic. 

To start, first run the following from the root directory to set up dependencies:

    python setup.py develop

Next you'll want to set up xonstatdb. This is maintained as a separate project here:

    https://github.com/antzucaro/xonstatdb

Next you'll want to open up development.ini and change a few things for added security. Chief among these is the "sqlalchemy.url" setting, which contains your username and password for the database. Change that match the new password you gave xonstat during the installation of xonstatdb. The other setting to change is "security.secret," which is used to keep your web session (cookies and such) secure. 

To start the server run the following from the root directory. I recommend running this within a GNU screen session:

    paster serve development.ini #(or production.ini if you've configured that settings file instead)

To get a Xonotic server configured to use this server, change the CVAR "g_playerstats_uri" to point to the correct host, port, and URL path. By default this is:

    http://localhost:6543/stats/submit

...so in the command line of the server (or in your config) you can put:

    set g_playerstats_uri http://localhost:6543/stats/submit

If you have any questions or issues please open up a bug report here, or - better yet ! - fork it and send me a pull request. 
