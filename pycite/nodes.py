"""Collection of nodes used in PyCite. Imports several things that are only used in other files."""

from docutils.nodes import citation_reference, enumerated_list, list_item, \
                           Inline, TextElement, Element

class underline(Inline, TextElement):
    """Underlined text (Not implemented in RST spec)"""
    pass

class small_caps(Inline, TextElement):
    """Small capitals (Not implemented in RST spec)"""
    pass

class light(Inline, TextElement):
    """Light text (Not implemented in RST spec)"""
    pass

class Bib(Element):
    """Informational element, contains the location of the .bib file. Removed during processing."""
    pass

class Csl(Element):
    """Informational element, contains the location of the .csl file. Removed during processing."""
    pass

class Bibliography(Element):
    """Informational element, specifies location of the Bibliography. Removed during processing."""
    pass
