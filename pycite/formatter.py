"""Module to be used as a formatter by citeproc. Yes, all these imports are necessary."""

from citeproc.formatter.rst import RoleWrapper, Italic, Oblique, Bold, Superscript, \
                                   Subscript, preformat

class Light(RoleWrapper):
    """Light text (Not implemented in RST spec)"""
    role = 'light'

class Underline(RoleWrapper):
    """Underlined text (Not implemented in RST spec)"""
    role = 'underline'

class SmallCaps(RoleWrapper):
    """Small capitals (Not implemented in RST spec)"""
    role = 'small_caps'
