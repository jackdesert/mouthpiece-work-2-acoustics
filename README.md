Mouthpiece Work Yahoo Group
===========================

Once upon a time there was a yahoo group called "Mouthpiece Work".
This repo takes the archive from the group and displays it as html.

Build the Files
---------------

    git clone git@github.com:jackdesert/mouthpiece-work
    cd mouthpiece-work
    python -m venv env
    env/bin/activate
    pip install -r requirements.txt
    python run.py

Format
------

A yahoo group appears to be in the form of email messages.
This repo uses the plain text part of the email messages, and strings them
together as message threads.

Image references are available in the .warc file, but they point to a location
on yimg.com which does not appear to exist anymore.


How to Recover Yahoo Groups Messages
------------------------------------

https://datahorde.org/how-to-recover-your-yahoo-groups-from-the-internet-archive/

These two groups appear:

"MouthpieceWork",200,"RESTRICTED","ALL","UNMODERATED",03/13/2002,"False","us","Saxophone","https://groups.yahoo.com/neo/groups/MouthpieceWork/info","en-US",1600032198,"<div id=""ygrps-yiv-1063236641"">This is the only group dedicated to sharing information on woodwind mouthpiece making, repair and refacing.  The tools, techniques, materials, successes, failures can all be gathered at this location for future reference.  This is the place to learn about mouthpiece refacing!<br>\n<br>New visitors/members may want to check out the Files-Grouped Posts area first.  You can download, print and read the first 800 message posts to get up to speed.<br><br>\nAlso be sure to check out the extensive list of mouthpiece-related Links, Files and Photos.\n<br><br>For some basic &quot;kit&quot; information, see the Mouthpiece_Tools.xls file in the Files - Tools area of this site.<br><br>\nCheck out our spin-off site at: http://launch.groups.yahoo.com/group/MouthpieceWork2_Acoustics/<br><br>\nWelcome!   Keith Bradbury (aka MojoBari) - Moderator/Owner,"N/A","false","/Music/Instruments/Wind Instruments/Saxophone/","MouthpieceWork","SUBSCRIBERS","SUBSCRIBERS","false","ALL","Got a Mouthpiece Work question?  Send it to MouthpieceWork@yahoogroups.com\n\nVisit the site at http://groups.yahoo.com/group/MouthpieceWork to see the Files, Photos and Bookmarks relating to Mouthpiece Work.\n\nTo see and modify your groups, go to http://groups.yahoo.com/mygroups","Sax and Clarinet Mouthpiece Work",6282900,1662,"false","2020-02-23"

"MouthpieceWork2_Acoustics",200,"RESTRICTED","ALL","UNMODERATED",03/20/2010,"False","us","Saxophone","https://groups.yahoo.com/neo/groups/MouthpieceWork2_Acoustics/info","en-US",1600032198,"<div id=""ygrps-yiv-17195941"">This is a group dedicated to sharing information on sax mouthpiece acoustics and related experiments.  Discussions will also include saxophone acoustics in general since it is difficult to talk about mouthpieces without considering the entire system including the sax, reed and player.  If there is interest, other woodwinds may also be discussed.\n\nThis group is a spin-off from the well-established MouthpieceWork group.  That group will continue to focus more on woodwind mouthpiece making, repair and refacing.\n\nCheck out our original site at: http://launch.groups.yahoo.com/group/MouthpieceWork/\n\n\nWelcome! Keith Bradbury (aka MojoBari) - Moderator/Owner</div>","http://launch.groups.yahoo.com/group/MouthpieceWork/","false","/Music/Instruments/Wind Instruments/Saxophone/","MouthpieceWork2_Acoustics","SUBSCRIBERS","SUBSCRIBERS","false","ALL","N/A","Sax Mouthpiece Acoustic Science",44743559,78,"false","2020-08-06"


Now search for one of these:
https://archive.org/search?query=subject%3A%22yahoo+groups%22+MouthpieceWork
https://archive.org/search?query=subject%3A%22yahoo+groups%22+MouthpieceWork2_Acoustics

When the search completes, click on the search result and you will land on one of thse:

https://archive.org/details/yahoo-groups-2017-04-08T03-00-25Z-2632c7
https://archive.org/details/yahoo-groups-2018-08-03T05-31-58Z-92e929

Look for the "Web Archive GZ" on the right hand side


### Easy Version

These are the two files we want:
https://archive.org/download/yahoo-groups-2017-04-08T03-00-25Z-2632c7/mouthpiecework.UdewYP7.warc.gz
https://archive.org/download/yahoo-groups-2018-08-03T05-31-58Z-92e929/mouthpiecework2_acoustics.ylBYMHp.warc.gz

(Note these are also saved inside this repo in the /warc directory)


How to use .warc files
-----------------------

https://archive-it.org/post/the-stack-warc-file/


See repo mouthpiece-work-yahoo-group on


Deploying
---------

There are two remotes:
    - git@gitlab.com:jackdesert/mouthpiece-work
    - git@gitlab.com:jackdesert/mouthpiece-work-2-acoustics

I keep a single repository on my local machine, and deploy different
branches to the two remotes.

### Deploying mouthpiece-work

    git checkout main
    python run.py
    git add threads
    git commit -am'YOUR MESSAGE'
    git push origin HEAD

### Deploying mouthpiece-work-2-acoustics

    git checkout acoustics-no-merge
    git rebase main (This will cause conflicts...you can resolve by deleting threads directory)
    python run.py
    git add threads
    git commit -am'YOUR MESSAGE'
    git push acoustics HEAD


### Why Two Deployments

I did not see an easy way to get two github pages from a single repo.
So I use a single repo locally, but push to two different remotes.
Each remote is set up as a github page.


### How to see `git diff` without threads/ overpowering

Try: `git add threads`, then `git diff`
