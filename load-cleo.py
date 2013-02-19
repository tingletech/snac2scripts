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
                # this will return False if file has problems
                read_name  = read_file(filename)
                if read_name:
                    counter = counter + 1
                    name = u" ".join(read_name)
                    # side effect on output
                    add_element(output, name, counter, 1)
    # write out xml file
    doc.write('/home/btingle/python/test.xml', encoding='utf-8', pretty_print=True)
    
def read_file(file):
    """read the identity strings from the XML file"""
    # need this try/catch because sometime there are bogus files
    try:
        tree = etree.parse(file)
    # http://stackoverflow.com/a/730778/1763984
    except Exception: 
        return False
    # could be XML, but not EAC-CPF
    if tree.xpath("/eac:eac-cpf", namespaces={'eac': 'urn:isbn:1-931666-33-4'}) == None:
        return False
    # grab all name parts, sloppy to return array/node set?
    return tree.xpath("/eac:eac-cpf/eac:cpfDescription/eac:identity/eac:nameEntry/eac:part/text()",
              namespaces={'eac': 'urn:isbn:1-931666-33-4'})

def add_element(tree, string, id, score):
     element = etree.SubElement(tree, "element")
     id_e = etree.SubElement(element, "id")
     id_e.text = unicode(id)
     name = etree.SubElement(element, "name")
     name.text = string
     title = etree.SubElement(element, "title")
     title.text = u'person'
     score_e = etree.SubElement(element, "score")
     score_e.text = unicode(score)
     # compile a regex to match all non-word characters (unicode aware)
     cleaner = re.compile('\W+', re.UNICODE)
     # MARC is decomposed, normalize to compatiable/combined form, or the cleaner regex will match combining characters
     string = unicodedata.normalize('NFKC', string)
     clean_string = cleaner.sub(' ', string)
     for term in clean_string.split():
        term_e = etree.SubElement(element, "term")
        term_e.text = term.lower()
        
# main() idiom for importing into REPL for debugging 
if __name__ == "__main__":
    sys.exit(main())
