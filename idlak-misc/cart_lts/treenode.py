# Copyright 2018 Cereproc Ltd. (author: Matthew Aylett)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.
# -*- coding: utf-8 -*-

import os.path, os, glob, re, platform

###################################################################
#                     Class definitions                           #
###################################################################
class treenode:
    def __init__(self, feat, isa, yesnode, nonode, val, id, obsolete = 0):
        self.feat = feat
        self.isa = isa
        self.yesnode = yesnode
        self.nonode = nonode
        self.val = val
        self.id = id
        self.obsolete = obsolete

    def set_parent(self, parent):
        self.parent = parent
        if self.feat:
            self.yesnode.set_parent(self.id)
            self.nonode.set_parent(self.id)

    def set_daughters(self):
        if not self.feat:
            self.daughters = []
        else:
            self.daughters = [self.yesnode.id] + self.yesnode.set_daughters() + [self.nonode.id] + self.nonode.set_daughters()
        return self.daughters

    def __str__(self):
        if not self.feat:
            return '(id=' + str(self.id) + ' val=' + self.val + ')'
        else:
            return '(id=' + str(self.id) + ' if ' + self.feat + '=' + self.isa + ' ' + self.yesnode.__str__() + self.nonode.__str__() + ')' 
    
    def to_string(self):
        if not self.feat:
            return '(' + self.val + ')'
        else:
            return '(' + self.feat + ' ' + self.isa + ' ' + self.yesnode.to_string() + self.nonode.to_string() + ')'

def prune_tree(tree, nodelist, fp):
    """
    @param tree: root node of cart tree
    @type treenode
    @param nodelist: list of nodes in tree
    @type list
    @param fp: file pointer (for writing compression diagnostics)
    @type file *
    Mark duplicates as obsolete, update the tree branch pointers and ids accordingly
    """
    tree.set_parent(None)
    sorted_nodelist = []
    for n in nodelist:
        n.string_rep = n.to_string()
        sorted_nodelist.append(n)
        n.set_daughters()
        sorted_nodelist.sort(sort_branch)
    last_n = sorted_nodelist[0]

    for n in sorted_nodelist[1:]:
        if not n.obsolete:
            if n.string_rep == last_n.string_rep:
                n.obsolete = 1
                for d in n.daughters:
                    for i in sorted_nodelist:
                        if i.id == d:
                            i.obsolete = 1
                parent = None
                last_parent = None
                #Set the parent of the obsolete branch to point to the matching branch
                for i in sorted_nodelist:
                    if i.id == last_n.parent:
                        last_parent = i
                    if i.id == n.parent:
                        parent = i
                if last_n == last_parent.yesnode:
                    if n == parent.yesnode:
                        parent.yesnode = last_parent.yesnode
                    else:
                        parent.nonode = last_parent.yesnode
                else:
                    if n == parent.yesnode:
                        parent.yesnode = last_parent.nonode
                    else:
                        parent.nonode = last_parent.nonode
            else: last_n = n  #Only make the current node the last node if it's not been made obsolete

    obsolete = 0
    valid = 0
    for n in nodelist:
        if n.obsolete:
            obsolete = obsolete + 1
        else:
            valid = valid + 1

    fp.write("Initial nodes: %d\nNodes after reduction %d\nReduction: %0.2f%%\n\n" % (obsolete + valid, valid, float(obsolete) / (float(obsolete) + float(valid)) * 100))

    #Recompute id distribution
    sorted_nodelist.sort(sort_node_id)   #Sort by id this time

    i = 0
    while i < len(sorted_nodelist):      #Remove obsolete nodes and update ids in nodelist 
        if sorted_nodelist[i].obsolete:
            sorted_nodelist.remove(sorted_nodelist[i])
            if i != len(sorted_nodelist):
                for j in xrange(i, len(sorted_nodelist)):
                    sorted_nodelist[j].id = sorted_nodelist[j].id - 1
        else:
            i = i + 1

    return sorted_nodelist

def sort_branch(a, b):     
    """
    @param a, b: node pair to be sorted by string representation length
    @type treenode, treenode
    """
    if len(a.string_rep) > len(b.string_rep):
        return -1
    elif len(a.string_rep) < len(b.string_rep):
        return 1
    else:
        if a.string_rep > b.string_rep:
            return 1
        elif a.string_rep < b.string_rep:
            return -1
        else:
            return 0

def sort_node_id(a, b):
    """
    @param a, b: node pair to be sorted by id
    @type treenode, treenode
    """
    if a.id > b.id:
        return 1
    else:
        return -1

def reorder(nodelist):
    '''Reorder the nodes so that the terminal nodes are stored before the non terminal ones,
    and make the root node the first non terminal node so that it can be accessed easily
    Return a list of all terminals and a list of all non-terminals'''
    terms = []
    non_terms = []

    #Move the root to the start of the list
    for i in xrange(len(nodelist)):
        if nodelist[i].parent == None:
            root = nodelist.pop(i)
            nodelist.insert(0, root)
            break

    #Update the ids
    for i in xrange(len(nodelist)):
        nodelist[i].id = i

    id_map = {}
    new_id = 0

    #Create the id mapping for the terminals
    for i in xrange(len(nodelist)):
        if not nodelist[i].feat:
            id_map[i] = new_id
            new_id = new_id + 1

    #Create the id mapping for the non terminals
    for i in xrange(len(nodelist)):
        if nodelist[i].feat:
            id_map[i] = new_id
            new_id = new_id + 1

    #Update the ids; now all terminals will have ids lower than those of the non terminals
    for n in nodelist:
        n.id = id_map[n.id]

    #Create the lists of terminals and non terminals
    for i in xrange(len(nodelist)):
        if nodelist[i].feat:
            fl = [nodelist[i].feat]      #field list
            fl.append(nodelist[i].isa.encode('utf8'))
            fl.append(nodelist[i].yesnode.id)
            fl.append(nodelist[i].nonode.id)
            non_terms.append(fl)
        else:
            terms.append([nodelist[i].val.encode('utf8')])

    return terms, non_terms


def parse(treelist, nodelist):
    """
    Convert a list structure into a tree object
    """
    if len(treelist) == 3:
        yesnode, nodelist = parse(treelist[1], nodelist)
        nonode, nodelist = parse(treelist[2], nodelist)
        node = treenode(treelist[0][0], treelist[0][2].decode('utf8'),
                        yesnode, nonode, None, len(nodelist))
    else:
        node = treenode(None, None, None, None, treelist[0][-1], len(nodelist))
    nodelist.append(node)
    return node, nodelist

def mklist(tokens):
    """
    Input a tokenised list and return a list structure
    """
    l = []
    while tokens:
        t = tokens.pop()
        if t == '(':
            l.append(mklist(tokens))
        elif t == ')':
            return l
        else:
            l.append(t)
    return l

def tokenise_tree(treef):
    """
    Input a tree output by wagon and return a tokenised list
    """
    fp = open(treef)
    tokens = ['']
    lastc = 'whitespace'
    c = fp.read(1)
    while c:
        if re.match('[\s\n]', c):
            if lastc == 'token':
                tokens.append('')
                lastc = 'whitespace'
        elif c == '(' or c == ')':
            if not tokens[-1]:
                tokens[-1] = c
            else:
                tokens.append(c)
            tokens.append('')
            lastc = 'whitespace'
        else:
            tokens[-1] = tokens[-1] + c
            lastc = 'token'
        c = fp.read(1)
    if not(tokens[-1]):
        tokens = tokens[:-1]
    tokens.reverse()
    fp.close()
    return tokens
