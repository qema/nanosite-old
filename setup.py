from setuptools import setup
from nanosite import __version__

setup(name = "nanosite",
      version = __version__,
      author = "Andrew Wang",
      scripts = ["nanosite"],
      py_modules = ["nanosite_gen"],
      data_files = [("templates", ["templates/footer-template.html",
                                 "templates/header-template.html",
                                 "templates/main-template.html",
                                 "templates/page-template.html",
                                 "templates/post-template.html"])])
