import sys
import pathlib
import tomli
import datetime


sys.path.insert(0, str(pathlib.Path("..", "src").resolve()))
META = tomli.load(open("../pyproject.toml", "rb"))["project"]

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = META["name"].replace("-", " ").upper()
copyright = f"{datetime.datetime.now().year}, {META['authors'][0]['name']}"
author = META["authors"][0]["name"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_mdinclude",
]

autodoc_typehints = "description"
autodoc_class_signature = "separated"

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_theme_options = {
    "collapse_navbar": True,
}
