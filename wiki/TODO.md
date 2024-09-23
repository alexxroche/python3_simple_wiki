## TODO

### List

00. find the createArticle page path error
000. Do NOT display edit button in site-map
01. ~~ fix http://localhost:8787/wiki/Trading/URLs &gt; Detail link ~~
02. ~~ and http://localhost:8787/wiki/static/css/main.css &lt; Details ~~
03. ~~ add route /wiki/static~~ -&gt; /static [test if that enables users to create their own css?]
03. refactor (clean up)
04. ~~image upload~~
0002. Display history with a function that can parse `git log -p -- wiki/TODO.md` &lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt; you are HERE 
23. track when page was last edited
     - i. use git to list [["commit.committed_datetime","wiki_user","commit_hash","a_path"]]
     -  ii. then use the commit_hash + a_path to view the change
24. ability to rename a page
    - i. remember to rename all of the internal links `grep '(*Terms)' wiki/*|grep -v 'http'` as well
    - ii. can probably use git to do the rename! 
3. clean up guide   
3.1. File upload guide
4. publish to gitlab and github

5. emoji
5.1. ~~ enable emoji ~~ [you can paste them in] 
5.2. enable emoji :joy:
6. anchors for footnotes
19. disable the "[Update]" button until some changes have happened
17. ~~when clicking [Edit] {Option} scroll to the bottom of the page~~
20. floating [edit] button so that it is always available on the left side of the screen
12. ~\~now~\~ inserts datetime
13. ~\~when~\~ inserts YYYY-Month-dd_HH:MM::SS
14. ~\~who~\~ inserts users signature
25. store local copy of page in local storage, so that if a race condition happens the changes aren't lost
26. [Preview] button to view without saving
1. add login
8. re-enable Tab when edit box has focus
9. Create [Ctrl+Enter] to submit
10. Add "Toast" to indicate Update has happened
25. ~~with page reload and F5 warn if update could overwrite the existing page~~
     - ~~we can prevent this with javascript [Done: but doesn't disable the browser reload button]~~
     - and switch the editor1 form to submit using XHR
     - ~~ or do a redirect after submit (or manipulate the history to be "not a submit, just load the page")~~ &lt; not needed
12. ~~Convert existing &amp;​#8203; in the articles into '&#8203;'~~
14. image creation rate limit
13. page creation /  edit rate limit based on a dynamically generated trust level.
     - how old is the account
     - what is the distribution of [additions/modification/deletions] = changes, 
     - how many changes have been undone
     - account type [anon, anon+known_ip, user, Curator, Editor, Admin, root, owner{BDFL}]
15. Columized List `.column-list { columns: 100px;}` 
17. Use `os.path.join('./static/img/', spath)` in path_from_req 
18. {optional} per-user css (so that they can change the wiki to their taste)   
31.1. add id and class to every tag of the templates
