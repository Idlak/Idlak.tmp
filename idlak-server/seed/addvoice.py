import sys
import argparse
import xmltodict
from app import app, db
from app.models.voice import Voice

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('../')

parser = argparse.ArgumentParser(description='Add a voice to the database.')
parser.add_argument('-i', help='id of the voice')
parser.add_argument('-d', help='path of the directory containing voice configuration file')

args = vars(parser.parse_args())
errs = ""
if args['i'] is None:
    errs += ", id"
if args['d'] is None:
    errs += ", directory"

if len(errs) > 0:
    errs = errs[2:]
    print("Please provide {} of the voice".format(errs))
    sys.exit()
    
voice_id = args['i']
conf_file_dir = args['d']
conf_file_name = conf_file_dir + voice_id + '_conf.xml'
conf_file = None
with open(conf_file_name) as fd:
    conf_file = xmltodict.parse(fd.read())

conf_file = conf_file['conf']
language = conf_file['globals']['@lang']
accent = conf_file['globals']['@acc']
#main_dir = '/'.join(conf_file_dir.split('/')[:-2]) + '/'
#audiodir = main_dir + conf_file['globals']['@audiodir']
#cachedir = main_dir + conf_file['globals']['@cachedir']
#dbdir = main_dir + conf_file['globals']['@dbdir']
#toolsdir = main_dir + conf_file['globals']['@toolsdir']
#lexdir = main_dir + conf_file['globals']['@lexdir']
name = conf_file['vce']['options']['header']['@VOICE_NAME']
gender = conf_file['vce']['options']['header']['@SEX']
lang_name = conf_file['vce']['options']['header']['@LANGUAGE']
country = conf_file['vce']['options']['header']['@COUNTRY']

voice = Voice.new_voice(voice_id, name, language, accent, gender, conf_file_dir, lang_name, country)
if type(voice) is dict and 'error' in voice:
    print voice['error'] + ':'
    print voice['voice']
else:
    print(voice)