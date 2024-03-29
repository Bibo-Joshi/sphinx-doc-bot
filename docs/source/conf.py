# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# pylint: disable=C0103
"""Configuration of Sphinx documentation"""
import os
import sys

from sphinx.application import Sphinx

sys.path.insert(0, os.path.abspath("../.."))


# -- Project information -----------------------------------------------------

project = "Sphinx Doc Bot"
copyright = "2021-2023, Hinrich Mahler"  # pylint: disable=W0622
author = "Hinrich Mahler"
master_doc = "index"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]

# Use intersphinx to reference the python-telegram-bot docs
intersphinx_mapping = {
    "telegram": ("https://python-telegram-bot.readthedocs.io/en/latest/", None),
    "python": ("https://docs.python.org/3/", None),
}

napoleon_use_admonition_for_examples = True
typehints_fully_qualified = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
# exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"
html_theme_options = {
    "navigation_with_keys": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "../../logo/sphinx-doc-bot-logo.png"

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "../../logo/sphinx-doc-bot-logo.ico"


def setup(app: Sphinx) -> None:
    """Adds dark mode to theme"""
    app.add_css_file("dark.css")
