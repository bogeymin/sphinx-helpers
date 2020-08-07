"""Sphinx extension that embeds Disqus comments in documents.

https://sphinxcontrib-disqus.readthedocs.org
https://github.com/Robpol86/sphinxcontrib-disqus
https://pypi.python.org/pypi/sphinxcontrib-disqus
"""
# Imports

from __future__ import print_function

import os
import re

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.errors import ExtensionError, SphinxError

# Administrivia

# Original author, but this code was copied from the working fork at https://github.com/rmk135/sphinxcontrib-disqus
__author__ = '@Robpol86'
__maintainer__ = "Shawn Davis <shawn@develmaycare.com>"
__license__ = 'MIT'
__version__ = '1.2.0-x'

# Exports

__all__ = (
    "event_html_page_context",
    "on_builder_inited",
    "setup",
    "DisqusError",
    "DisqusNode",
    "DisqusDirective",
)

# Constants

RE_SHORTNAME = re.compile('^[a-zA-Z0-9-]{3,50}$')
STATIC_DIR = os.path.join(os.path.dirname(__file__), '_static')

# Classes


class DisqusError(SphinxError):
    """Non-configuration error. Raised when directive has bad options."""

    category = 'Disqus option error'


class DisqusNode(nodes.General, nodes.Element):
    """Disqus <div /> node for Sphinx/docutils."""

    def __init__(self, disqus_shortname, disqus_identifier):
        """Store directive options during instantiation.

        :param str disqus_shortname: Required Disqus forum name identifying the website.
        :param str disqus_identifier: Unique identifier for each page where Disqus is present.
        """
        super(DisqusNode, self).__init__()
        self.disqus_shortname = disqus_shortname
        self.disqus_identifier = disqus_identifier

    @staticmethod
    def visit(spht, node):
        """Append opening tags to document body list."""
        html_attrs = {
            'ids': ['disqus_thread'],
            'data-disqus-shortname': node.disqus_shortname,
            'data-disqus-identifier': node.disqus_identifier,
        }
        spht.body.append(spht.starttag(node, 'div', '', **html_attrs))

    @staticmethod
    def depart(spht, _):
        """Append closing tags to document body list."""
        spht.body.append('</div>')


class DisqusDirective(Directive):
    """Disqus ".. disqus::" rst directive."""

    option_spec = dict(disqus_identifier=str)

    def get_shortname(self):
        """Validate and returns disqus_shortname config value.

        :returns: disqus_shortname config value.
        :rtype: str
        """
        disqus_shortname = self.state.document.settings.env.config.disqus_shortname
        if not disqus_shortname:
            raise ExtensionError('disqus_shortname config value must be set for the disqus extension to work.')
        if not RE_SHORTNAME.match(disqus_shortname):
            raise ExtensionError('disqus_shortname config value must be 3-50 letters, numbers, and hyphens only.')
        return disqus_shortname

    def get_identifier(self):
        """Validate and returns disqus_identifier option value.

        :returns: disqus_identifier config value.
        :rtype: str
        """
        if 'disqus_identifier' in self.options:
            return self.options['disqus_identifier']

        title_nodes = self.state.document.traverse(nodes.title)
        if not title_nodes:
            raise DisqusError('No title nodes found in document, cannot derive disqus_identifier config value.')
        return _first(title_nodes).astext()

    def run(self):
        """Executed by Sphinx.

        :returns: Single DisqusNode instance with config values passed as arguments.
        :rtype: list
        """
        disqus_shortname = self.get_shortname()
        disqus_identifier = self.get_identifier()
        return [DisqusNode(disqus_shortname, disqus_identifier)]

# Functions


def event_html_page_context(app, pagename, templatename, context, doctree):
    """Called when the HTML builder has created a context dictionary to render a template with.

    Conditionally adding disqus.js to <head /> if the directive is used in a page.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str pagename: Name of the page being rendered (without .html or any file extension).
    :param str templatename: Page name with .html.
    :param dict context: Jinja2 HTML context.
    :param docutils.nodes.document doctree: Tree of docutils nodes.
    """
    assert app or pagename or templatename  # Unused, for linting.

    if doctree and 'script_files' in context:
        for n in doctree.traverse():
            if hasattr(n, "disqus_shortname"):
                context['script_files'] = context['script_files'][:] + ['_static/js/disqus.js']

    # if doctree and any(hasattr(n, 'disquss_shortname') for n in doctree.traverse()):
    #     if 'script_files' not in context:
    #         context['script_files'] = list()
    #
    #     # Clone list to prevent leaking into other pages and add disqus.js to this page.
    #     context['script_files'] = context['script_files'][:] + ['_static/js/disqus.js']

    # if 'script_files' in context and doctree and any(hasattr(n, 'disqus_shortname') for n in doctree.traverse()):
        # print("HERE ----------> add disqus.js")
        # Clone list to prevent leaking into other pages and add disqus.js to this page.
        # context['script_files'] = context['script_files'][:] + ['_static/disqus.js']


def on_builder_inited(app):
    # app.config.html_static_path.append(os.path.relpath(STATIC_DIR, app.confdir))

    # path = os.path.relpath(os.path.join(STATIC_DIR, "js"), app.confdir)
    path = os.path.relpath(STATIC_DIR, app.confdir)
    app.config.html_static_path.append(path)
    # app.config.html_js_files += ['js/disqus.js']


def setup(app):
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application object.

    :returns: Extension version.
    :rtype: dict
    """
    app.add_config_value('disqus_shortname', None, True)
    app.add_directive('disqus', DisqusDirective)
    app.add_node(DisqusNode, html=(DisqusNode.visit, DisqusNode.depart))
    # app.config.html_static_path.append(os.path.relpath(STATIC_DIR, app.confdir))
    app.connect('html-page-context', event_html_page_context)
    app.connect('builder-inited', on_builder_inited)
    return dict(version=__version__)


def _first(it):
    """Returns the first element in an iterable.
    
    Returns the first element found in a provided iterable no matter if it is a
    list or generator type. If no element is found, this call will return a
    `None` value.
    
    :param it: an iterable
    
    :returns: The first element
    :rtype: object
    """
    return next(iter(it), None)
