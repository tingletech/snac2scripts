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

def main(argv=None):
    # argument parser 
    parser = argparse.ArgumentParser(
                     description="playing around",
                     epilog="...")

    parser.add_argument("dir", help="directory to troll for XML files")

    if argv is None:
        argv = parser.parse_args()

    # http://stackoverflow.com/a/12355420/1763984
    # http://stackoverflow.com/a/541408/1763984
    # http://www.saltycrane.com/blog/2007/03/python-oswalk-example/

    # build a cleo load file
    output = etree.Element("element-list")
    doc = etree.ElementTree(output)
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
                # side effect on output xml
                add_element(output, name, title, counter, 1)
    # write out xml file
    doc.write('/home/btingle/python/test.xml', encoding='utf-8', pretty_print=True)

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

def add_element(tree, name, title, id, score):
     # create some XML
     element = etree.SubElement(tree, "element")
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
        
# main() idiom for importing into REPL for debugging 
if __name__ == "__main__":
    sys.exit(main())
