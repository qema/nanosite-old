import markdown
import os
import datetime
import pkg_resources
import shutil

__version__ = "0.1"

# directories must have trailing slash
PostsDirectory = "posts/"
PagesDirectory = "pages/"
TemplatesDirectory = "templates/"
ArchiveDirectory = "archive/"
Templates = ["footer", "header", "main", "front", "page", "post"]
FrontMaxPosts = 5      # how many posts to show on front page

def insert_attribs(p, attribs):
    """This is the main mechanism to fill in templates by replacing
    "hook" strings with the content that should fill them.
    
    Keyword arguments:
    p -- String containing the template to be filled in.
    attribs -- Dictionary mapping template "hooks"
               (which will always be in the form $STRING$)
               to the strings which should replace them."""
    
    for attrib in attribs:
        p = p.replace(attrib, attribs[attrib])
    return p

def load_template(name):
    """Loads a template in the templates directory with name [name],
    and corresponding filename [name]-template.html."""
    return open(TemplatesDirectory + name + "-template.html", "r").read()

def load_templates():
    """Load all templates."""
    templates = {}
    for name in Templates:
        templates[name] = load_template(name)
    return templates
    
def load_markdown(filename, site_meta=None):
    """Converts a Markdown file to HTML and returns a tuple (html, meta) where
    [html] is the converted contents of the file and [meta] is a dictionary
    mapping meta properties to values. These meta properties are given at the
    top of Markdown files as follows:

    Name1: Value1
    Name2: Value2
    ...

    The Markdown file also has access to all attributes defined in site_meta,
    which it can access with dollar signs: $attrib$."""
    
    file_md = open(filename, "r").read()
    # Insert attribs from meta, adding surrounding dollar signs
    if site_meta is not None:
        file_md = insert_attribs(file_md, \
                                 {"$"+k+"$":v for k, v in site_meta.items()})
    
    # Markdown will parse metadata in posts
    md = markdown.Markdown(extensions = ["markdown.extensions.meta"])
    html = md.convert(file_md)
    meta = {k: "".join(v) for k, v in md.Meta.items()} \
           if md.Meta is not None else {}
    return (html, meta)

pages_cache = {}
def load_pages(site_meta, directory=PagesDirectory):
    """ Loads and returns all of the pages in [directory].
    These are cached so they are only loaded on the first call.
    Precondition: directory name ends with a slash '/'."""
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
            pages[1][filename] = load_markdown(path, site_meta)
        elif os.path.isdir(path):
            pages[0][filename] = load_pages(site_meta, directory + \
                                                       filename + "/")

    pages_cache[directory] = pages
    return pages

posts_cache = {}
post_titles = {}
def make_post(site_meta, templates, filename):
    """Builds the post with filename [filename] and returns the completed
    HTML string.
    These are cached so each page is only built on the first call."""
    global posts_cache
    if filename in posts_cache:
        return posts_cache[filename]
    
    post_content, meta = load_markdown(filename, site_meta)
    post_title = meta["title"] if "title" in meta else ""
    post_titles[os.path.basename(filename)] = post_title
    post_date = string_of_date(date_of_file(filename))
    
    name = os.path.splitext(filename)[0]
    post_attribs = {"$POST_TITLE$": post_title,
                    "$POST_CONTENT$": post_content,
                    "$POST_DATE$": post_date,
                    "$POST_PERMALINK$": site_meta["url"] + ArchiveDirectory + name + ".html" }
    post = insert_attribs(templates["post"], post_attribs)
    posts_cache[filename] = post
    return post

def title_of_post(filename):
    """Get title of post based on its filename"""
    global post_titles
    return post_titles[os.path.basename(filename)]
    
def date_of_file(filename):
    """Gets the creation date of the file."""
    t = os.stat(filename).st_birthtime if os.name != "nt" else \
        os.path.getctime(filename)
    return datetime.datetime.fromtimestamp(t)

def string_of_date(date):
    """Returns formatted string D Mon Y"""
    return "{} {} {}".format(date.day, date.strftime("%b"), date.year)

def make_menu(site_meta, templates, pages, base=True):
    """Returns navigation bar encapsulated in <nav> element.
    Built from a list (so <li>, <ul> elements).
    List items are given class "menu-item"."""
    menu_item_template = "<li><a href=\"{}\">{}</a></li>"

    menu_string = ""
    if base:
        menu_string += "<nav class=\"nav-bar\"><ul>"
        # Home link
        site_url = site_meta["url"]
        menu_string += menu_item_template.format(site_url + "index.html", \
                                                 "Home")
    # Directories become categories
    directories = pages[0]
    for directory in sorted(directories):
        menu_string += "<li><a href=\"#\">{}</a>".format(directory)
        menu_string += "<ul>"
        menu_string += make_menu(site_meta, templates,
                                 directories[directory], base=False)
        menu_string += "</ul></li>"

    # Files
    files = pages[1]
    for filename in sorted(files):
        name = os.path.splitext(filename)[0]
        url = site_meta["url"] + name + ".html"
        meta = files[filename][1]
        title = meta["title"] if "title" in meta else name
        menu_string += menu_item_template.format(url, title)

    if base:
        menu_string += "</ul></nav>"
        
    return menu_string

header_cache = None
def make_header(site_meta, templates):
    """Builds the site header and returns the completed HTML code.
    This is cached so it's only built on the first call."""
    global header_cache
    if header_cache is not None:
        return header_cache
    
    menu = make_menu(site_meta, templates, load_pages(site_meta))
    attribs = {"$SITE_URL$": site_meta["url"],
               "$TITLE$": site_meta["title"],
               "$TAGLINE$": site_meta["tagline"],
               "$MENU$": menu}
    header_cache = insert_attribs(templates["header"], attribs)
    return header_cache

def sorted_post_paths():
    """Get the paths of all posts, sorted by date created (newest first)."""
    paths = []
    for filename in os.listdir(PostsDirectory):
        paths.append(PostsDirectory + filename)
    # sort by most recent post
    paths = sorted(paths, key=lambda p:date_of_file(p), reverse=True)
    return paths
    
def make_content_from_posts(site_meta, templates):
    """Builds and concatenates together posts in the posts directory,
    up to a maximum of [FrontMaxPosts] posts."""
    html = ""

    paths = sorted_post_paths()

    for path in paths[:FrontMaxPosts]:
        # only process Markdown files
        if os.path.isfile(path) and os.path.splitext(path)[1] == ".md":
            # make post
            post_html = make_post(site_meta, templates, path)
            # append
            html += post_html

    return html

footer_cache = None
def make_footer(site_meta, templates):
    """Builds the site footer and returns the completed HTML code.
    This is cached so it's only built on the first call."""
    global footer_cache
    if footer_cache is not None:
        return footer_cache
    
    attribs = {"$AUTHOR$": site_meta["author"]}
    footer_cache = insert_attribs(templates["footer"], attribs)
    return footer_cache

def gen_front(site_meta, templates):
    """Builds the front page and writes to index.html."""

    content = insert_attribs(templates["front"],
                             {"$POSTS$":
                              make_content_from_posts(site_meta, templates)})
    
    attribs = {"$SITE_URL$": site_meta["url"],
               "$TITLE$": site_meta["title"],
               "$HEADER$": make_header(site_meta, templates),
               "$CONTENT$": content,
               "$NAV_LINK$": site_meta["url"] + "archive.html",
               "$NAV_TEXT$": "View older posts.",
               "$FOOTER$": make_footer(site_meta, templates)}
    page = insert_attribs(templates["main"], attribs)

    output_file = open("index.html", "w")
    output_file.write(page)
    output_file.close()

def gen_page(site_meta, templates, filename, page):
    """Generates the page with filename [filename] and contents [page] in the
    form of the (html, meta) tuple outputted by [load_markdown]."""
    
    html, meta = page
    name = os.path.splitext(filename)[0]
    page_title = meta["title"] if "title" in meta else name
    attribs = {"$PAGE_TITLE$": page_title,
               "$CONTENT$": html}
    content = insert_attribs(templates["page"], attribs)

    attribs = {"$SITE_URL$": site_meta["url"],
               "$TITLE$": site_meta["title"],
               "$HEADER$": make_header(site_meta, templates),
               "$CONTENT$": content,
               "$NAV_LINK$": site_meta["url"],
               "$NAV_TEXT$": "Return to home.",
               "$FOOTER$": make_footer(site_meta, templates)}
    page_output = insert_attribs(templates["main"], attribs)
    
    output_file = open(name + ".html", "w")
    output_file.write(page_output)
    output_file.close()

def gen_pages(site_meta, templates, pages=None):
    """Generate all pages.
    Set the [pages] parameter to generate only specific pages."""
    
    if not pages:
        pages = load_pages(site_meta)
        
    directories = pages[0]
    for directory in directories:
        gen_pages(site_meta, templates, directories[directory])

    files = pages[1]
    for filename in files:
        gen_page(site_meta, templates, filename, files[filename])

def gen_archive_entry(site_meta, templates, path):
    attribs = {"$SITE_URL$": site_meta["url"],
               "$TITLE$": site_meta["title"],
               "$HEADER$": make_header(site_meta, templates),
               "$CONTENT$": make_post(site_meta, templates, path),
               "$NAV_LINK$": site_meta["url"] + "archive.html",
               "$NAV_TEXT$": "Return to archives.",
               "$FOOTER$": make_footer(site_meta, templates)}
    page = insert_attribs(templates["main"], attribs)
    name = os.path.splitext(os.path.basename(path))[0]
    output_file = open(ArchiveDirectory + name + ".html", "w")
    output_file.write(page)
    output_file.close()
    
def gen_archive(site_meta, templates):
    """Generate the post archive:
    - Build all posts and put in archive folder.
    - Generate archive.html with links to all posts."""
    
    # Archive posts and build archive_md (formatted list of post links)
    archive_md = ""
    for path in sorted_post_paths():
        gen_archive_entry(site_meta, templates, path)
        
        name = os.path.splitext(os.path.basename(path))[0]
        output_path = ArchiveDirectory + name + ".html"

        title = title_of_post(path)
        url = site_meta["url"] + output_path
        archive_md += "* [{}]({})\n".format(title, url)

    # Create archive page based on page template
    archive_html = markdown.markdown(archive_md)
    gen_page(site_meta, templates, "archive.html",
             (archive_html, {"title": "Archive"}))

def gen_site():
    # Load settings as meta attributes from "meta.md"
    # Note: All URLs must have trailing slash
    site_meta = load_markdown("meta.md")[1]  # get meta info only
    
    templates = load_templates()

    gen_front(site_meta, templates)
    gen_pages(site_meta, templates)
    gen_archive(site_meta, templates)

def setup_blank_site(meta):
    def safe_mkdir(name):
        # Create the directory if it doesn't already exist
        if not os.path.exists(name):
            os.mkdir(name)

    # Write meta.md
    output = open("meta.md", "w")
    for key in meta:
        output.write(key + ": " + meta[key] + "\n")
    output.close()

    # Create folders
    safe_mkdir(PagesDirectory)
    safe_mkdir(PostsDirectory)
    safe_mkdir(TemplatesDirectory)
    safe_mkdir(ArchiveDirectory)

    # Copy default templates
    for name in Templates:
        rsc_path = "templates/" + name + "-template.html"
        src = pkg_resources.resource_filename(__name__, rsc_path)
        shutil.copyfile(src, TemplatesDirectory + name + "-template.html")

    # Copy style.css
    src = pkg_resources.resource_filename(__name__, "style.css")
    shutil.copyfile(src, "style.css")

    # Generate the site
    gen_site()
    
def setup_site_interactive():
    def prompt_YN(prompt):
        full_prompt = prompt + " [y/n] "
        print(full_prompt, end="")
        x = input()
        while x.lower()[:1] != "y" and x.lower()[:1] != "n":
            print("Invalid option. Type 'y' for yes and 'n' for no.")
            print(full_prompt, end="")
            x = input()
        return x.lower()[:1]
        
    print("-- nanosite --")
    setup_site = prompt_YN("Would you like to set up a site in this directory?")
    if setup_site == "y":
        print("Enter a title for your site: ", end="")
        title = input()
        print("Enter a tagline for your site: ", end="")
        tagline = input()
        print("Enter the author name for your site: ", end="")
        author = input()
        print("Enter the base URL where you will upload your site to.")
        print(" - Example: http://mysite.com/")
        print("Base URL: ", end="")
        site_url = input()
        if site_url[-1:] != "/":    # add trailing slash if needed
            site_url += "/"
        meta = {"title": title,
                "tagline": tagline,
                "author": author,
                "url": site_url}
        setup_blank_site(meta)
        print("Success! Generated site.")
    else:
        print("Canceled.")

def main(argv):
    def do_gen_site():
        gen_site()
        print("Generated site.")
        
    cmd = argv[0].lower() if len(argv) >= 1 else ""
    if cmd == "":
        # if site exists, build it
        if os.path.exists("meta.md") and os.path.isfile("meta.md"):
            do_gen_site()
        else:
            setup_site_interactive()
    elif cmd == "init":
        setup_site_interactive()
    elif cmd == "build":
        do_gen_site()
    elif cmd == "--help":
        print("Usage: nanosite [command]. Valid commands:")
        print("  init -- Start a new site in this directory.")
        print("  build -- Build the site in this directory.")
    else:
        print("nanosite: Invalid option. See 'nanosite --help'.")
