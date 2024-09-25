# Python 3 Simple Wiki

So you want a wiki? Install https://www.mediawiki.org/wiki/MediaWiki it is battle tested, it is the software behind wikipedia.org you get the joy of learning MariaDB and PHP and a httpd daemon, such as Apache.

But maybe you have further requirements?

* "*It is just for me, I love Markdown and I haven't found Markor for Android*": try https://en.wikipedia.org/wiki/TiddlyWiki 
* "*It has to be small, (but not as small as tiddlyWiki) but also reliable*": https://www.dokuwiki.org/dokuwiki - it's possibly the best wiki
* "*I **have** to run it behind nginx on linux but I do not trust databases and I absolutely refuse to let PHP anywhere near any of my servers! I lived through the Millennium and PHP is theWorst or PHP.is_the_best or mayBePHP(isn-t4U)?*"  

Then do we have an Open Source (MIT License) bundle for you at the low low price of <pre>$your_time</pre>: Python 3 Simple Wiki ([p3sw](https://gitlab.com/alexx_net/p3sw) - inspired by [wiki-in-a-flask](https://github.com/saucecode/wiki-in-a-flask), which, (unsurprisingly) is built upon [Flask](https://flask.palletsprojects.com/) using only 100% organic hand-milled Javascript, css, HTML in a beautifully indented python basket. [Seriously, pull request are **very** much open to additional refactoring.]

### Installation & verifying

	The full [install guide](wiki/INSTALL.md) is in the wiki... once you install it 😈
Clone or download this repo into /var/www/wiki to get started. (You can move it somewhere else, just remember to edit the .env file.)

Once you have `source .venv/bin/activate` you can verify the local install with `python p3sw.py`

### Introduction

The wiki pages are written in a [Markdown](https://en.wikipedia.org/wiki/Markdown) dialect, (with a pinch of opinio: __underlining__ is done with double underscores. &lt;zws&gt; and &lt;nbsp&gt; are accepted tags that are converted to HTML. The wiki runs behind nginx through gunicorn, and launched by SystemD.

p3sw has an built-in editor: a Web 1.0 <pre>form textarea</pre>, (the crowd goes "ooooh!" but unironically      as it's cool and retro, and **simple**, as is in the name of this wiki.)

Users can upload a limited range of files, and they are stored under their username.

Users are defined by a simple .htaccess file, or you can enable one global anonymous user for everyone. [So create your own Certificate Authority for TLS in nginx or use the excellent and free https://letsencrypt.org to reduce credential snooping.]

There is the *outline* of a search function that, (currently) only looks at file names in the first directory.

Topics can be kept separate with paths, that just map directly to the file system. This also enables there to be multiple files of the same name. Users can also have a home directory to store their ~~vanity~~ passion projects - but N.B. anyone with access to the wiki can edit any page... and those changes will be committed to a git log for posterity, (and so that later we can praise or rollback edits.)

### Future development

Currently some ideas are stored in the wiki as a [To Do](wiki/TODO.md) file.
