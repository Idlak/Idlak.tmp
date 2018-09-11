# -*- coding: utf-8 -*-
# prototype normaliser for Idlak
import sys
import os
import traceback
import copy
import importlib.util
from lxml import etree, objectify
from xml.sax.saxutils import escape
from re import match, compile
from .. import idargparse, xmldoc, pyIdlak_txp, pytxplib

validmatchtypes = ['rgx', 'xml']
validreplacetypes = ['fixed', 'lookup', 'func', 'xml']
validsrc = ['lcase', 'mcase', 'pos']
NORMFUNCS = None

def importhrules(hrules_fn):
    global NORMFUNCS
    spec = importlib.util.spec_from_file_location("hrules", hrules_fn)
    hrules_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hrules_module)
    NORMFUNCS = hrules_module.NORMFUNCS
    
def getlkpitem(items):
    matched = match("\s*[\'\"](.+?)[\'\"]\s*:\s*[\'\"](.*)[\'\"]\s*,\s*(.*)", items)
    if not matched:
        matched = match("\s*[\'\"](.+?)[\'\"]\s*:\s*[\'\"](.*)[\'\"]\s*", items)
    return matched

def parselookup(lkptext):
    try:
        # eval automatically converts unicode into ascii so
        # we have to decode it again.
        lkp_encode = eval(lkptext)
        lkp = {}
        for k in lkp_encode.keys():
            #lkp[k.decode('utf8')] = lkp_encode[k].decode('utf8')
            lkp[k] = lkp_encode[k]
    except SyntaxError:
        type, value, tb = sys.exc_info()
        traceback.print_exception(type, value, tb)
        return {}, None
    except TypeError:
        #print ('HERE', lkptext)
        return {}, None
    return lkp, None

def getpretk(tokens, i):
    while i >= 0:
        if tokens[i].tag == 'tk':
            return tokens[i]
        i = i - 1
    return None
    
def getpsttk(tokens, i):
    while i < len(tokens):
        if tokens[i].tag == 'tk':
            return tokens[i]
        i = i + 1
    return None
    
# search up the tree for a specific tag
def gettagup(tk, tag):
    parent = tk.getparent()
    while parent:
        if parent.tag == tag:
            return parent
        parent = tk.getparent()
    return None
    
class Match:
    type = ''
    src = ''
    offset = None
    norm = None
    rule = None
    def __init__(self, norm, rule, type, xml):
        if not type in validmatchtypes:
            sys.stderr.write('WARNING Bad match component:' + etree.tostring(xml))
            return
        self.type = type
        self.src = xml.get('src')
        self.offset = int(xml.get('offset'))
        if self.offset < norm.minoffset:
            norm.minoffset = self.offset
        if self.offset > norm.maxoffset:
            norm.maxoffset = self.offset
        self.norm = norm
        self.rule = rule

class RgxMatch(Match):
    rgxname = ''
    def __init__(self, norm, rule, xml):
        Match.__init__(self, norm, rule, 'rgx', xml)
        self.rgxname = xml.get('name')
    def apply(self, pos, tokens):
        if pos + self.offset < 0:
            return False, []
        if pos + self.offset >= len(tokens):
            return False, []
        if self.rgxname not in self.norm.rgxs:
            #sys.stderr.write('WARNING Bad match component:' + self.rgxname)
            return False, []
        if self.src == 'lcase':
            val = tokens[pos +self.offset].get('norm')
            if val is None:
                return False, []
            matched = match(self.norm.rgxs[self.rgxname], val)
            if matched:
                if not len(matched.groups()):
                    return True, [matched.group(0)]
                else:
                    return True, matched.groups()
            else:
                return False, []
        else:
            if tokens[pos +self.offset].text:
                matched = match(self.norm.rgxs[self.rgxname], (tokens[pos +self.offset].text).strip())
            else:
                return False, []
            if matched:
                if not len(matched.groups()):
                    return True, [matched.group(0)]
                else:
                    return True, matched.groups()
                #return True, [matched.group(0)] + list(matched.groups())
            else:
                return False, []
            

class XmlMatch(Match):
    xmltag = ''
    xmlatt = ''
    xmlval = ''
    xtype = ''
    def __init__(self, norm, rule, xml):
        Match.__init__(self, norm, rule, 'xml', xml)
        self.xmltag = xml.get('name')
        self.xmlatt = xml.get('attribute')
        self.xmlval = xml.get('val')
        self.xtype = xml.get('xtype')
    def apply(self, pos, tokens):
        starttag = True
        endtag = True
        if pos + self.offset < 0:
            return False, []
        if pos + self.offset >= len(tokens):
            return False, []
        # search for the tag (break tags treated differently)
        if self.xmltag == 'break':
            if pos + self.offset + 1 < len(tokens) and \
               tokens[pos + self.offset + 1].tag == 'break':
                intag = [tokens[pos + self.offset + 1]]
        else:
            intag = tokens[pos + self.offset].xpath('ancestor::' + self.xmltag)
        if not len(intag):
            return False, []
        # get tag position
        pretk = getpretk(tokens, pos + self.offset)
        if pretk is not None:
            tag = pretk.xpath('ancestor::' + self.xmltag)
            if tag: starttag = False
        psttk = getpsttk(tokens, pos + self.offset)
        if psttk is not None:
            tag = psttk.xpath('ancestor::' + self.xmltag)
            if tag: endtag = False
        if self.xtype:
            if self.xtype == 'start' and not starttag:
                return False, []
            elif self.xtype == 'startend' and not (starttag and endtag):
                return False, []
        if self.xmlatt:
            if not (self.xmlatt in intag[0].keys()):
                return False, []
            else:
                if self.xmlval:
                    if not intag[0].get(self.xmlatt) ==  self.xmlval:
                        return False, []
        return True, [tokens[pos + self.offset].get('norm')]
                        
class Replace:
    type = ''
    offset = None
    fromoffset = None
    fromgroup = -1
    newxml = None
    norm = None
    rule = None
    def __init__(self, norm, rule, type, xml):
        if not type in validreplacetypes:
            sys.stderr.write('WARNING Bad replace component:' + etree.tostring(xml))
            return
        self.type = type
        if xml.get('grp'):
            self.fromgroup = int(xml.get('grp'))
        if type == 'fixed' and xml.get('val'):
            if xml.get('from'):
                sys.stderr.write('WARNING Bad replace component (fixed value taking from value):' + etree.tostring(xml))
        if xml.get('from'):
            self.fromoffset = int(xml.get('from')[1:])
        newxml = xml.getchildren()
        if len(newxml) > 1:
            sys.stderr.write('WARNING Bad replace component (odd replace xml):' + etree.tostring(xml))
        elif len(newxml) > 0:
            self.newxml = newxml[0]
        self.offset = int(xml.get('offset'))
        if self.offset < norm.minoffset:
            norm.minoffset = self.offset
        if self.offset > norm.maxoffset:
            norm.maxoffset = self.offset
        self.norm = norm
        self.rule = rule
    def insertxml(self, tk, newxml):
        if newxml is not None:
            # if its a break tag it goes after
            newtag = copy.deepcopy(newxml)
            if self.newxml.tag == 'break':
                p = tk.getparent()
                p.insert(p.index(tk)+1, newtag)
            # otherwise put it around the tag
            else:
                p = tk.getparent()
                idx = p.index(tk)
                newtag.append(tk)
                p.insert(idx, newtag)
    def apply(self, matches, pos, tokens):
        pass

#TODO: add code to deal with XML adding etc. (stray hypen for example).
class FixedReplace(Replace):
    value = None
    def __init__(self, norm, rule, xml):
        Replace.__init__(self, norm, rule, 'fixed', xml)
        self.value = xml.get('val')
    def apply(self, matches, pos, tokens, replaces):
        if pos + self.offset < 0 or pos + self.offset >= len(tokens):
            return
        tk = tokens[pos + self.offset]
        # if just alters XMl on token val may not be set
        val = None
        if self.value:
            val = self.value
        elif self.value == '':
            val = ''
        elif self.fromoffset != None:
            if self.fromgroup > 0:
                val = matches[self.fromoffset][self.fromgroup]
            else:
                val = matches[self.fromoffset][0]
        if val != None:
            if str(self.offset) in replaces:
                replaces[str(self.offset)] = replaces[str(self.offset)] + ' ' + \
                                             val             
            else:
                replaces[str(self.offset)] = val
                tk.set('isnrm', 'true')
            # if tk.get('isnrm'):
            #     newtk = etree.Element('tk')
            #     newtk.set('nnorm', val)
            #     tk.append(newtk)
            # else:
            #     tk.set('isnrm', 'true')
            #     tk.set('nnorm',  val)
        # check for new xml to add to output
        self.insertxml(tk, self.newxml)
        
class LookupReplace(Replace):
    lkpname = None
    def __init__(self, norm, rule, xml):
        Replace.__init__(self, norm, rule, 'lookup', xml)
        self.lkpname = xml.get('name')
    def apply(self, matches, pos, tokens, replaces):
        if self.lkpname not in self.norm.lkps:
            #sys.stderr.write('WARNING Bad replace component:' + self.lkpname)
            return
        if pos + self.offset < 0 or pos + self.offset >= len(tokens):
            return
        tk = tokens[pos + self.offset]
        if self.fromgroup > 0:
            if self.fromgroup < len(matches[self.fromoffset]):
                key = matches[self.fromoffset][self.fromgroup]
            else:
                #sys.stderr.write('WARNING Bad replace component: + no group %d in regex result' % self.fromgroup)
                return
        else:
            key = matches[self.fromoffset][0]
        #print (key.__repr__())
        if key in self.norm.lkps[self.lkpname]:
            # mark that token is normalised
            if str(self.offset) in replaces:
                replaces[str(self.offset)] = replaces[str(self.offset)] + ' ' + \
                                             self.norm.lkps[self.lkpname][key]             
            else:
                replaces[str(self.offset)] = self.norm.lkps[self.lkpname][key]
                tk.set('isnrm', 'true')
            # if tk.get('isnrm'):
            #     newtk = etree.Element('tk')
            #     newtk.set('nnorm', self.norm.lkps[self.lkpname][key])
            #     tk.append(newtk)
            # else:
            #     tk.set('isnrm', 'true')
            #     tk.set('nnorm',  self.norm.lkps[self.lkpname][key])
        self.insertxml(tk, self.newxml)
                
class FuncReplace(Replace):
    fncname = None
    def __init__(self, norm, rule, xml):
        self.args = {}
        Replace.__init__(self, norm, rule, 'func', xml)
        # print etree.tostring(xml)
        self.fncname = xml.get('name')
        # add any preset arguments
        # print self.fncname, self.norm.functions
        defaultargs = self.norm.functions[self.fncname]
        for key in defaultargs.keys():
            self.args[key] = defaultargs[key]
        for att in xml.keys():
            # all other attributes are arguments for the function
            if att not in ['name', 'from', 'grp', 'offset']:
                self.args[att] = xml.get(att)
    def apply(self, matches, pos, tokens, replaces):
        if self.fncname not in NORMFUNCS:
            #sys.stderr.write('WARNING Bad replace component:' + self.lkpname)
            return
        if pos + self.offset < 0 or pos + self.offset >= len(tokens):
            return
        tk = tokens[pos + self.offset]
        if self.fromgroup > 0:
            if self.fromgroup < len(matches[self.fromoffset]):
                input = matches[self.fromoffset][self.fromgroup]
            else:
                #sys.stderr.write('WARNING Bad replace component: + no group %d in regex result' % self.fromgroup)
                return
        else:
            input = matches[self.fromoffset][0]
        #print ('-', input.__repr__(), self.rule.name)
        if input is not None:
            if str(self.offset) in replaces:
                replaces[str(self.offset)] = replaces[str(self.offset)] + ' ' + \
                                             NORMFUNCS[self.fncname](self.norm, input, self.args)
            else:
                replaces[str(self.offset)] = NORMFUNCS[self.fncname](self.norm, input, self.args)
                tk.set('isnrm', 'true')
            # if tk.get('isnrm'):
            #     newtk = etree.Element('tk')
            #     newtk.set('nnorm', NORMFUNCS[self.fncname](self.norm, input, self.args))
            #     tk.append(newtk)
            # else:
            #     tk.set('isnrm', 'true')
            #     tk.set('nnorm',  NORMFUNCS[self.fncname](self.norm, input, self.args))
        self.insertxml(tk, self.newxml)
        
class XmlReplace(Replace):
    maptag = None
    totag = None
    mapatt = None
    toatt = None
    atts = None
    def __init__(self, norm, rule, xml):
        Replace.__init__(self, norm, rule, 'xml', xml)
        self.fncname = xml.get('name')
        self.maptag = xml.get('maptag')
        self.totag = xml.get('totag')
        self.mapatt = xml.get('mapatt')
        self.toatt = xml.get('toatt')
        # all other attributes are copied onto the token
        self.atts = {}
        for att in xml.keys():
            if att not in ['name', 'from', 'grp', 'offset', 'maptag', 'totag', 'mapatt', 'toatt']:
                self.atts[att] = xml.get(att)
    def apply(self, matches, pos, tokens, replaces):
        if pos + self.offset < 0 or pos + self.offset >= len(tokens):
            return
        tk = tokens[pos + self.offset]
        # find the tag we are mapping if present
        p = tk.getparent()
        #print ('!!', etree.tostring(p))
        while(p is not None):
            #print ('!!', p.tag, self.maptag)
            if p.tag == self.maptag:
                break
            p = p.getparent()
        if p is not None and p.getparent() is not None: # not root node!
            newtag = etree.Element(self.totag)
            # copy attribs appropriately to new tag
            for att in p.keys():
                val = p.get(att)
                if att == self.mapatt:
                    att = self.toatt
                newtag.set(att, val)
            for att in self.atts.keys():
                #print (att, self.atts[att])
                newtag.set(att, self.atts[att])
            # replace parent
            #print ('!!', etree.tostring(p))
            pp = p.getparent()
            idx = pp.index(p)
            for c in p.getchildren():
                newtag.append(c)
            pp.replace(p, newtag)
        self.insertxml(tk, self.newxml)
        
class Rule:
    name = ''
    comment = ''
    matches = []
    replaces = []
    def __init__(self, name, comment):
         self.name = name
         self.comment = comment
         self.matches = []
         self.replaces = []
    def append_match(self, matched):
         self.matches.append(matched)
    def append_replace(self, replace):
         self.replaces.append(replace)
    def apply(self, pos, tokens):
        matches = []
        for m in self.matches:
            matched, groups = m.apply(pos, tokens)
            if not matched:
                return False
            else:
                matches.append(groups)
        #print (self.name, 'matched', matches)
        replaces = {}
        for r in self.replaces:
            r.apply(matches, pos, tokens, replaces)
        for offset in replaces:
            tk = tokens[pos + int(offset)]
            tk.set('nnorm', replaces[offset])
        return True
    
class Normrules:
    maxrulewin = 0
    rulesequence = []
    functions = {}
    rules = {}
    rgxs = {}
    lkps = {}
    minoffset = 0
    maxoffset = 0
    
    def __init__(self, ruledir):
        self.read_normmaster(ruledir)
        self.readrgxs(ruledir)
        self.readlkps(ruledir)
        for setname in self.rulesequence:
            self.rules[setname] = self.readruleset(ruledir, setname)
    
    def read_normmaster(self, ruledir):
        masterxml = etree.parse(ruledir + '/master.xml')
        rulesetxml = masterxml.find('ruleset').findall("rs")
        for rs in rulesetxml:
            self.rulesequence.append(rs.get('name'))
        funcxml = masterxml.find('replacefunction').findall("function")
        for func in funcxml:
            args = {}
            for att in func.keys():
                args[att] = func.get('att')
            self.functions[func.get('name')] = args

    def readruleset(self, ruledir, setname):
        setxml = etree.parse(ruledir + '/' + setname + '.xml')
        rulesetxml = setxml.find('rules').findall("rule")
        ruleset = []
        for rulexml in rulesetxml:
            rule = Rule(rulexml.get('name'), rulexml.find('comment').text)
            for matched in rulexml.find('match').getchildren():
                if matched.tag == 'rgx':
                    rule.append_match(RgxMatch(self, rule, matched))
                elif  matched.tag == 'xml':
                    rule.append_match(XmlMatch(self, rule, matched))
                else:
                    sys.stderr.write('WARNING Bad match component:' + etree.tostring(matched))
            for rep in rulexml.find('replace').getchildren():
                if rep.tag == 'cpy':
                    rule.append_replace(FixedReplace(self, rule, rep))
                elif rep.tag == 'lkp':
                    rule.append_replace(LookupReplace(self, rule, rep))
                elif rep.tag == 'fnc':
                    rule.append_replace(FuncReplace(self, rule, rep))
                elif rep.tag == 'xml':
                    rule.append_replace(XmlReplace(self, rule, rep))
            ruleset.append(rule)
        return ruleset
        
    def readrgxs(self, ruledir):
        parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)
        regularexpressionsxml = etree.parse(ruledir + '/regularexpressions.xml', parser=parser)
        for rgx in regularexpressionsxml.find('regexs').findall('regex'):
            try:
                self.rgxs[rgx.get('name')] = compile(rgx.find('exp').text)
            except:
                sys.stderr.write('WARNING Bad regex: %s %s \n' % (rgx.get('name'), rgx.find('exp').text)) 
        
    def readlkps(self, ruledir):
         parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)
         lkptablesxml = etree.parse(ruledir + '/lookuptables.xml', parser=parser)
         for lkp in lkptablesxml.find('tables').findall('lookup'):
             table, baditem = parselookup(lkp.find('exp').text)
             if not table:
                 sys.stderr.write('WARNING Bad lookup: %s\n' % (lkp.get('name')))
             else:
                 self.lkps[lkp.get('name')] = table
                 
    def runrulesets(self, tokens):
        for ruleset in self.rulesequence:
            for i, tk in enumerate(tokens):
                #if tk.tag == 'tk' and not tk.get('isnrm'):
                if tk.tag == 'tk' and (tk.get('nnorm') == None or not match('^[a-z ]*$', tk.get('nnorm')) or ruleset[:4] == 'ssml'):
                    for rule in self.rules[ruleset]:
                        tokensxml = []
                        for tk in tokens:
                            tokensxml.append(etree.tostring(tk, pretty_print=True, encoding='UTF-8').strip())
                        
                        matched = rule.apply(i, tokens)
                        if matched:
                            newtokensxml = []
                            for tk in tokens:
                                newtokensxml.append(etree.tostring(tk, pretty_print=True, encoding='UTF-8').strip())
                            break
                           
                           
class Normalise(object):
    lang = ""
    acc = ""
    spk = ""
    region = ""
    arch = ""
    tpdb = ""
    ruledir = ""
    
    def __init__(self, idargs):
        """ Creates the Normalise object and finds 
            the location of normaliser rules """
        if type(idargs) != idargparse.TxpArgumentParser:
            raise ValueError("idargs must be a TxpArgumentParser")
        
        config = pytxplib.PyTxpParseOptions_GetConfig(idargs.idlakopts)
        if 'general-lang' in config:
            self.lang = config['general-lang']
        if 'general-acc' in config:
            self.acc = config['general-acc']
        if 'general-spk' in config:
            self.spk = config['general-spk']
        if 'general-region' in config:
            self.region = config['general-region']
        if 'normalise-arch' in config:
            self.arch = config['normalise-arch']
        self.tpdb = pyIdlak_txp.PyTxpParseOptions_GetTpdb(idargs.idlakopts)
            
        # Getting possible directories
        lastdir = [ 'normrules-' + self.arch, 'normrules-default' ]
        paths = []
        if self.spk != "" and self.acc != "" and self.lang != "":
            paths.append(os.path.join(self.lang, self.acc, self.spk))
        if self.acc != "" and self.lang != "":
            paths.append(os.path.join(self.lang, self.acc))
        if self.region != "" and self.lang != "":
            paths.append(os.path.join(self.lang, self.region))
        if self.lang != "":
            paths.append(self.lang)
        
        # Find existing directory
        for last in lastdir:
            if self.ruledir != "":
                break
            for middle_dir in paths:
                path = os.path.join(self.tpdb, middle_dir, last)
                if os.path.exists(path):
                    self.ruledir = path
                    break
        
        if self.ruledir == "" and lastdir[0] == lastdir[1]:
            raise NameError("Directory for normaliser rules (\"" + lastdir[0] +"\") could not be found.")
        elif self.ruledir == "":
            raise NameError("Directory for normaliser rules (\"" + lastdir[0] + "\" or \"" + lastdir[1] + "\") could not be found.")
        
        # getting file path of hrules and importing hardcoded rules
        lastdir = [ 'hrules-' + self.arch + '.py', 'hrules-default.py' ]
        hrule_filename = ""
        for last in lastdir:
            if hrule_filename != "":
                break
            for middle_dir in paths:
                path = os.path.join(self.tpdb, middle_dir, last)
                if os.path.exists(path):
                    hrule_filename = path
                    break
        if hrule_filename == "" and lastdir[0] == lastdir[1]:
            sys.stderr.write('WARNING No hardcoded functions provided. Functions should be provided in %s file. Assuming the normaliser doesn\'t need them. \n' % (lastdir[0]))
        elif hrule_filename == "":
            sys.stderr.write('WARNING No hardcoded functions provided. Functions should be provided in %s or %s file. Assuming the normaliser doesn\'t need them. \n' % (lastdir[0], lastdir[1]))
        else:
            importhrules(hrule_filename)
        
    def process(self, doc):
        """ process the document in place """
        if not type(doc) is xmldoc.XMLDoc:
            raise ValueError("doc must be a XMLDoc")
        
        # xmldoc to lxml
        strin = doc.to_string()
        xmlin = etree.fromstring(strin)
        
        normrules = Normrules(self.ruledir)
        tokens = xmlin.xpath('.//tk|.//break')
        normrules.runrulesets(tokens)        
        
        # lxml to xmldoc
        strout = str(etree.tostring(xmlin, encoding='utf8').decode('utf8'))
        doc.load_string(strout)
