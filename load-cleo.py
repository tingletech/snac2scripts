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

    # http://stackoverflow.com/a/12355420/1763984
    # http://stackoverflow.com/a/541408/1763984
    # http://www.saltycrane.com/blog/2007/03/python-oswalk-example/

    counter = 0
    # look for files in the input directory
    for (path, dirs, files) in os.walk(argv.dir):
        for file in files:
            # limit to XML files by file extension
            if os.path.splitext(file)[1] == '.xml':
                filename = os.path.join(path,file)
                # http://stackoverflow.com/a/3448733/1763984
                try:
                    read_name, read_title = read_file(filename)
                except MyReadError:
                    break
                # not sure if the identifier has to be a number
                counter = counter + 1
                # convert from array/nodelist to unicode string
                name = u" ".join(read_name)
                title = u" ".join(read_title)
                # POST to cleo index
                add_element(name, title, counter, 1, argv.cleo_url)

class MyReadError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
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
    # grab all name parts, sloppy to return array/node set?
    return (tree.xpath("/eac:eac-cpf/eac:cpfDescription/eac:identity/eac:nameEntry/eac:part/text()",
              namespaces={'eac': 'urn:isbn:1-931666-33-4'}), 
            tree.xpath("/eac:eac-cpf/eac:cpfDescription/eac:identity/eac:entityType/text()",
              namespaces={'eac': 'urn:isbn:1-931666-33-4'}), 
           )

# http://stackoverflow.com/a/11801981/1763984
def post(url, data, contenttype):
    request = urllib2.Request(url, data)
    request.add_header('Content-Type', contenttype)
    response = urllib2.urlopen(request)
    return response.read()

def postxml(url, elem):
    data = etree.tostring(elem, encoding='UTF-8')
    print data
    return post(url, data, 'application/xml')

def add_element(name, title, id, score, out):
     # create some XML
     element = etree.Element("element")
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
     name = unicodedata.normalize('NFKC', name)
     clean_string = cleaner.sub(' ', name)
     for term in clean_string.split():
        term_e = etree.SubElement(element, "term")
        term_e.text = term.lower()
     # ElementTree has the write/tostring methods
     postxml(out, element)

# main() idiom for importing into REPL for debugging 
if __name__ == "__main__":
    sys.exit(main())
