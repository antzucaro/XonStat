This is **XonStat**, the application in front of [xonstatdb][xonstatdb].  
[XonStat][xonstat] handles the submission of statistical information from the open source first person shooter [Xonotic][xonotic].

----

To start, create a virtualenv and install dependencies:

    virtualenv env
    source env/bin/activate

From within the directory you've cloned the repo, install the dependencies:

    pip install -r requirements.txt

Next, install the application itself:

    pip install -e .

Next you'll want to set up [xonstatdb][xonstatdb]. This is maintained as a separate project here:

    https://github.com/antzucaro/xonstatdb

Next you'll want to open up development.ini and change a few things for added security.
Chief among these is the "sqlalchemy.url" setting, which contains your username and password for the database.
Change that match the new password you gave xonstat during the installation of xonstatdb.
The other setting to change is "session.secret," which is used to keep your web session (cookies and such) secure.

To start the server run the following from the root directory. I recommend running this within a GNU screen session:

    pserve --reload development.ini #(or production.ini if you've configured that settings file instead)

To get a Xonotic server configured to use this server, change the CVAR `g_playerstats_gamereport_uri` to point to the correct host, port, and URL path. By default this is:

    http://localhost:6543/stats/submit

...so in the server console (or in your config) you can put:

    set g_playerstats_gamereport_uri http://localhost:6543/stats/submit

If you have any questions or issues please open up a bug report here, or - better yet ! - fork it and send me a pull request.

[xonstatdb]: https://github.com/antzucaro/xonstatdb
[xonstat]: http://stats.xonotic.org/
[xonotic]: http://www.xonotic.org/

----

Project is licensed GPLv2+.
