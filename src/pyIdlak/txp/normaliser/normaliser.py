# -*- coding: utf-8 -*-
# prototype normaliser for Idlak
import sys
import os
import traceback
import copy
import pdb
import importlib.util
from pprint import pformat
from lxml import etree, objectify
from xml.sax.saxutils import escape
from re import match, compile
from .. import idargparse, xmldoc, pyIdlak_txp, pytxplib

validmatchtypes = ['rgx', 'xml']
validreplacetypes = ['fixed', 'lookup', 'func', 'xml']
validsrc = ['lcase', 'mcase', 'pos']


def loadhrules(hrules_fn):
    spec = importlib.util.spec_from_file_location("hrules", hrules_fn)
    hrules_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hrules_module)
    return hrules_module.NORMFUNCS


def getlkpitem(items):
    match_rgx1 = "\s*[\'\"](.+?)[\'\"]\s*:\s*[\'\"](.*)[\'\"]\s*,\s*(.*)"
    match_rgx2 = "\s*[\'\"](.+?)[\'\"]\s*:\s*[\'\"](.*)[\'\"]\s*"
    matched = match(match_rgx, items)
    if not matched:
        matched = match(match_rgx2, items)
    return matched


def parselookup(lkptext):
    try:
        # eval automatically converts unicode into ascii so
        # we have to decode it again.
        lkp_encode = eval(lkptext)
        lkp = {}
        for k in lkp_encode.keys():
            lkp[k] = lkp_encode[k]
    except SyntaxError:
        type, value, tb = sys.exc_info()
        traceback.print_exception(type, value, tb)
        return {}, None
    except TypeError:
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


def gettagup(tk, tag):
    # search up the tree for a specific tag
    parent = tk.getparent()
    while parent:
        if parent.tag == tag:
            return parent
        parent = tk.getparent()
    return None


class Match:

    def __init__(self, norm, rule, type, xml):
        if type not in validmatchtypes:
            sys.stderr.write('WARNING Bad match component:' +
                             etree.tostring(xml))
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

    def __init__(self, norm, rule, xml):
        Match.__init__(self, norm, rule, 'rgx', xml)
        self.rgxname = xml.get('name')

    def apply(self, pos, tokens):
        if pos + self.offset < 0:
            return False, []
        if pos + self.offset >= len(tokens):
            return False, []
        if self.rgxname not in self.norm.rgxs:
            return False, []
        if self.src == 'lcase':
            val = tokens[pos + self.offset].get('norm')
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
            if tokens[pos + self.offset].text:
                matched = match(self.norm.rgxs[self.rgxname],
                                (tokens[pos + self.offset].text).strip())
            else:
                return False, []
            if matched:
                if not len(matched.groups()):
                    return True, [matched.group(0)]
                else:
                    return True, matched.groups()
            else:
                return False, []


class XmlMatch(Match):
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
            starttag = False if tag else starttag
        psttk = getpsttk(tokens, pos + self.offset)
        if psttk is not None:
            tag = psttk.xpath('ancestor::' + self.xmltag)
            endtag = False if tag else endtag
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
                    if not intag[0].get(self.xmlatt) == self.xmlval:
                        return False, []
        return True, [tokens[pos + self.offset].get('norm')]


class Replace:
    def __init__(self, norm, rule, type, xml):
        if type not in validreplacetypes:
            sys.stderr.write('WARNING Bad replace component:' +
                             etree.tostring(xml))
            return
        self.type = type
        self.fromgroup = int(xml.get('grp')) if xml.get('grp') else -1
        if type == 'fixed' and xml.get('val'):
            if xml.get('from'):
                sys.stderr.write('WARNING Bad replace component ' +
                                 '(fixed value taking from value):' +
                                 etree.tostring(xml))
        self.fromoffset = int(xml.get('from')[1:]) if xml.get('from') else None
        newxml = xml.getchildren()
        if len(newxml) > 1:
            sys.stderr.write('WARNING Bad replace component ' +
                             '(odd replace xml):' + etree.tostring(xml))
        elif len(newxml) > 0:
            self.newxml = newxml[0]
        else:
            self.newxml = None
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


# TODO: add code to deal with XML adding etc. (stray hypen for example).
class FixedReplace(Replace):
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
        elif self.fromoffset is not None:
            if self.fromgroup > 0:
                val = matches[self.fromoffset][self.fromgroup]
            else:
                val = matches[self.fromoffset][0]
        if val is not None:
            if str(self.offset) in replaces:
                replaces[str(self.offset)] = (replaces[str(self.offset)] +
                                              ' ' + val)
            else:
                replaces[str(self.offset)] = val
                tk.set('isnrm', 'true')
        # check for new xml to add to output
        self.insertxml(tk, self.newxml)


class LookupReplace(Replace):
    def __init__(self, norm, rule, xml):
        Replace.__init__(self, norm, rule, 'lookup', xml)
        self.lkpname = xml.get('name')

    def apply(self, matches, pos, tokens, replaces):
        if self.lkpname not in self.norm.lkps:
            return
        if pos + self.offset < 0 or pos + self.offset >= len(tokens):
            return
        tk = tokens[pos + self.offset]
        if self.fromgroup > 0:
            if self.fromgroup < len(matches[self.fromoffset]):
                key = matches[self.fromoffset][self.fromgroup]
            else:
                # sys.stderr.write('WARNING Bad replace component: + no ' +
                #                  'group %d in regex result' % self.fromgroup)
                return
        else:
            key = matches[self.fromoffset][0]
        if key in self.norm.lkps[self.lkpname]:
            # mark that token is normalised
            if str(self.offset) in replaces:
                to_replace = (replaces[str(self.offset)] + ' ' +
                              self.norm.lkps[self.lkpname][key])
                replaces[str(self.offset)] = to_replace

            else:
                replaces[str(self.offset)] = self.norm.lkps[self.lkpname][key]
                tk.set('isnrm', 'true')
        self.insertxml(tk, self.newxml)


class FuncReplace(Replace):
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
        if self.fncname not in self.norm.hrules:
            # sys.stderr.write('WARNING Bad replace component:' + self.lkpname)
            return
        if pos + self.offset < 0 or pos + self.offset >= len(tokens):
            return
        tk = tokens[pos + self.offset]
        if self.fromgroup > 0:
            if self.fromgroup < len(matches[self.fromoffset]):
                input = matches[self.fromoffset][self.fromgroup]
            else:
                # sys.stderr.write('WARNING Bad replace component: + no ' +
                #                  'group %d in regex result' % self.fromgroup)
                return
        else:
            input = matches[self.fromoffset][0]
        if input is not None:
            to_replace = self.norm.hrules[self.fncname](self.norm,
                                                        input,
                                                        self.args)
            if str(self.offset) in replaces:
                replaces[str(self.offset)] = (replaces[str(self.offset)] +
                                              ' ' + to_replace)
            else:
                replaces[str(self.offset)] = to_replace
                tk.set('isnrm', 'true')
        self.insertxml(tk, self.newxml)


class XmlReplace(Replace):
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
            if att not in ['name', 'from', 'grp', 'offset', 'maptag',
                           'totag', 'mapatt', 'toatt']:
                self.atts[att] = xml.get(att)

    def apply(self, matches, pos, tokens, replaces):
        if pos + self.offset < 0 or pos + self.offset >= len(tokens):
            return
        tk = tokens[pos + self.offset]
        # find the tag we are mapping if present
        p = tk.getparent()
        while(p is not None):
            if p.tag == self.maptag:
                break
            p = p.getparent()
        if p is not None and p.getparent() is not None:  # not root node!
            newtag = etree.Element(self.totag)
            # copy attribs appropriately to new tag
            for att in p.keys():
                val = p.get(att)
                if att == self.mapatt:
                    att = self.toatt
                newtag.set(att, val)
            for att in self.atts.keys():
                newtag.set(att, self.atts[att])
            # replace parent
            pp = p.getparent()
            idx = pp.index(p)
            for c in p.getchildren():
                newtag.append(c)
            pp.replace(p, newtag)
        self.insertxml(tk, self.newxml)


class Rule:
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

        replaces = {}
        for r in self.replaces:
            r.apply(matches, pos, tokens, replaces)
        for offset in replaces:
            tk = tokens[pos + int(offset)]
            tk.set('nnorm', replaces[offset])
        return True


class Normrules:
    def __init__(self, ruledir, hrules):
        self.minoffset = 0
        self.maxoffset = 0
        self.rulesequence = []
        self.functions = {}
        self.read_normmaster(ruledir)
        self.rgxs = {}
        self.readrgxs(ruledir)
        self.lkps = {}
        self.readlkps(ruledir)
        self.rules = {}
        for setname in self.rulesequence:
            self.rules[setname] = self.readruleset(ruledir, setname)
        self.hrules = hrules

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
                elif matched.tag == 'xml':
                    rule.append_match(XmlMatch(self, rule, matched))
                else:
                    sys.stderr.write('WARNING Bad match component:' +
                                     etree.tostring(matched))
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
        regularexpressionsxml = etree.parse((ruledir +
                                             '/regularexpressions.xml'),
                                            parser=parser)
        for rgx in regularexpressionsxml.find('regexs').findall('regex'):
            try:
                self.rgxs[rgx.get('name')] = compile(rgx.find('exp').text)
            except:
                sys.stderr.write(('WARNING Bad regex: ' +
                                  '%s %s \n' % (rgx.get('name')),
                                 rgx.find('exp').text))

    def readlkps(self, ruledir):
        parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)
        lkptablesxml = etree.parse(ruledir + '/lookuptables.xml',
                                   parser=parser)
        for lkp in lkptablesxml.find('tables').findall('lookup'):
            table, baditem = parselookup(lkp.find('exp').text)
            if not table:
                sys.stderr.write('WARNING Bad lookup: ' +
                                 '%s\n' % (lkp.get('name')))
            else:
                self.lkps[lkp.get('name')] = table

    def runrulesets(self, tokens):
        for ruleset in self.rulesequence:
            for i, tk in enumerate(tokens):
                norm_empty = (tk.get('nnorm') is None or
                              not match('^[a-z ]*$', tk.get('nnorm')) or
                              ruleset[:4] == 'ssml')
                if tk.tag == 'tk' and norm_empty:
                    for rule in self.rules[ruleset]:
                        tokensxml = []
                        for tk in tokens:
                            tokensxml.append(etree.tostring(tk,
                                                            pretty_print=True,
                                                            encoding='UTF-8')
                                             .strip())
                        matched = rule.apply(i, tokens)
                        if matched:
                            newtokensxml = []
                            for tk in tokens:
                                ntkstr = etree.tostring(tk,
                                                        pretty_print=True,
                                                        encoding='UTF-8')
                                newtokensxml.append(ntkstr.strip())
                            break


class Normalise(object):
    def __init__(self, idargs):
        """ Creates the Normalise object and finds
            the location of normaliser rules """
        if type(idargs) != idargparse.TxpArgumentParser:
            raise ValueError("idargs must be a TxpArgumentParser")

        config = pytxplib.PyTxpParseOptions_GetConfig(idargs.idlakopts)
        self.lang = config.get('general-lang', '')
        self.acc = config.get('general-acc', '')
        self.spk = config.get('general-spk', '')
        self.region = config.get('general-region', '')
        self.arch = config.get('normalise-arch', '')
        self.tpdb = pyIdlak_txp.PyTxpParseOptions_GetTpdb(idargs.idlakopts)

        # Getting possible directories
        normdir = ['normrules-' + self.arch, 'normrules-default']
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
        self.ruledir = ''
        for last in normdir:
            if self.ruledir != '':
                break
            for middle_dir in paths:
                path = os.path.join(self.tpdb, middle_dir, last)
                if os.path.exists(path):
                    self.ruledir = path
                    break

        if self.ruledir == "" and self.arch == 'default':
            raise NameError("Directory for normaliser rules (\"" + normdir[0] +
                            "\") could not be found.")
        elif self.ruledir == "":
            raise NameError("Directory for normaliser rules (\"" + normdir[0] +
                            "\" or \"" + normdir[1] +
                            "\") could not be found.")

        # getting file path of hrules and importing hardcoded rules
        hrulefn = ['hrules-' + self.arch + '.py', 'hrules-default.py']
        hrule_filename = ""
        for last in hrulefn:
            if hrule_filename != "":
                break
            for middle_dir in paths:
                path = os.path.join(self.tpdb, middle_dir, last)
                if os.path.exists(path):
                    hrule_filename = path
                    break
        self.hrules = []
        if hrule_filename == "" and self.arch == 'default':
            sys.stderr.write('WARNING No hardcoded functions provided. ' +
                             'Functions should be provided in ' +
                             ' %s file.' % (normdir[0]) +
                             ' Assuming the normaliser doesn\'t need them. \n')
        elif hrule_filename == "":
            sys.stderr.write('WARNING No hardcoded functions provided. ' +
                             'Functions should be provided in ' +
                             '%s or %s files. ' % (normdir[0], normdir[1]) +
                             'Assuming the normaliser doesn\'t need them. \n')
        else:
            self.hrules = loadhrules(hrule_filename)

    def process(self, doc):
        """ process the document in place """
        if not type(doc) is xmldoc.XMLDoc:
            raise ValueError("doc must be a XMLDoc")

        # xmldoc to lxml
        strin = str(doc.to_string())
        xmlin = etree.fromstring(strin)

        normrules = Normrules(self.ruledir, self.hrules)
        tokens = xmlin.xpath('.//tk|.//break')
        normrules.runrulesets(tokens)

        for tk in tokens:
            if 'nnorm' not in tk.attrib:
                tk.set('nnorm', tk.get('norm'))

        # lxml to xmldoc
        strout = str(etree.tostring(xmlin, encoding='utf8').decode('utf8'))
        doc.load_string(strout)
