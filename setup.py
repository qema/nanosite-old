from setuptools import setup
from nanosite_gen.nanosite_gen import __version__

setup(name = "nanosite",
      version = __version__,
      url = "https://github.com/qema/nanosite",
      author = "Andrew Wang",
      scripts = ["nanosite"],
      packages = ["nanosite_gen"],
      package_data = {"nanosite_gen": ["templates/*.html", "style.css"]})
