<<<<<<< HEAD
from app import api, jwt
from flask_restful import Resource, reqparse, abort, request

spch_parser = reqparse.RequestParser()
spch_parser.add_argument('voice_id', help='voice id', location='json', required=True)
spch_parser.add_argument('streaming', choices=['true','false'], \
	help='true|false, default=false', location='json')
spch_parser.add_argument('audio_format', choices=['wav|ogg|mp3'], \
	help='wav|ogg|mp3, default=wav', location='json')
spch_parser.add_argument('text', help='text to syntesise speech', location='json', required=True)


class Speech(Resource):
	def post(self):
		# get available voices
		return "get synthesise speech"
=======
# -*- coding: utf-8 -*-
import subprocess
import sys
import os
import uuid
import time
from app import app, api, jwt
from flask import send_from_directory
from flask_restful import Resource, reqparse, abort, request
from flask_jwt_simple import jwt_required
from app.models.voice import Voice

reload(sys)
sys.setdefaultencoding("utf-8")

spch_parser = reqparse.RequestParser()
spch_parser.add_argument('voice_id', help='voice id', location='json', required=True)
spch_parser.add_argument('audio_format', choices=['wav','ogg','mp3'], \
    help='wav|ogg|mp3, default=wav', location='json')
spch_parser.add_argument('text', help='text to syntesise speech', location='json', required=True)

def convertTo(audio_format, filename):
    """ Converts a wav audio file into a provided audio format
    
        Args:
            audio_format (str): format of audio (assuming correct - ogg|mp3)
            filename (str): path of the file with its name 
                            (assuming has extension of wav file)
            
        Returns: 
            (str): filename of the converted file
    """
    new_filename = filename[:-3] + audio_format
    command = "ffmpeg -i {} {}".format(filename, new_filename)
    return_code = subprocess.call(command, shell=True)
    return new_filename

def removeOldOutputFiles():
    """ Removes an output folder if it is older than 5 minutes """
    path = "output/"
    current_time = time.time() - 300
    for filename in os.listdir(path):
        if os.stat(path + filename).st_mtime < current_time:
            subprocess.call("rm -rf " + path + filename, shell=True)
            app.logger.info("Directory \"" + path + filename + "\" was deleted because it wasn't necessary anymore.")
        

class Speech(Resource):
    decorators = [jwt_required]
    def post(self):
        """ Speech endpoint
        
            Args:
                voice_id (str): id of the voice
                audio_format (str, optional): wav|ogg|mp3 - assume is correct
                text (str): text to process
                
            Returns: 
                streamed audio file of the processed speech
        """
        args = spch_parser.parse_args()
        voice = Voice.query.filter_by(id=args['voice_id']).first()
        if voice is None:
            return {"message":"Voice could not be found"}, 400
        
        removeOldOutputFiles()
        
        # set the current path to where the speech files are for the processing
        current_path = os.getcwd()
        os.chdir(app.config['SPEECH_PATH'])
                
        app.logger.info("PROCESSING SPEECH:\nVoice id: {}\nText: {}".format(voice.id, args['text']))
        voice_dir = "voices/{}/{}/{}_pmdl".format(voice.language, voice.accent, voice.id)
        output_dir = current_path + "/output/" + uuid.uuid4().hex[:8] 
        
        command = "echo {} | local/synthesis_voice_pitch.sh {} {}".format(args['text'], voice_dir, output_dir)
        return_code = subprocess.call(command, shell=True)
        if return_code == 0:
            app.logger.info("Processing went through successfully, the audio files have been stored in " + output_dir)
        else:
            app.logger.error("PROCESSING FAILED!!!")
            os.chdir(current_path)
            return {"message":"The process has failed"}, 400
        
        # remove temporary files of the user after processing
        if 'CURRENT_USER' in app.config:
            subprocess.call("ls -l /tmp | grep \"" + app.config['CURRENT_USER'] + ".*tmp*\" | awk '{print \"/tmp/\"$NF}' | xargs rm -rf", shell=True)
            app.logger.info("Deleted temporary processing files")
        
        # change the path to the path of this program to
        # continue on converting the file if necessary
        os.chdir(current_path)
        
        output_dir += "/wav_mlpg/"
        audio_file = "test001.wav"
                
        if not os.path.isfile(output_dir + audio_file):
            app.logger.error("PROCESSING FAILED: no audio file has been found!!!")
            return {"message":"The process has failed"}, 400
        
        # check if the audio file needs to be converted
        if args['audio_format'] is not None and args['audio_format'] != "wav":
            audio_file = convertTo(args['audio_format'], output_dir + audio_file)
            audio_file = audio_file.split('/')[len(audio_file.split('/'))-1]
            app.logger.info("Audio file has been converted to " + args['audio_format'])
                
        return send_from_directory(output_dir, audio_file)
>>>>>>> 0d65f968c7b8ecc9c1080ae5cae487ba38fc8210


api.add_resource(Speech, '/speech')
