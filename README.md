# nanosite
nanosite is a speedy static site generator in Python. It's a thin layer around your content and customizable to the core. Feedback and pull requests are welcome.

Here's a website made with nanosite: [wanganzhou.com](http://wanganzhou.com/).

## Features
* Write your content in simple [Markdown](http://daringfireball.net/projects/markdown/) format.
* Create a blog or static pages or a combination of both.
* Templates are simple and extremely flexible.
* Simple, fast workflow.

## How to Install
Download the repo and run setup.py install:

    python setup.py install

## How to Use
To start a new site, simply run `nanosite` at the terminal, in the directory you want the site to be in. Follow the prompts to generate a blank site. After editing your site, run `nanosite` again to build it. Or, type `nanosite build` to do this explicitly.

Put your posts, or time-sorted content, as `.md` files in the `posts/` directory.  
Put your pages, or static content, as `.md` in the `pages/` directory. Or, you can create folders in this directory, which will become category names. Every page in one of these sub-folders will be organized accordingly in the site's navigation bar.

Example directory structure:
- mysite/
  - posts/
    - 2015-9-4.md
    - 2015-9-6.md
  - pages/
    - Music/
      - song_recs.md
    - Writing/
      - essay1.md
      - essay2.md

nanosite can infer default titles for each post or page, but if you want to set your own titles, add a `title:` meta attribute at the top of each file. For example:

    title: My Latest Adventure
    
    I just had the greatest trip to Iceland! ...

nanosite will use your titles accordingly.
