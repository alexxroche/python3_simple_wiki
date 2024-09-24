## TODO

### List

3. Display history with a function that can parse `git log -p -- wiki/TODO.md` 
4. display when page was last edited
     - i. use git to list [["commit.committed_datetime","wiki_user","commit_hash","a_path"]]
     -  ii. then use the commit_hash + a_path to view the change
5. ability to rename a page
    - i. remember to rename all of the internal links `grep '(*Terms)' wiki/*|grep -v 'http'` as well
    - ii. can probably use git to do the rename! 
6. ability to delete a page
7. emoji   
7.1. ~~ enable emoji ~~ [you can paste them in]    
7.2. enable emoji :joy:   
8. anchors for footnotes
9. disable the "[Update]" button until some changes have happened
10. floating [edit] button so that it is always available on the left side of the screen
11. ~\~now~\~ inserts datetime
12. ~\~when~\~ inserts YYYY-Month-dd_HH:MM::SS
13. ~\~who~\~ inserts users signature
15. store local copy of page in local storage, so that if a race condition happens the changes aren't lost
16. [Preview] button to view without saving
18. re-enable Tab when edit box has focus
19. Create [Ctrl+Enter] to submit
20. Add "Toast" to indicate Update has happened
21. image creation rate limit   
22. drag-n-drop image upload   
23. page creation /  edit rate limit based on a dynamically generated trust level.
     - how old is the account
     - what is the distribution of [additions/modification/deletions] = changes, 
     - how many changes have been undone
     - account type [anon, anon+known_ip, user, Curator, Editor, Admin, root, owner{BDFL}]
25. Columized List `.column-list { columns: 100px;}` 
27. Use `os.path.join('./static/img/', spath)` in path_from_req 
28. {optional} per-user css (so that they can change the wiki to their taste)   
29. add id and class to every tag of the templates
30. add login &lt;= would no longer be simple
31. do we use git to track file uploads?
