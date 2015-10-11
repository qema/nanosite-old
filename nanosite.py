# Settings
SiteAttribs = {"$TITLE$": "Paradoxical",
               "$TAGLINE$": "A computer science blog.",
               "$AUTHOR$": "Andrew Wang"}
SiteUrl = "./"
PostsDirectory = "posts/"    # with trailing slash
PagesDirectory = "pages/"    # with trailing slash
#PageNumPosts = 10      # how many posts to show on front page

import markdown
import os
import datetime

main_template = open("main-template.html", "r").read()
header_template = open("header-template.html", "r").read()
post_template = open("post-template.html", "r").read()
page_template = open("page-template.html", "r").read()
                
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

# precondition: directory ends with a slash '/'
pages_cache = {}
def load_pages(directory=PagesDirectory):
    global pages_cache
    if directory in pages_cache:
        return pages_cache[directory]
    
    # first element is set of directories, recursively loaded;
    # second element is the files in this directory converted to html
    pages = [{}, {}]
    for filename in sorted(os.listdir(directory)):
        path = directory + filename
        # only process Markdown files
        if os.path.isfile(path) and os.path.splitext(filename)[1] == ".md":
            pages[1][filename] = load_markdown(path)
        elif os.path.isdir(path):
            pages[0][filename] = load_pages(directory + filename + "/")

    pages_cache[directory] = pages
    return pages
            
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

# returns navigation bar with [nav] element, and list items class [menu-item]
def make_menu(pages, base=True):
    menu_item_template = "<li><a href=\"{}\">{}</a></li>"

    menu_string = ""
    if base:
        menu_string += "<nav class=\"nav-bar\"><ul>"
        # Home link
        menu_string += menu_item_template.format(SiteUrl + "index.html", \
                                                 "Home")
        # Directories become categories
        # Only do this in base case (no subdirectories allowed)
        directories = pages[0]
        for directory in sorted(directories):
            menu_string += "<li><a href=\"#\">{}</a>".format(directory)
            menu_string += "<ul>"
            menu_string += make_menu(directories[directory], base=False)
            menu_string += "</ul></li>"

    # Files
    files = pages[1]
    for filename in files:
        name = os.path.splitext(filename)[0]
        url = SiteUrl + name + ".html"
        meta = files[filename][1]
        title = meta["title"][0] if "title" in meta else name
        menu_string += menu_item_template.format(url, title)

    if base:
        menu_string += "</ul></nav>"
        
    return menu_string

header_cache = None
def make_header():
    global header_cache
    if header_cache is not None:
        return header_cache
    
    menu = make_menu(load_pages())
    attribs = {"$TITLE$": SiteAttribs["$TITLE$"],
               "$TAGLINE$": SiteAttribs["$TAGLINE$"],
               "$MENU$": menu}
    header_cache = insert_attribs(header_template, attribs)
    return header_cache

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

def gen_front():
    attribs = {"$TITLE$": SiteAttribs["$TITLE$"],
               "$HEADER$": make_header(),
               "$CONTENT$": make_content_from_posts()}
    page = insert_attribs(main_template, attribs)

    output_file = open("index.html", "w")
    output_file.write(page)
    output_file.close()

# [page] is the (html, meta) tuple given by [load_markdown]
def gen_page(filename, page):
    html, meta = page
    name = os.path.splitext(filename)[0]
    page_title = meta["title"][0] if "title" in meta else name
    attribs = {"$PAGE_TITLE$": page_title,
               "$CONTENT$": html}
    content = insert_attribs(page_template, attribs)

    attribs = {"$TITLE$": SiteAttribs["$TITLE$"],
               "$HEADER$": make_header(),
               "$CONTENT$": content}
    page_output = insert_attribs(main_template, attribs)
    
    output_file = open(name + ".html", "w")
    output_file.write(page_output)
    output_file.close()
    
def gen_pages():
    # TODO: pages in subdirectories

    files = load_pages()[1]
    for filename in files:
        gen_page(filename, files[filename])

gen_front()
gen_pages()
