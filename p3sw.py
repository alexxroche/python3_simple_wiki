"""
    "python 3 simple wiki"
    p3sw.py
    ver.  2024-Sep-17T13:52:06
    RDFa:derived_from="wiki-in-a-flask.py"
    RDFa:deps="[python3 venv pip]"
    # Copyright 2024 alexx, MIT License
    Motivation: I just need a small wiki for a small team and
         don't want to install PHP.
        Tried Moin2 and it wasn't ready.
"""

from os import listdir, mkdir, makedirs  # , walk
from os.path import dirname, exists, isdir, isfile, join, realpath
import sys
import mimetypes
import base64
import re
import errno
from subprocess import Popen, PIPE
from configparser import ConfigParser as cfg_parse
from configparser import ExtendedInterpolation as ei
from collections import Counter
from git import Repo
from flask import Flask, request, Response, abort, render_template_string

# for image upload
from flask import flash, jsonify, make_response, redirect, send_from_directory, url_for

import markdown as MD
from flask_ckeditor.utils import cleanify
from pathvalidate import sanitize_filepath
from werkzeug.utils import secure_filename

# The configuration file.
CFG = ".env"

# turns out the interpolation can be helpful
cfg = cfg_parse(delimiters="=", interpolation=ei())
# cfg = cfg_parse(delimiters=('='), interpolation=None)
### interpolation=None lets us have '%' in our strings
###  without having to escape them as '%%'
# cfg._interpolation = ei()
if exists(CFG):
    # cfg.read_file(open(CFG, encoding="utf-8"))
    with open(CFG, encoding="utf-8") as cfg_ini:
        cfg.read_file(cfg_ini)
else:
    print(f"[err] unable to locate {CFG} INI file")
    sys.exit(1)

# wiki_uri
wu = cfg.get("g", "wu", fallback="/wiki")
# wiki_path
wp = cfg.get("g", "wp", fallback="." + wu)

# limit upload file types
allowed_extensions = cfg.get(
    "g", "allowed_extensions", fallback='{"png", "jpg", "jpeg", "gif", "webp"}'
)
# new_line for f-strings
NEW_LINE = "\n"

app = Flask(__name__, static_url_path="")

# Limit file upload size
max_upload_filesize = cfg.getint("g", "max_upload_size", fallback=int(16000000))
app.config["MAX_CONTENT_LENGTH"] = max_upload_filesize
app.secret_key = cfg.get(
    "g", "secret_key", fallback="NpI5CwDVaYhY-fzBifR-9mCSok-wiVMzpRwXO"
)
# app.config['SESSION_TYPE'] = 'filesystem'

""" if you want to enable anonymous edits then set a global username in .env """
global_user: str = cfg.get("g", "global_user")


def make_dir(path, mode=0o755, flag=None):
    """if flag is set then we only make one additional depth or return failure
    # if mode is '0755' string then we turn it into 0o755 oct int
    # if mode is 0o755 then we use it natively
    #
    # why? becuase "do what I mean" and "be obvious" REQUIRE mkdir('~/var/example/', 0755)
    # to set 0755 and not 1341
    """
    try:
        if flag and flag is not None:
            # fail if parent does not exist
            mkdir(path, mode=mode)
        else:
            makedirs(path, mode=mode)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and isdir(path):
            pass
        else:
            raise


def guess_mimetype(guess: str) -> str:
    """E731 Do not assign a `lambda` expression, use a `def`"""
    return mimetypes.guess_type(guess)[0] or "application/octet-stream"


def load_file(fname: str) -> str:
    """load file from disk into a string"""
    if isfile(fname):
        with open(fname, "r", encoding="utf-8") as file:
            return file.read()
    return ""


def load_resource(fname: str) -> str:
    """load file from disk into a binary"""
    if isfile(fname):
        with open(fname, "rb") as file:
            return file.read()
    return ""


def esc_s(this_str: str = "") -> str:
    """used to obfuscate the strike escape while we are implementing strike"""
    return this_str.replace(r"~\~", r"<del_esc>")


def s_esc(this_str: str = "") -> str:
    """esc_s backwards"""
    return this_str.replace(r"<del_esc>", r"~\~")


def add_strikethrough(text_to_strike: str = "") -> str:
    """expects a string that may (or may not) have ~~strike~~"""
    # We also find escaped version (with a backslash between the tildas
    # and turn it into '~~'
    if r"~~" in text_to_strike:
        count = 0
        loop_break = 0
        while r"~~" in text_to_strike:
            # if we have '~\~~~' do NOT match the trailing tilda in ~\~
            text_to_strike = esc_s(text_to_strike)
            where_s: int = text_to_strike.find(r"~~")
            s_tag = r"<s>"
            if count == 1:
                s_tag = r"</s>"
            text_to_strike = (
                text_to_strike[:where_s] + s_tag + text_to_strike[where_s + 2 :]
            )
            count += 1
            loop_break += 1
            if count > 1:
                count = 0
            if loop_break >= 500:
                return s_esc(text_to_strike)
    return s_esc(text_to_strike)


def esc_strikethrough(text_to_esc: str = "") -> str:
    """escape strikethrough"""
    while r"~\~" in text_to_esc:
        s_tag = r"~~"
        where_s_esc: int = text_to_esc.find(r"~\~")
        text_to_esc = text_to_esc[:where_s_esc] + s_tag + text_to_esc[where_s_esc + 3 :]
    return text_to_esc


def esc_u(this_str: str = "") -> str:
    """used to obfuscate the underline escape while we are implementing strike"""
    if r"_\_" in this_str:
        return this_str.replace(r"_\_", r"<esc_u>")
    return this_str


def u_esc(this_str: str = "") -> str:
    """esc_u backwards"""
    # return this_str.replace(r"<esc_u>", r"_\_")
    return this_str.replace(r"<esc_u>", r"_\_")


def add_underline(text_to_underline: str = "") -> str:
    """expects a string that may (or may not) have '__underline__'"""
    # We also find '_\___' as the escaped verion and turn it into '__'
    #    TO-DO : check for uneven pairs of underline
    text_to_underline = esc_u(text_to_underline)
    if r"__" in text_to_underline:
        count = 0
        loop_break = 0
        while r"__" in text_to_underline:
            # if we have '_\___'  do NOT match the trailing underscore in _\_
            where_u: int = text_to_underline.find(r"__")
            u_tag = r"<u>"
            if count == 1:
                u_tag = r"</u>"
            text_to_underline = (
                text_to_underline[:where_u] + u_tag + text_to_underline[where_u + 2 :]
            )
            count += 1
            loop_break += 1
            if count > 1:
                count = 0
            if loop_break >= 500:
                # where_u_lost: int = text_to_underline.find(r"__")
                # app.logger.info("[w:u_lost] found unproccessed __ at %s", where_u_lost)
                return text_to_underline
        if count == 1:
            where_u_unmatched: int = text_to_underline.find(r"__")
            app.logger.info("[w:add_u] unmatched underline found %s", where_u_unmatched)
    return text_to_underline


def esc_nbsp(this_str: str = "") -> str:
    """enables nbsp through rendering"""
    return this_str.replace(r"&nbsp;", r"<nbsp>")


def nbsp_esc(this_str: str = "") -> str:
    """esc_nbsp backwards"""
    return this_str.replace(r"<nbsp>", r"&nbsp;")


def esc_zws(this_str: str = "") -> str:
    """zws_esc : can be used to escape"""
    # if r"<zws>" in this_str:
    #    app.logger.info(f'[d:zws_e] found esced zws DONE')
    # elif r"&#8203;" in this_str:
    #    app.logger.info(f'[d:zws_e] found zws to esc')
    return this_str.replace(r"&#8203;", r"<zws>")


def zws_unesc(this_str: str = "") -> str:
    """zws_unesc, needs itself to be escaped"""
    # if r"<zws>" in this_str:
    #    app.logger.info(f'[d:e_zws] found esced zws')
    # elif r"&#8203;" in this_str:
    #    app.logger.info(f'[d:e_zws] found zws ALREADY')
    return this_str.replace(r"<zws>", r"&#8203;")


# def nbsp_esc_l(this_str: list = "") -> list:
#    """esc_u backwards"""
#    ret = []
#    for line in this_str:
#        ret.append(line.decode().replace(r"<nbsp>", r"&nbsp;").encode("utf-8"))
#    return ret


def render_markdown(mdown: str) -> str:
    """render markdown, now with formatting escape that should probably be processed by Rust"""
    aul = add_underline(esc_nbsp(esc_zws(mdown)))
    # app.logger.info('[rmd] %s', aul)
    tmd = MD.markdown(aul, extensions=["markdown.extensions.tables"])
    struk = add_strikethrough(tmd)
    return struk
    # return add_strikethrough(
    #    MD.markdown(
    #        add_underline(esc_u(esc_nbsp(esc_zws(mdown)))),
    #        extensions=["markdown.extensions.tables"]
    #    )
    # )


def path_from_req(spath: str = None, article: str = None) -> str:
    """create file_path from spath & article"""
    spath += r"/"
    if article is None or article == "":
        article = cfg.get("g", "splash", fallback="/splash")
        # app.logger.info("[d:pfr] NOT ART: so spath: %s; art: %s", spath, article)
        article_file = article  # + '.md'
        # app.logger.info("[d:pfr] RETURNIUNG : .%s%s", spath, article_file)
        return "." + spath + article_file

    if spath.startswith(r"/") or wp.endswith(r"/"):
        spath = wp + spath + "/"
    else:
        spath = wp + "/" + spath + "/"
    # spath = spath.replace('//', '/') #dirty hack
    if not spath.startswith(r"/") and not spath.startswith(r"./"):
        spath = r"./" + spath
    elif spath.startswith(r"/"):
        spath = r"." + spath
    # app.logger.info("[d:pfr] spath: {spath}; art: %s", article)
    return f"{spath}{article}"


def uri_from_req(spath: str = None, article: str = None) -> str:
    """create file_path from spath & article"""
    # if article is not None and not spath.startswith(wu):
    #    app.logger.info("[d:ufr] spath before: %s (%s)", spath, wu)
    if spath.endswith(r"/"):
        if spath.startswith(r"/") or wu.endswith(r"/"):
            spath = wu + spath
        else:
            spath = wu + "/" + spath
    else:
        if spath.startswith(r"/") or wu.endswith(r"/"):
            spath = wu + spath
        else:
            if spath and spath != "":
                spath = wu + "/" + spath + r"/"
            else:
                spath = wu + r"/"
    return f"{spath}{article}"


def parse_x(req_str: str) -> tuple[str, str, str, str]:
    """find useful headers from the request"""
    u_agent = req_str.headers.get("User-Agent")
    auth_str = req_str.headers.get("Authorization")
    username = ""
    hxr_ip = req_str.remote_addr
    if "HTTP_X_FORWARDED_FOR" in req_str.environ:
        hxr_ip = req_str.environ["HTTP_X_FORWARDED_FOR"]
    if auth_str and auth_str is not None:
        decoded_string = base64.b64decode(auth_str[6:]).decode()
        username = str(decoded_string).split(":", maxsplit=1)[0]
    elif "global_user" in globals():
        username = global_user
    return (u_agent, username, hxr_ip, auth_str)


# def gitdun(user: str) -> str | bool: # python 3.11.2
def gitdun(user: str):  # python 3.9.18
    """use git to track the wiki history
    user can be a usename or a remote ip address"""
    # TO-DO: check that git exists
    # TO-DO: check a repo has been initalised
    if user and user is not None:
        git_cmd = f'$(which git) add wiki splash.md; git commit -m "{user}"'
        return Popen(git_cmd, shell=True, stdout=PIPE).stdout.read()
    return False


def read_template() -> str:
    """fetch the template
    TO-DO merge this with load_resource"""
    template_file: str = cfg.get("g", "template_file", fallback="./template.html")
    if exists(template_file):
        with open(template_file, "r", encoding="utf-8") as file:
            return file.read()
    return ""


def is_exists(repo, filename, sha):
    """Check if a file in current commit exist.
    RDFa:src="https://stackoverflow.com/a/55659674/1153645" """
    # cwd = os.path.dirname(os.path.realpath(sys.argv[0]))
    # app.logger.info(f'[d:is_exists] {repo} ; {filename}; {sha};')
    files = repo.git.show("--pretty=", "--name-only", str(sha))
    if filename in files:
        return True
    return False


def get_file_commits(filename):
    """RDFa:src="https://stackoverflow.com/a/55659674/1153645" """
    file_commits = []
    cwd = dirname(realpath(sys.argv[0]))
    repo = Repo(cwd)
    # tree = repo.head.commit.tree
    # commits = list(repo.iter_commits("main", max_count=5))
    filename = filename.replace("history", "wiki", 1) + ".md"
    # app.logger.info(f'[d] listing all changes to {filename} in {repo}')
    commits = repo.iter_commits(all=True, max_count=100, paths=f"{filename}")
    for commit in list(commits):
        # if is_exists(repo, filename, commit.hexsha):
        if is_exists(repo, filename, commit):
            # file_commits.append(commit)
            # file_commits.append(f'{commit.__dir__()}')
            # file_commits.append({f'{commit.message}': f'{commit.diff}'})
            # app.logger.info(f'[d] FOR {commit}')
            # total_stats = commit.stats.total
            # total_files = commit.stats.files
            cmt_hash = str(commit)
            # diffs = repo.index.diff(f'{cmt_hash}..{cmt_hash}~1', create_patch=True)
            diffs = repo.index.diff(f"{cmt_hash}^1", create_patch=True)
            # diffs = repo.index.diff(f'{str(commit)}^1..', create_patch=True)
            # diffs = commit.diff(create_patch=True)
            # diffs = repo.index.diff(commit, create_patch=False)
            # patch = "Larry Wall"
            # patch = repo.index.diff(commit, patch = True)

            wiki_user = ""
            commit_name = Counter(map(str.lower, (commit.message).split()))
            if len(commit_name) == 1:
                wiki_user = commit.message.rstrip()
            for diff in diffs:
                # new line: nwl
                nwl = "\n"
                if diff.a_path == filename:
                    # diff_ascii =str(d.diff).replace('\\n',"<br>\n")
                    # backslash = "\\"
                    # backward_slash = r"\u005C"  # .encode('utf-8')
                    diff_str = (
                        diff.diff.decode("utf-8")
                        .encode("utf-8")
                        .decode("unicode_escape")
                        .replace(nwl, "<br>")
                    )
                    # diff_ascii = d.diff.decode('utf-8').replace(nwl,"<br>" + nwl)
                    ##diff_ascii = d.diff.decode('unicode_escape').replace(nwl,"<br>")
                    # diff_ascii = re.sub(r'\\', f'{backslash}', diff_str)
                    diff_ascii = re.sub(r"\\", r"&#92;", diff_str)
                    ##diff_ascii = re.sub(r'\\', f'{backward_slash}', diff_str)
                    file_commits.append(
                        {
                            f"{wiki_user}": [
                                f"{diff.a_path}",
                                f"{commit.committed_datetime}",
                                f"<pre>{diff_ascii}{nwl}</pre><br>",
                            ]
                        }
                    )  # works
            #   #file_commits.append(diff.a_path)
            #   #file_commits.append({diff.a_path: f'{d.__dict__.keys()}'})
            #   file_commits.append({d.a_path: f'{d.__dir__()}'})

    # return f'<body><pre>{file_commits}</pre>'
    return f"<body>{file_commits}"


@app.route("/")
def index_page() -> str:
    """index_page"""
    # index_file: str = c['g']['index_file']
    index_file: str = cfg.get("g", "index_file", fallback="./index.html")
    if exists(index_file):
        index_html = load_resource(index_file).decode()
        return render_template_string(
            index_html,
            pagetext=cfg.get(
                "g",
                "index_page_text",
                fallback="p3sw is running! <a href='/wiki/'>Click here to enter the wiki.</a>",
            ),
        )
    return f"<h1> MISSING {index_file} </h1><a href='/wiki/'>Enter Wiki</a>"


@app.route("/static/<fname>")
@app.route("/wiki/static/<fname>")
@app.route("/static/<path:spath>/<fname>")
@app.route("/wiki/static/<path:spath>/<fname>")
def get_static_resource(spath="", fname=None):
    """static route, for images, css and javascript"""
    # app.logger.info(f'[d:static] {spath}; file: {fname}')
    if not fname:
        return abort(404)
    static = cfg.get("g", "static", fallback="./static/")
    file_path = static
    if spath:
        file_path += spath + "/"
    file_path += fname
    (_, username, _, _) = parse_x(request)
    if isfile(file_path):
        with open(file_path, "rb") as file:
            return Response(file.read(), mimetype=guess_mimetype(fname))
    elif file_path.startswith(join(static, "img", username)):
        dir_ls = list_files(file_path)
        if dir_ls != "":
            return render_template_string(read_template(), contenthtml=dir_ls)
        return ""
    else:
        return "No peeking!"


@app.route("/wiki/history/<path:spath>")
def history_show(spath=None):
    """history_show rather than show_history because routes were
    being selected alphabetically or something??
    """
    if not spath:
        return abort(404)
    file_path = request.path[6:]
    file_path = sanitize_filepath(file_path)
    return get_file_commits(file_path)


@app.route("/wiki/site_map/")
@app.route("/wiki/site-map/")
@app.route("/wiki/site-map/<path:subdir>")
def site_map(subdir=None):
    """to-do: ls subdir and create cont_html (no edit)"""
    this_uri = wu
    if subdir is not None:
        this_uri = join(wu, subdir)
    if subdir is None:
        subdir = ""
    #    subdir = wu
    template_html = read_template()
    these_files = []
    these_dirs = []
    this_path = r"." + this_uri + "/"
    #
    # TO-DO: refactor this into list_files(str(this_path))
    #
    for f in listdir(str(this_path)):
        ff = join(this_path, f)
        if isdir(ff):
            these_dirs.append(f)
        else:
            these_files.append(f)
    cont_html = f" Listing: /{subdir.replace('/wiki', '')}"
    for this_dir in these_dirs:
        # cont_html += '<li class="isDir"> → &nbsp; <a href="'
        # conf_html += os.path.join(subdir, this_dir) + '">' + this_dir + "</a></li>"
        cont_html += (
            '<li class="isDir"> → &nbsp; <a href="/wiki/site-map/'
            + join(subdir, this_dir)
            + '">'
            + this_dir
            + "</a></li>"
        )
    for this_file in these_files:
        if this_file.endswith("_Detail.md"):
            continue
        f_name = re.sub(".md$", "", this_file)
        cont_html += (
            '<li class="isFile"> <a href="'
            + join(this_uri, f_name)
            + '">'
            + f_name
            + "</a></li>"
        )
    (_, username, _, _) = parse_x(request)
    return render_template_string(
        template_html,
        title="Site Map",
        username=username,
        no_edit=True,
        user_ip="10.10.10.57",
        auth_str="Site-Map:has_no_user_and_can_not_be_edited",
        content_txt="",
        contenthtml=cont_html,
    )


# @app.route("/wiki/<article>/md") # viewArticle is grabbing this!
@app.route("/wiki/md/")
@app.route("/wiki/raw/<article>")
@app.route("/wiki/<article>/md")
# Flask does not match http://localhost:8787/wiki/ISO_8601/md
@app.route("/wiki/md/<article>")
@app.route("/wiki/raw/<path:subpath>/<article>")
@app.route("/wiki/md/<path:subpath>/<article>")
# @app.route("/wiki/raw/<path:subpath>/<article>", defaults={"subpath": ""})
def view_art_md(subpath="", article=None) -> Response:
    # def avmd(subpath="", article=None) -> Response:
    # seeing if a short function name would encouarage Flask to prioritize this route
    """view Article as raw Markdown"""
    # app.logger.info(
    #    "[START:d:MD] wp: %s; subpath: %s, + article: %s:|",
    #    wp, subpath, article
    # )
    file_path: str = ""
    if not article:
        # file_path = r'./splash.md'
        # file_path = r'./' + cfg.get("g", "splash", fallback="splash") + r'.md'
        # file_path = path_from_req(subpath,"")
        file_path = path_from_req("", "") + r".md"
        #  If you want to disable viewing
        # raw md of splash.md then just:
        #  return abort(404)
        # and you can REM the /wiki/md/ route above
    else:
        file_path = path_from_req(subpath, article) + r".md"
    # file_path = request.path[6:]
    # file_path = sanitize_filepath(file_path)
    # if file_path.startswith("md"):
    #    file_path = file_path[3:]
    # elif file_path.startswith("raw"):
    #    file_path = file_path[4:]
    # if not os.path.exists(wp + file_path + ".md"):
    if not exists(file_path):
        # create missing page
        cmp_str = cfg.get(
            "g",
            "create_missing_page",
            fallback="<a href='/wiki/createpage/%s'>Click to create page!</a>",
        )
        # app.logger.info(
        #   "[d:MD] wp: %s; subpath: %s, + article: %s = file_path: %s",
        #   wp, subpath, article, file_path)
        return cmp_str % file_path
    # with open(wp + file_path + ".md", "r", encoding="utf-8") as file:
    with open(file_path, "r", encoding="utf-8") as file:
        return Response(file.read(), mimetype="text/plain")


# def create_article(path=None, article=None):
# @app.route("/wiki/createpage/<path:spath>/<article>", defaults={"spath": ""})
@app.route("/wiki/createpage/<article>")
@app.route("/wiki/createpage/<path:spath>/<article>")
def create_article(spath="", article=None):
    """create a new page
    TO-DO: create new subdirs when needed"""
    (_, username, _, _) = parse_x(request)
    if not article or username == "" or username is None:
        return abort(404)
    file_path = request.path[17:].strip("/")
    if spath not in file_path:
        return abort(404)
    if exists(wp + file_path + ".md"):
        rt_err = cfg.get(
            "g",
            "page_already_exists",
            fallback="<a href='/wiki/%s'>Already exists!</a>",
        )
        return rt_err % file_path
    spath = "/" + spath + "/"
    spath = spath.replace("//", "/")  # Dirty hack to clean up broken code
    if not exists(wp + spath):
        # app.logger.info("[d:cp] creating %s%s;", wp, spath)
        make_dir(wp + spath)

    # app.logger.info(f"[d:cp] creating {wp}{spath}{article}.md;")
    with open(wp + spath + article + ".md", "w", encoding="utf-8") as file:
        file.write(article.replace("_", " ") + "\n=======")

    gitdun(username)
    rt_str = cfg.get(
        "g", "article_created", fallback="<a href='/wiki/%s'>Article created.</a>"
    )
    return rt_str % file_path


@app.route("/wiki/search/<query>")
def search_wiki_path(query=None):
    """we should have the route below redirect here
    /wiki/search/ISO_8601"""
    if query is not None:
        clean_query = query.replace(" ", "_")
        files = [x for x in listdir("./wiki/") if not x.endswith("_Detail.md")]
        results = [
            '<a href="/wiki/' + x[:-3] + '">' + x[:-3].replace("_", " ") + "</a>"
            for x in files
            if clean_query.lower() in x.lower()
        ]
        return render_template_string(
            read_template(),
            contenthtml=cfg.get(
                "g", "found_results", fallback="Found %i result(s)!<br/>"
            )
            % len(results)
            + "<br/>".join(results),
        )
    return render_template_string(
        read_template(),
        contenthtml=cfg.get(
            "g",
            "search_index",
            fallback="<h2>Search me!</h2><br/> TO-DO: [add a search box]",
        ),
    )


@app.route("/wiki/search/")
def search_wiki():
    """/wiki/search/?query=ISO_8601"""
    query = request.args.get("query")
    if query is not None:
        clean_query = query.replace(" ", "_")
        files = [x for x in listdir("./wiki/") if not x.endswith("_Detail.md")]
        results = [
            '<a href="/wiki/'
            + x.replace(".md", "")
            + '">'
            + x.replace(".md", "").replace("_", " ")
            + "</a>"
            for x in files
            if clean_query.lower() in x.lower()
        ]
        ret_str = f"Found {len(results)} result(s): <br/>"
        return render_template_string(
            read_template(), contenthtml=ret_str + "".join(results)
        )
    return render_template_string(
        read_template(),
        contenthtml=cfg.get(
            "g",
            "search_term_missing",
            fallback="Your search seems a little too broad!<br/>TO-DO:",
        ),
    )


@app.route("/wiki/", methods=["GET", "POST"])
@app.route("/wiki/<article>", methods=["GET", "POST"])
@app.route("/wiki/<path:spath>/<article>", methods=["GET", "POST"])
def view_this_article(spath="", article=None):
    """view_article: was being greedy and catching /wiki/example/md
    , so  we tried lengthening the function name
    """
    # file_path = request.path[6:]
    file_path = None
    # req_path = request.path[6:]
    this_uri = None
    title = ""
    detail_uri = ""
    if not article:
        title = cfg.get("g", "splash_title", fallback="Wiki Index")
        file_path = path_from_req("", "")
        this_uri = uri_from_req("", "")
        # app.logger.info(
        #    "[i:582] NO ART: spath: %s, + article: %s = file_path: %s ;; %s",
        #    spath, article, file_path, this_uri
        # )
    else:
        # if type(article) is tuple:
        if isinstance(article, tuple):
            # app.logger.info("[i:595] %s is a list", article)
            title = (article[0].replace("_", " "),)
            # app.logger.info("[i:596] %s from article", title)
        else:
            # app.logger.info(
            #    "[i:598] %s/%s '%s' '%s' from %s",
            #     spath, type(article), article, title, article)
            title = article.replace("_", " ")
            # app.logger.info("[i:600] '%s' now %s", title, article)
        file_path = path_from_req(spath, article)
        this_uri = uri_from_req(spath, article)
        detail_uri = join(spath, article)
    (_, username, hxr_ip, _) = parse_x(request)
    if request.method == "POST" and username is not None:
        data = request.form.get("editor1")
        if data and data is not None:
            # [Errno 2] No such file or directory: './wiki/site-map//Example.md'
            this_path = file_path.replace("//", "/")
            # TO-DO: remove this ^ Dirty hack to clean up broken code
            with open(this_path + ".md", "w", encoding="utf-8") as file:
                file.write(cleanify(nbsp_esc(zws_unesc(data))))
        gitdun(username)
    if not exists(file_path + ".md"):
        return_str = cfg.get(
            "g",
            "create_missing_page",
            fallback='<a href="' + wu + '/createpage/%s">Create!</a>',
        )
        return return_str % join(spath, article)
    detailhtml = ""
    mdown = ""
    parent_uri = None
    if this_uri.endswith("_Detail"):
        parent_uri = re.sub("_Detail$", "", this_uri)
    else:
        if exists(file_path + "_Detail.md"):
            detailhtml = render_markdown(
                # load_resource(spath + article + "_Detail.md").decode()
                load_resource(file_path + "_Detail.md").decode()
            )
    # with open(spath + article + ".md", "r", encoding="utf-8") as file:
    navigation_file: str = "navigation.html"
    navigation_stub: str = load_file(navigation_file)
    with open(file_path + ".md", "r", encoding="utf-8") as file:
        mdown = file.read()
    rts_args = {
        # "user_agent": u_agent,
        "parent_uri": parent_uri,
        "file_path": file_path,
        # "detail_uri": detail_uri,
        "detail_uri": detail_uri,
        "username": username,
        "navigation_stub": navigation_stub,
        "user_ip": hxr_ip,
        # "auth_str": auth_str,
        "title": title,
        "content_txt": esc_zws(esc_nbsp(mdown)),
        #'contenthtml':esc_u(zws_unesc(nbsp_esc(esc_strikethrough(render_markdown(mdown))))),
        "contenthtml": u_esc(
            zws_unesc(nbsp_esc(esc_strikethrough(render_markdown(esc_u(mdown)))))
        ),
        "detailhtml": detailhtml,
    }
    # if req_path == "":
    if article is None:  # or article == "splash":
        # we don't offer a _Details page for the splash page
        # app.logger.info("[REQ p] %s", req_path)
        del rts_args["parent_uri"]
    # else:
    #    rts_args["parent_uri"] = f'[{article}]'
    # return render_template_string(template_html, **rts_args)
    return render_template_string(read_template(), **rts_args)


@app.errorhandler(413)
def too_large(err):
    """if the uploaded file is too large"""
    err_msg = (
        "File is too large: "
        + str(err)
        + ". Current limit is: "
        + str(app.config["MAX_CONTENT_LENGTH"])
    )
    return make_response(jsonify(message=err_msg), 413)


def allowed_file(filename):
    """limit file uploads to those with allowed_extensions"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def list_files(dir_path: str = None):
    """list_files"""
    # template_html = read_template()
    these_files = []
    these_dirs = []
    if dir_path is None:
        return ""
    if not isdir(dir_path):
        return ""
        # return f"{dir_path} not found"
    # max_depth = 1 # no peeking deeper into the tree
    # for dirpath, dirnames, filenames in walk(this_path):
    #    if dirpath.count(sep) - this_path.count(sep) == max_depth - 1:
    #    if dirpath[len(this_path):].count(sep) == max_depth:
    #        these_files.extend(filenames)
    #        these_dirs.extend(dirnames)
    for f in listdir(str(dir_path)):
        ff = join(dir_path, f)
        if isdir(ff):
            these_dirs.append(f)
        else:
            these_files.append(f)
    dir_uri = re.sub("^/?.?/wiki", "", dir_path)
    # cont_html = f" Listing: /{subdir.replace('/wiki', '')}"
    cont_html = f" Listing: {re.sub('^.?', '', dir_path)}"
    for this_dir in these_dirs:
        cont_html += (
            '<li class="isDir"> → &nbsp; <a href="/'
            + join(dir_path, this_dir)
            + '">'
            + this_dir
            + "</a></li>"
        )
    for this_file in these_files:
        if this_file.endswith("_Detail.md"):
            continue
        f_name = re.sub(".md$", "", this_file)
        cont_html += (
            '<li class="isFile"> <a href="/'
            + join(re.sub(r"/upload/", r"/", dir_uri, count=1), f_name)
            + '">'
            + f_name
            + "</a></li>"
        )
    return cont_html


@app.route("/wiki/upload/<name>")
@app.route("/wiki/upload/<name>/")
def show_uploads(spath=None, name=None):
    """by default we don't do this, for security;
    but maybe you have some other need
    """
    (_, username, _, _) = parse_x(request)
    if username and username != "" and username == name:
        return f"TODO: a list of the files in /static/img/{username}/ {spath}"
    if username and username != "":
        static = cfg.get("g", "static", fallback="./static/")
        dir_ls = list_files(join(static, "img", username))
        if dir_ls != "":
            return render_template_string(read_template(), contenthtml=dir_ls)
        return render_template_string(
            read_template(),
            contenthtml="""
            No files found. You could <a href="/wiki/upload">upload</a>
             some, if you have a need.
            """,
        )
    return "Just because you look does not mean that you will see."


@app.route("/wiki/upload/<path:spath>/<name>")
def download_file(spath=None, name=None):
    """let users view files"""
    # TO-DO actually display a "Success: you uploaded [file_type] and
    # can now link it within the wiki with ![alt](/static/img/{user}/filename)
    # If users upload more than 65536 files, it is left to you to divide
    #   them into /static/img/{user}/f/i/l/filename.jpg
    # If you have more then 65536 users, it is left to you to divide them
    #   into /static/img/u/s/e/{user}/filename.jpg
    # 2 bonus internet points if you do both and send a pull request
    file_path = join("static/img/", spath)
    # app.logger.info(f"[d] showing img from {file_path}")
    if name is not None and name != "":
        return send_from_directory(file_path, name)
    return "Did you typo that URL? ALWAYS cut-n-paste!"


@app.route("/wiki/upload", methods=["GET", "POST"])
@app.route("/wiki/upload/", methods=["GET", "POST"])
def upload_file():
    """let your users fill your diskspace :facepalm:"""
    (_, username, _, _) = parse_x(request)
    static = cfg.get("g", "static", fallback="static")
    if static and not static.endswith(r"/"):
        static = static + r"/"
    # upload_folder = r'./' + static + 'img/%s' % username
    upload_folder = static + f"img/{username}"
    if request.method == "POST":
        # app.logger.info(f'[d:HERE] {request.__dict__}')
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            app.logger.info("[i] %s tried to upload without selecting a file", username)
            return redirect(request.url)
        # TO-DO: check the file hasn't already been uploaded!
        # TO-DO: ask if they want to replace the existing file?
        if file and allowed_file(file.filename):
            make_dir(upload_folder)
            filename = secure_filename(file.filename)
            try:
                # file.save(os.path.join(app.config['upload_folder'], filename))
                file.save(join(upload_folder, filename))
            except OSError as err:
                return f"Error saving file: {str(err)}", 500
            # app.logger.info(f'[upload done?] name= {username} - {filename}')
            # return redirect(url_for('download_file', name= username + '/' + filename))
            return redirect(url_for("download_file", spath=username, name=filename))
        if file and not allowed_file(file.filename):
            return f"""<pre>{NEW_LINE}
                    Only the follow file types may currently be uploaded: {allowed_extensions}
                    Please go back and try a differnt file.</pre>"""
    static = cfg.get("g", "static", fallback="./static/")
    dir_ls = list_files(join(static, "img", username))
    upload_template = load_file("upload.html")
    upload_html = render_template_string(upload_template, dir_ls=dir_ls)
    return render_template_string(
        read_template(),
        title="Upload a new File",
        username=username,
        no_edit=True,
        dir_ls=dir_ls,
        contenthtml=upload_html,
        # TO-DO: this V should be in .env
        detailhtml="""
    <h1> <=====<<  Upload a new File</h1>
    <h3>Over there Click the <input type="file" disabled id="up_bb" class="btn_p ggb_prompt"> button, to select a file; then click <span id="up_ub" class="btn_p b_prompt"> &nbsp;Upload </span>&nbsp;to ...</h3>
    """,
    )


if __name__ == "__main__":
    FLASK_RUN_HOST = cfg.get("g", "host", fallback="localhost")
    FLASK_RUN_PORT = cfg.getint("g", "port", fallback=8787)
    FLASK_DEBUG = cfg.getboolean("g", "debug", fallback=True)
    # print(f'[d] launching {FLASK_RUN_HOST}:{FLASK_RUN_PORT} ({FLASK_DEBUG})')
    if FLASK_DEBUG is True:
        app.run(threaded=True, debug=True, port=FLASK_RUN_PORT)
    else:
        app.run(threaded=True, port=FLASK_RUN_PORT)
