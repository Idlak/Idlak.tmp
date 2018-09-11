# Tokeniser after normalising
from lxml import etree, objectify
from copy import deepcopy
from .. import idargparse, xmldoc, pyIdlak_txp, pytxplib

def splitNormalised(token):
    if token.get('nnorm') is None:
        return

    if token.get('nnorm') == '':
        token.getparent().remove(token)
        return
    #print (token.get('norm'), token.get('nnorm'), token.text)
    if ' ' not in token.get('nnorm'):
        token.set('norm', token.get('nnorm'))
        token.attrib.pop('nnorm')
        return

    words = token.get('nnorm').split(' ')

    # replace the original token norm with first word
    token.set('norm', words[0])
    # remove the nnorm attribute
    token.attrib.pop('nnorm')
    # go through the rest of the list and save as separate tokens
    tk_parent = token.getparent()
    last_tk = token
    for w in words[1:]:
        # make a copy of original token
        new_tk = deepcopy(token)
        new_tk.set('norm', w)
        new_tk.text = ""
        # append it after the previous token
        last_index = tk_parent.index(last_tk)
        tk_parent.insert(last_index+1, new_tk)
        last_tk = new_tk


class Norm_Tokenise(object):

    def __init__(self, idargs):
        if type(idargs) != idargparse.TxpArgumentParser:
            raise ValueError("idargs must be a TxpArgumentParser")


    def process(self, doc):
        """ process the document in place """
        if not type(doc) is xmldoc.XMLDoc:
            raise ValueError("doc must be a XMLDoc")

        # xmldoc to lxml
        strin = doc.to_string()
        xmlin = etree.fromstring(strin)

        tokens = xmlin.xpath('.//tk|.//break')
        for t in tokens:
            splitNormalised(t)

        # lxml to xmldoc
        strout = str(etree.tostring(xmlin, encoding='utf8').decode('utf8'))
        doc.load_string(strout)
