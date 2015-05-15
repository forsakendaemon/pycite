"""This module collects the primary functionality of PyCite.

PyCite is a tool for resolving ReStructuredText citations from a bib file, rather than from
targets defined in the RST file itself. It introduces three new directives - the bib directive,
for specifying the location of the .bib file, the csl directive, for specifying the location
of the .csl file (see http://www.citationstyles.org for more information on CSL), and the
bibliography directive for specifying the location of the bibliography, which is output
as an enumerated list.

PyCite leaves alone citations which are not specified in a .bib file, and so will work with
in-file citations as well."""

import re
import os

from citeproc.source.bibtex import BibTeX
from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import Citation, CitationItem

import docutils.transforms
import docutils.readers
from docutils.core import publish_doctree
from docutils.parsers.rst import Directive, directives
import docutils.writers.html4css1 as html

import pycite.formatter as formatter
import pycite.nodes as nodes

def escape_elist(string):
    """Escapes a string starting with ( that isn't an enumerated list"""
    return '\\' + string if string.startswith('(') else string

def escape_bquote(string):
    """Removes whitespace from a string that isn't a blockquote"""
    return string.strip()

IROLEPATTERN = re.compile(r"(:`.*`)(\S)")

def escape_irole(string):
    """Deals with the case where an interpreted role is immediately
    followed by a non-whitespace character, such as "a :emphasis:`b`c"."""
    return IROLEPATTERN.sub(r"\1 \2", string)

WSPACEPATTERN = re.compile(r"(\s+|\n)")

def escape_wspace(string):
    """Collapses extra whitespace down to a single space, and removes newlines"""
    return WSPACEPATTERN.sub(" ", string)


def escape(string):
    """Chains together the previous escape patterns"""
    return escape_wspace(escape_elist(escape_bquote(escape_irole(string))))

def fail(citation_item):
    """Failure function to use as a callback when citing"""
    raise ValueError("Reference with key '{}' not found in the bibliography."
                     .format(citation_item.key))

class Bib(Directive):
    """The .. bib:: directive specifies the location of the bib file"""
    required_arguments = 1

    def run(self):
        bib_node = nodes.Bib(bibfile=self.arguments[0])
        return [bib_node]

directives.register_directive('bib', Bib)

class Csl(Directive):
    """The .. csl:: directive specifies the location of the csl file"""
    required_arguments = 1

    def run(self):
        csl_node = nodes.Csl(cslfile=self.arguments[0])
        return [csl_node]

directives.register_directive('csl', Csl)

class Bibliography(Directive):
    """The .. bibliography:: directive specifies the location of the bibliography in the output"""
    def run(self):
        bibliography_node = nodes.Bibliography()
        return [bibliography_node]

directives.register_directive('bibliography', Bibliography)


class Transform(docutils.transforms.Transform):
    """The PyCite Transform handles the recognition and processing of bib-backed citations"""
    default_priority = 208

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cwd, _ = os.path.split(self.document.transformer.components['input'].source_path)
        self.bib_source = "bibliography"
        self.bib_style = "apa"
        self.bibliography = None
        self.citations = {}

    def register_item(self, item):
        """Registers the citation with the Bibliography"""
        citation = Citation([CitationItem(item["refname"])])
        self.citations[item["refname"]] = citation
        self.bibliography.register(citation)

    def cite_item(self, item):
        """Inserts the in-text citation"""
        try:
            i = publish_doctree(escape(self.bibliography.cite(self.citations[item["refname"]],
                                                              fail)))[0][0]
        except ValueError:
            return
        item.parent.replace(item, i)

    def apply(self):
        """Process Bib and Csl nodes, set up bibliography opbects, register and then cite the
        in-text citations, and then construct the bibliography."""
        # Find Bib and Csl nodes and extract the relevant information from them.
        bibnodes = [bib for bib in self.document.traverse() if isinstance(bib, nodes.Bib)]
        if bibnodes:
            self.bib_source = bibnodes[0]["bibfile"]

        cslnodes = [csl for csl in self.document.traverse() if isinstance(csl, nodes.Csl)]
        if cslnodes:
            self.bib_style = cslnodes[0]["cslfile"]

        # Remove the extraneous nodes now we're done with them.
        for node in bibnodes + cslnodes:
            node.parent.remove(node)

        citations = [cite for cite in self.document.traverse() \
                     if isinstance(cite, nodes.citation_reference)]

        if citations:
            # Set up the bibliography objects.
            self.bib_source = os.path.join(self.cwd, self.bib_source + \
                                          (".bib" if not self.bib_source.endswith('.bib') else ''))
            self.bib_source = BibTeX(self.bib_source)
            self.bib_style = os.path.join(self.cwd, self.bib_style + \
                                          (".csl" if not self.bib_style.endswith('.csl') else ''))
            self.bib_style = CitationStylesStyle(self.bib_style, validate=False)
            self.bibliography = CitationStylesBibliography(self.bib_style,
                                                           self.bib_source, formatter)

            # Register each in-text citation, then cite each one.
            for citation in citations:
                self.register_item(citation)
            for citation in citations:
                self.cite_item(citation)

            # Find the places where a Bibliography has been requested.
            bnodes = [bib for bib in self.document.traverse() \
                      if isinstance(bib, nodes.Bibliography)]
            self.document.b = self.bibliography
            biblist = nodes.enumerated_list()
            bibtexts = self.bibliography.bibliography()
            for btext in bibtexts:
                list_item = nodes.list_item()
                item_node = publish_doctree(escape(str(btext)))[0]
                list_item.append(item_node)
                biblist.append(list_item)
            for bnode in bnodes:
                bnode.parent.replace(bnode, biblist)

class Reader(docutils.readers.Reader):
    """Generic Reader subclass that adds the PyCite Transform"""
    def get_transforms(self):
        """Override of the corresponding method on docutils.readers.Reader"""
        return super().get_transforms() + [Transform]

class HTMLTranslator(html.HTMLTranslator):
    """HTML Translator to deal with the custom nodes defined in nodes.py"""

    def visit_underline(self, node):
        """Begin a <u>"""
        self.body.append(self.starttag(node, 'u', ''))

    def depart_underline(self, node):
        """Close the <u>"""
        del node # unused
        self.body.append('</u>')

    def visit_small_caps(self, node):
        """Begin a <span style="font-variant: small-caps">"""
        self.body.append(self.starttag(node, 'span', '', style='font-variant: small-caps'))

    def depart_small_caps(self, node):
        """End a <span style="font-variant: small-caps">"""
        del node # unused
        self.body.append('</span>')

    def visit_light(self, node):
        """Begin a <span style="font-weight: lighter">"""
        self.body.append(self.starttag(node, 'span', '', style='font-weight: lighter'))

    def depart_light(self, node):
        """End a <span style="font-weight: lighter">"""
        del node # unused
        self.body.append('</span>')

    def unimplemented_visit(self, node):
        """if a node is visited that we don't know about yet, raise an Error."""
        raise NotImplementedError('visiting unimplemented node type: %s'
                                  % node.__class__.__name__)
