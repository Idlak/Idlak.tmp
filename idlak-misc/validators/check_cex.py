#!/usr/bin/env python2
# -*- encoding utf-8 -*-

import argparse
from lxml import etree
import os
import sys
import re

# TODO: Phoneset
# TODO: Tones
# TODO: Format


def cex_has_allpos(cexxml, possetxml):
    """ The CEX file must have all the POS tags in the 'pos' set """
    posset_pos = set()
    for tag in possetxml.xpath('//tag'):
        name = tag.get('name', '')
        name = name.strip("'").strip('"')
        if len(name):
            posset_pos.add(name)

    if len(posset_pos):
        cexpos = cexxml.xpath('//set[@name="pos"]')
        if not cexpos:
            sys.stderr.write('cex does not have a set for pos\n')
            return False
        cex_pos = set()
        for item in cexpos[0].xpath('item'):
            cex_pos.add(item.get('name'))

    missing_pos = list(posset_pos - cex_pos)
    missing_pos.sort()
    if missing_pos:
        sys.stderr.write('POS tags are missing:\n\t'  + '\n\t'.join(missing_pos) + '\n')

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cex', required = True, type = argparse.FileType('r'),
                        help = 'cex xml to check')
    parser.add_argument('-p', '--phoneset', type = argparse.FileType('r'),
                        help = 'phoneset to check against')
    parser.add_argument('-P', '--posset', required = True, type = argparse.FileType('r'),
                        help = 'posset to check against')

    args = parser.parse_args()

    cexxml = etree.parse(args.cex)
    possetxml = etree.parse(args.posset)

    if not cex_has_allpos(cexxml, possetxml):
        sys.stderr.write('cex does not match posset\n')
        exit(1)




if __name__ == "__main__":
    main()