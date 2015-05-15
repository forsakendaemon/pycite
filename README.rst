======
PyCite
======
An extension to docutils that allows resolution of citations from a BibTeX file.

Usage
-----

PyCite can be used from the command line as follows::
    python pycite/tool.py path/to/file.txt path/to/output.html

It takes as input a ReStructuredText file with an associated BibTeX .bib file and Citation Styles Language .csl file.

PyCite has three directives that will be useful::
    .. bib:: bibliography
    .. csl:: apa
    .. bibliography::

These directives (shown with their respective defaults) set the bib file name (to bibliography.bib), the csl file name (to apa.csl) and specify the location of the bibliography in the output file, respectively.

Known Issues
------------

- Parsing will only proceed if you have at least one citation in the document.
- Only one citation can be used at a time (currently a limitation of docutils, but something I'd like to work on!
- When using only non-PyCite citations, a bibliography and CSL file must still be included.

PyCite relies on docutils_ and citeproc-py_, and if you don'd know those projects then you should check them out!

.. _docutils: http://docutils.sourceforge.net
.. _citeproc-py: https://github.com/brechtm/citeproc-py/
