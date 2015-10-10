# Settings
SiteAttribs = {"$TITLE$": "Paradoxical",
               "$TAGLINE$": "A computer science blog.",
               "$AUTHOR$": "Andrew Wang"}
PostsDirectory = "posts"    # no slash
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

# returns html string for post
def make_post_from_markdown(post_md, post_date=""):
    # Markdown will parse metadata in posts
    md = markdown.Markdown(extensions = ["markdown.extensions.meta"])

    post_content = md.convert(post_md)
    post_title = md.Meta["title"][0] if md.Meta is not None \
                                     and "title" in md.Meta else ""
    
    post_attribs = {"$POST_TITLE$": post_title,
                    "$POST_CONTENT$": post_content,
                    "$POST_DATE$": post_date}
    post_template = open("post-template.html", "r").read()
    return insert_attribs(post_template, post_attribs)

# gets date by creation date
def date_of_file(p):
    t = os.path.getctime(p)
    return datetime.datetime.fromtimestamp(t)

def string_of_date(date):
    return "{} {} {}".format(date.day, date.strftime("%b"), date.year)

def make_header():
    return insert_attribs(header_template, SiteAttribs)

def make_content_from_posts():
    posts = ""

    paths = []
    for filename in os.listdir(PostsDirectory):
        paths.append(PostsDirectory + "/" + filename)
    # sort by most recent post
    paths = sorted(paths, key=lambda p:date_of_file(p), reverse=True)

    for path in paths:
        if path[-3:] == ".md":   # only process Markdown files
            post_md = open(path, "r").read()

            # get date of post
            date = string_of_date(date_of_file(path))

            # make post
            html = make_post_from_markdown(post_md, date)
            # append
            posts += html
    return posts

attribs = {"$TITLE$": SiteAttribs["$TITLE$"],
           "$HEADER$": make_header(),
           "$CONTENT$": make_content_from_posts()}
page = insert_attribs(front_template, attribs)

print(page)

output_file = open("index.html", "w")
output_file.write(page)
output_file.close()
