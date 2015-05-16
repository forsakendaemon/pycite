from distutils.core import setup

setup(
    name='pycite',
    version='0.1',
    packages=['pycite'],
    url='https://github.com/forsakendaemon/pycite',
    author='David Allen',
    author_email='forsakendaemon+pycite@gmail.com',
    description='An extension to docutils that allows resolution of citations from a BibTeX file.',
    requires=['docutils', 'citeproc-py'],
    provides=['pycite'],
    scripts=['tool.py']
)
