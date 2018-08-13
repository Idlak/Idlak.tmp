#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
import argparse
import xmltodict
from app import app, db
from app.models.voice import Voice

""" Example:
./addvoice.py -g female -n Anna -i abr -d /home/skaiste/Documents/Idlak/idlak/idlak-egs/tts_tangle_idlak/s2/voices/ru/ru/abr_pmdl
"""

parser = argparse.ArgumentParser(description='Add a voice to the database.')
parser.add_argument('-i', help='id of the voice')
parser.add_argument('-g', help='gender')
parser.add_argument('-n', help='name')
parser.add_argument('-d', help='path of the directory containing voice configuration file')

def addVoice():
    args = vars(parser.parse_args())
    errs = ""
    if args['i'] is None:
        errs += ", id"
    if args['g'] is None:
        errs += ", gender"
    if args['n'] is None:
        errs += ", name"
    if args['d'] is None:
        errs += ", directory"

    if len(errs) > 0:
        errs = errs[2:]
        print("Please provide {} of the voice".format(errs))
        sys.exit()
        
    conf_file_dir = args['d']
    conf_file_name = conf_file_dir + '/voice.conf'
    conf_file = {}
    with open(conf_file_name) as fd:
        for line in fd.readlines():
            conf_file[line.split('=')[0]] = line.split('=')[1][:-1]

    voice_id = args['i']
    language = conf_file['lng']
    accent = conf_file['acc']
    name = args['n']
    gender = args['g']

    voice = Voice.new_voice(voice_id, name, language, accent, gender, conf_file_dir)
    if type(voice) is dict and 'error' in voice:
        print voice['error'] + ':'
        print voice['voice']
    else:
        print(voice)
        
if __name__ == '__main__':
    addVoice()
