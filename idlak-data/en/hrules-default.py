import pdb
from pcre import match
###########################################################################
#                         HARD CODED NORMALISER FUNCTIONS
###########################################################################

###########################
#      ASDIGITS           #
###########################

# Read out digit by digit like a telephone number

def asdigits(norm, string, args):
    result = []
    if 'case' in args and args['case'] is not None:
        lkptable = args['case']
    else:
        lkptable = 'digitlkp'
    for c in string:
        if c in norm.lkps[lkptable]:
            result.append(norm.lkps[lkptable][c])

    return ' '.join(result)

###########################
#      NUMBER             #
###########################

# read standard cardinal number

def number(norm, string, args):
    #pdb.set_trace()
    # set defaults arguments
    #print (args)
    setdefaultarg(args, 'separator', ',')
    setdefaultarg(args, 'leadingzeros', 'f')
    setdefaultarg(args, 'case', 'digitlkp')
    # remove delimiters etc.
    output = []
    string =  posnumbersonly( norm.lkps['digitlkp'], string, args, output)
    # recursive function to turn digits to string
    if string == '':
        return ''
    number_recursive(norm.lkps['digitlkp'], norm.lkps[args['case']], string, args, output)
    return ' '.join(output)

def number_recursive(lkp, lkpcase, string, args, output):
    # check if whole number is present
    if lookup(lkpcase, string):
        output.append(lookup(lkpcase, string))
        return
    n = int(string)
    #print ('#', n)
    # Calculate remainder, if it's less than 100, add an -and-
    n = numberchunk(lkp, lkpcase, n, args, output, 1000000000, 'billion')
    n = numberchunk(lkp, lkpcase, n, args, output, 1000000, 'million')
    n = numberchunk(lkp, lkpcase, n, args, output, 1000, 'thousand')
    n = numberchunk(lkp, lkpcase, n, args, output, 100, 'hundred')

    # now do numbers < 100
    tens = 10 * int(n / 10);
    units = n % 10;
    tensstr = ''
    if tens:
        # check if whole number < 100 is present
        if lookup(lkp, str(n)):
            output.append(lookup(lkp, str(n)))
            return
        if not units:
            if lookup(lkp, str(tens)):
                output.append(lookup(lkpcase, str(tens)))
        else:
            if lookup(lkp, str(tens)):
                output.append(lookup(lkp, str(tens)))

    if units:
        if lookup(lkpcase, str(units)):
            output.append(lookup(lkpcase, str(units)))


def numberchunk(lkp, lkpcase, n, args, output, scale, scalename):
    scalen = int(n / scale);
    remainder = n % scale
    checkn = scalen * scale
    if scalen < 1:
        return n
    # check if whole number is present
    if lookup(lkpcase, str(n)):
        output.append(lookup(lkpcase, str(n)))
        return 0
    # check if whole scale number is present
    if lookup(lkp, str(scalen)):
        output.append(lookup(lkp, str(scalen)))
    else:
        number_recursive(lkp, lkpcase, str(scalen), args, output)
    if remainder:
        output.append(lookup(lkp, scalename))
    else:
        output.append(lookup(lkpcase, scalename))
    if remainder < 100 and remainder > 0:
        # add 'and' as required
        if lookup(lkp, 'hundred_join'):
            output.append(lookup(lkp, 'hundred_join'))
    return remainder

def setdefaultarg(args, key, value):
    if key not in args or args[key] == None:
        args[key] = value

# get rid of separators, read out leading zeros if required and minus
def posnumbersonly(lkp, string, args, output):
    n = ''
    leading = True
    for i, c in enumerate(string):
        # minus handled by rule and should be tokenised separately
        # one result is single '-' in filter returns nothing.
        if i == 0 and c == '-':
            pass
            #output.append(lkp['-'])
        elif c == args['separator']:
            pass
        elif c == '0' and leading and args['leadingzeros'] == 't':
            output.append(lkp['0'])
        elif match('[0-9]', c):
            leading = False
            n = n + c
        else:
            break
    return n

def lookup(lkp, string):
    if string in lkp:
        return lkp[string]
    return None

###########################
#      ROMAN              #
###########################

# read out roman numerals like MCM etc.

def roman(norm, string, args):
    romanlkp = {'I':1, 'V':5, 'X':10, 'L':50, 'C':100, 'D':500, 'M':1000}
    if len(string) == 0: return
    prvn = 0
    pstn = 0
    result = 0
    for idx, c in enumerate(string):
        c = c.upper()
        if c in romanlkp:
            n = romanlkp[c]
            if idx < len(string) - 1 and string[idx + 1].upper() in romanlkp:
                pstn = romanlkp[string[idx + 1].upper()]
            else:
                pstn = 0

        else:
            return string
        # if number after this number is bigger then this is
        # to take away and should be ignored
        #print (prvn, n, pstn)
        if pstn > 0 and n < pstn:
            pass
        elif prvn > 0 and n > prvn:
            result += n - prvn
        else:
            result += n;
        prvn = n
    return number(norm, str(result), args)

###########################
#      ASCHARS            #
###########################

# read out character by character

def aschars(norm, string, args):
    #print 'C', string
    result = []
    if not string:
        return ''
    for c in string:
        if c in norm.lkps['downcase']:
            result.append( norm.lkps['downcase'][c])
        elif c in norm.lkps['symbols']:
            result.append( norm.lkps['symbols'][c])
        elif c in norm.lkps['currency']:
            result.append( norm.lkps['currency'][c])
        elif c in norm.lkps['digitlkp']:
            result.append( norm.lkps['digitlkp'][c])
        else:
            result.append(c)
    return ' '.join(result)

###########################
#      FILTER             #
###########################

# use a mixture of the above to read out a mixed string

def filter(norm, string, args):
    # set defaults arguments
    setdefaultarg(args, 'separator', ',')
    setdefaultarg(args, 'leadingzeros', 'f')
    setdefaultarg(args, 'case', 'digitlkp')
    lkp = norm.lkps[args['case']]
    #print 'F', string
    # split string into numbers, words, and individual symbols and currency chars.
    # then call appropriate fuctions on each.
    type = 'start'
    tokens = []
    types = []
    for c in string:
        if c in lkp:
            if type == 'digit':
                tokens[-1] = tokens[-1] + c
            else:
                type = 'digit'
                tokens.append(c)
                types.append('digit')
        elif c in norm.lkps['symbols']:
            if type == 'symbols':
                tokens[-1] = tokens[-1] + c
            else:
                type = 'symbols'
                tokens.append([c])
                types.append('symbols')
        elif c in norm.lkps['currency']:
            if type == 'currency':
                tokens[-1] = tokens[-1] + c
            else:
                type = 'currency'
                tokens.append(c)
                types.append('currency')
        else:
            if type == 'other':
                tokens[-1] = tokens[-1] + c
            else:
                type = 'other'
                tokens.append(c)
                types.append('other')
    #print (tokens, types)
    results = []
    for i, t in enumerate(tokens):
        if types[i] == 'other':
            if 'acrolkp' in norm.lkps:
                if t in norm.lkps['acrolkp']:
                    results.append(norm.lkps['acrolkp'][t])
            else:
                results.append(t)
        elif types[i] == 'digit':
            # check if it has a symbol inside
            st = 0
            for c_i in range(len(t)):
                if t[c_i] in norm.lkps['symbols']:
                    results.append(number(norm, t[st:c_i], args))
                    st = c_i + 1
                    results.append(lkp[t[c_i]])
            if st < len(t):
                results.append(number(norm, t[st:], args))
        else:
            results.append(aschars(norm, t, args))

    return ' '.join(results)


NORMFUNCS = {'asdigits': asdigits, 'number':number, 'roman':roman, 'aschars': aschars, 'filter': filter}
