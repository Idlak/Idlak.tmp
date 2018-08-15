#takes output from cart lts and produces input for idlak

import treenode, sys, glob, os.path

def load_trees(indir, outfile):
    treefiles = glob.glob(indir + '/*/tree.dat')
    treefiles.sort()
    fplog = open(os.path.splitext(outfile)[0] + '_diagnostics.dat', 'w')
    fp = open(outfile, 'w')
    fp.write("<lts>\n")
    for t in treefiles:
        ltrdir = os.path.split(os.path.split(t)[0])[1]
        print 'Loading %s' % t
        sys.stdout.flush()
        ltr = ltrdir.split('_')[0].decode('utf8')
        if ltr=="stress":
            ltr="0"
        tree, nodelist = treenode.parse(treenode.mklist(treenode.tokenise_tree(t))[0], [])
        fplog.write("Letter: %s\n" % (ltr.encode('utf8')))
        
        sorted_nodelist = treenode.prune_tree(tree, nodelist, fplog) 
        terms, non_terms = treenode.reorder(sorted_nodelist)

        fp.write("\t<tree ltr='%s' rootnode='N%d' terminal='%d' nonterminal='%d'>\n" %
                 (ltr.encode('utf8'), len(terms), len(terms), len(non_terms)))
        idx = 0
        for i in terms:
            fp.write("\t\t<node id='T%d' val='%s'/>\n" % (idx, i[0]))
            idx += 1
        for i in non_terms:
            fp.write("\t\t<node id='N%d' pos='%s' posval='%s' yes='%d' no='%d'/>\n" % (idx, i[0], i[1], i[2], i[3]))
            idx += 1
        fp.write("\t</tree>\n")
        fp.flush()
        fplog.flush()
    fp.write("</lts>\n")
    fp.close()
    fplog.close()

if len(sys.argv) < 2 or sys.argv[1] == '-h' or len(sys.argv) > 3:
    print "python carttree2xml.py <input wagon dir> <output.xml>"
    sys.exit(1)


load_trees(sys.argv[1], sys.argv[2])
