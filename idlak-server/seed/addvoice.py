import sys
import argparse
sys.path.append('../')
from app import app, db
from app.models.voice import Voice

parser = argparse.ArgumentParser(description='Add a voice to the database.')
parser.add_argument('-n', help='name of the voice')
parser.add_argument('-l', help='language the voice is in')
parser.add_argument('-a', help='accent the voice is in')
parser.add_argument('-g', help='voice gender (male|female)')
parser.add_argument('-d', help='path of the directory containing voice files')

args = vars(parser.parse_args())
errs = ""
if args['n'] is None:
    errs += ", name"
if args['l'] is None:
    errs += ", language"
if args['a'] is None:
    errs += ", accent"
if args['g'] is None:
    errs += ", gender"
if args['d'] is None:
    errs += ", directory"

if len(errs) > 0:
    errs = errs[2:]
    print("Please provide {} of the voice".format(errs))
    sys.exit()

voice = Voice.new_voice(args['n'], args['l'], args['a'], args['g'], args['d'])
print(voice)
