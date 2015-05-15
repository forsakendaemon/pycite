#!/usr/bin/env python3

"""Tool for running PyCite, with output to an HTML file."""

import argparse
import os

from docutils.core import publish_cmdline
from docutils.writers.html4css1 import Writer

from pycite import Reader, HTMLTranslator

def main():
    """Parses command-line arguments for an input file, then processes it using PyCite."""
    writer = Writer()
    writer.translator_class = HTMLTranslator
    reader = Reader()
    publish_cmdline(reader=reader, writer=writer)
    
if __name__ == '__main__':
    main()
