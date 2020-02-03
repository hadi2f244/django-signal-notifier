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
import os
import sys
import django
# sys.path.insert(0, os.path.abspath('../source'))

sys.path.append(os.path.dirname(__file__))
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
django.setup()

from django_signal_notifier import VERSION

# MODULES_TO_MOCK = [  # TODO fix autodocs
#     'django',
#     'django.conf',
#     'django.contrib.auth',
#     'django.contrib.auth.models',
#     'django.utils',
#     'django.utils.importlib',
#     'django.utils.module_loading',
#     'django.utils.translation',
#     'django.template.loader',
# ]
#
# class ModuleMock(object):
#
#     __all__ = []
#
#     def __init__(self, *args, **kwargs):
#         pass
#
#     def __call__(self, *args, **kwargs):
#         return ModuleMock()
#
#     @classmethod
#     def __getattr__(cls, name):
#         if name in ('__file__', '__path__'):
#             return '/dev/null'
#         elif name[0] == name[0].upper():
#             MockType = type(name, (), {})
#             MockType.__module__ = __name__
#             return MockType
#         else:
#             return ModuleMock()
#
# for mod_name in MODULES_TO_MOCK:
#     sys.modules[mod_name] = ModuleMock()




# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx_rtd_theme',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']


# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# -- Project information -----------------------------------------------------

project = 'django_signal_notifier'
copyright = '2020, Mohammad Hadi Azaddel'
author = 'Mohammad Hadi Azaddel'

# The full version, including alpha/beta/rc tags
# The short X.Y version.
version = '.'.join(map(str, VERSION))
# The full version, including alpha/beta/rc tags.
release = '.'.join(map(str, VERSION))
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    html_theme = 'default'
else:
    html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'django-signal-notifier-doc'


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
#latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'django-signal-notifier.tex', u'django-signal-notifier Documentation',
   u'Mohammad Hadi Azaddel', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''
