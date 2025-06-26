import sys
import pathlib
import tomli


sys.path.insert(0, str(pathlib.Path("..", "src").resolve()))
project = tomli.load(open("../pyproject.toml", "rb"))["project"]

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = project["name"]
copyright = f"2025, Simon Münker" 
author = "Simon Münker"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc"
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