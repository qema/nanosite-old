# Settings
SiteAttribs = {"$TITLE$": "Paradoxical",
               "$TAGLINE$": "A computer science blog.",
               "$AUTHOR$": "Andrew Wang"}
SiteUrl = "./"
PostsDirectory = "posts/"    # with trailing slash
PagesDirectory = "pages/"    # with trailing slash
#FrontPageNumPosts = 10      # how many posts to show on front page

import markdown
import os
import datetime

front_template = \
    open("front-template.html", "r").read()
header_template = \
    open("header-template.html", "r").read()
post_template = \
    open("post-template.html", "r").read()

def insert_attribs(p, attribs):
    for attrib in attribs:
        p = p.replace(attrib, attribs[attrib])
    return p

# returns (html, meta) tuple
def load_markdown(filename):
    file_md = open(filename, "r").read()
    # Markdown will parse metadata in posts
    md = markdown.Markdown(extensions = ["markdown.extensions.meta"])
    html = md.convert(file_md)
    meta = md.Meta if md.Meta is not None else {}
    return (html, meta)
    
# returns html string given a post filename
def make_post(filename, post_date=""):
    post_content, meta = load_markdown(filename)
    post_title = meta["title"][0] if "title" in meta else ""
    
    post_attribs = {"$POST_TITLE$": post_title,
                    "$POST_CONTENT$": post_content,
                    "$POST_DATE$": post_date}
    return insert_attribs(post_template, post_attribs)

# gets date by creation date
def date_of_file(filename):
    t = os.path.getctime(filename)
    return datetime.datetime.fromtimestamp(t)

def string_of_date(date):
    return "{} {} {}".format(date.day, date.strftime("%b"), date.year)

# returns horizontal list with class [menu]
def make_menu():
    menu_string = "<ul class=\"menu\">"
    for filename in sorted(os.listdir(PagesDirectory)):
        path = PagesDirectory + filename
        name, ext = os.path.splitext(filename)
        # only process Markdown files
        if os.path.isfile(path) and ext == ".md":
            _, meta = load_markdown(path)
            url = SiteUrl + name + ".html"
            title = meta["title"][0] if "title" in meta \
                                          else os.path.splitext(filename)[0]
            menu_string += "<li><a href=\"{}\">{}</a></li>".format(url, title)
    menu_string += "</ul>"
    return menu_string
        
def make_header():
    menu = make_menu()
    attribs = {"$TITLE$": SiteAttribs["$TITLE$"],
               "$TAGLINE$": SiteAttribs["$TAGLINE$"],
               "$MENU$": menu}
    return insert_attribs(header_template, attribs)

def make_content_from_posts():
    posts = ""

    paths = []
    for filename in os.listdir(PostsDirectory):
        paths.append(PostsDirectory + filename)
    # sort by most recent post
    paths = sorted(paths, key=lambda p:date_of_file(p), reverse=True)

    for path in paths:
        # only process Markdown files
        if os.path.isfile(path) and os.path.splitext(path)[1] == ".md":
            # get date of post
            date = string_of_date(date_of_file(path))
            # make post
            html = make_post(path, date)
            # append
            posts += html
    return posts

def gen_front_page():
    attribs = {"$TITLE$": SiteAttribs["$TITLE$"],
               "$HEADER$": make_header(),
               "$CONTENT$": make_content_from_posts()}
    page = insert_attribs(front_template, attribs)

    print(page)

    output_file = open("index.html", "w")
    output_file.write(page)
    output_file.close()
    
gen_front_page()
