#!/bin/env python
""" autocomplete using cleo
"""
import os
import sys
import argparse
from lxml import etree
import os.path
import re
import unicodedata
import urllib2

# http://stackoverflow.com/a/3448733/1763984
# Function returning a tuple or None: how to call that function nicely?
# because there are zero length input files or other problems reading the files
class MyReadError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def main(argv=None):
    # argument parser 
    parser = argparse.ArgumentParser(
                     description="playing around",
                     epilog="...")

    parser.add_argument("dir", help="directory to troll for XML files")

    parser.add_argument('--cleo_url', nargs='?', 
                     help='output greeked XML (or standard out)',
                     default='http://localhost:8080/cleo-primer/rest/elements/_')
    # arguments can come from the command line via argparse or passed in if main is called from other code
    if argv is None:
        argv = parser.parse_args()

    seen_names = {}
    counter = 0

    # look for files in the input directory
    # http://stackoverflow.com/a/12355420/1763984
    # http://stackoverflow.com/a/541408/1763984
    # http://www.saltycrane.com/blog/2007/03/python-oswalk-example/
    for (path, dirs, files) in os.walk(argv.dir):
        for file in files:
            # limit to XML files by file extension
            if os.path.splitext(file)[1] == '.xml':
                filename = os.path.join(path,file)
                # http://stackoverflow.com/a/3448733/1763984
                # Function returning a tuple or None: how to call that function nicely?
                try:
                    name, title = read_file(filename)
                except MyReadError:
                    break
                # http://youtu.be/naos7it_bl0
                # stop me if you think that you've heard this one before
                if not name in seen_names:
                    # not sure if the identifier has to be a number
                    counter = counter + 1
                    add_element(name, title, counter, 1, argv.cleo_url)
                    seen_names[name] = True

def read_file(file):
    """read the identity strings from the XML file"""
    # need this try/catch because sometime there are bogus files
    try:
        tree = etree.parse(file)
    # http://stackoverflow.com/a/730778/1763984
    except Exception: 
        raise MyReadError("could not open")
    # could be XML, but not EAC-CPF
    if tree.xpath("/eac:eac-cpf", namespaces={'eac': 'urn:isbn:1-931666-33-4'}) == None:
        raise MyReadError("not EAC")
    # returns a tuple of strings based on xpath expressions
    return ( u" ".join(tree.xpath("/eac:eac-cpf/eac:cpfDescription/eac:identity/eac:nameEntry/eac:part/text()",
                         namespaces={'eac': 'urn:isbn:1-931666-33-4'})), 
             u" ".join(tree.xpath("/eac:eac-cpf/eac:cpfDescription/eac:identity/eac:entityType/text()",
                         namespaces={'eac': 'urn:isbn:1-931666-33-4'})), )

# http://stackoverflow.com/a/11801981/1763984
# XML POST with Python
def post_xml(url, elem):
# http://stackoverflow.com/a/11801981/1763984
    data = etree.tostring(elem, encoding='UTF-8')
    request = urllib2.Request(url, data)
    request.add_header('Content-Type', 'application/xml')
    response = urllib2.urlopen(request)
    return response.read()

# create cleo XML element and POST it to the cleo index
def add_element(name, title, id, score, out):
     # create some XML
     element = etree.Element("element")
     # is there a shorter way to create an element and set thie value?
     id_e = etree.SubElement(element, "id")
     id_e.text = unicode(id)
     name_e = etree.SubElement(element, "name")
     name_e.text = name
     title_e = etree.SubElement(element, "title")
     title_e.text = title
     score_e = etree.SubElement(element, "score")
     score_e.text = unicode(score)
     # compile a regex to match all non-word characters (unicode aware)
     cleaner = re.compile('\W+', re.UNICODE)
     # MARC is decomposed, normalize to compatiable/combined form, or the cleaner regex will match combining characters
     # http://en.wikipedia.org/wiki/Unicode_equivalence#Normalization
     name = unicodedata.normalize('NFKC', name)
     clean_string = cleaner.sub(' ', name)
     for term in clean_string.split():
        term_e = etree.SubElement(element, "term")
        term_e.text = term.lower()
     post_xml(out, element)

# main() idiom for importing into REPL for debugging 
if __name__ == "__main__":
    sys.exit(main())
