# Settings
SiteAttribs = {"$TITLE$": "Paradoxical",
           "$AUTHOR$": "Andrew Wang"}
PostsDirectory = "posts"    # no slash

import markdown
import os
import datetime

front_template = \
    open("front-template.html", "r").read()
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

def insert_posts_as_content(p):
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
    return p.replace("$CONTENT$", posts)

page = front_template
page = insert_attribs(page, SiteAttribs)
page = insert_posts_as_content(page)

print(page)

output_file = open("index.html", "w")
output_file.write(page)
output_file.close()
