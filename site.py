# Settings
SiteAttribs = {"$TITLE$": "Paradoxical",
           "$AUTHOR$": "Andrew Wang"}
PostsDirectory = "posts"    # no slash

import markdown
import os

def insert_attribs(p, attribs):
    for attrib in attribs:
        p = p.replace(attrib, attribs[attrib])
    return p

# returns html string for post
def make_post_from_markdown(post_md):
    # Markdown will parse metadata in posts
    md = markdown.Markdown(extensions = ["markdown.extensions.meta"])

    post_content = md.convert(post_md)
    post_title = md.Meta["title"] if "title" in md.Meta else ""
    
    post_attribs = {"$POST_TITLE$": post_title,
                    "$POST_CONTENT$": post_content,
                    "$POST_DATE$": "date-todo"}
    post_template = open("post-template.html", "r").read()
    return insert_attribs(post_template, post_attribs)
    
def insert_posts_as_content(p):
    posts = ""
    # TODO: specify order, nested folders
    for filename in os.listdir(PostsDirectory):
        if filename[-3:] == ".md":   # only process Markdown files
            post_md = open(PostsDirectory+"/"+filename, "r").read()
            html = make_post_from_markdown(post_md)
            posts += html
    return p.replace("$CONTENT$", posts)

page = open("template.html", "r").read()
page = insert_attribs(page, SiteAttribs)
page = insert_posts_as_content(page)

print(page)

output_file = open("index.html", "w")
output_file.write(page)
output_file.close()
