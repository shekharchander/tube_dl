import requests
import re
import os
try:
    import moviepy.editor as converter
except:
    raise Exception('moviepy module is needed for this operation. Install it with pip install moviepy')
class Convert:
    def __init__(self,filename:str,extension,Type):
        if Type.lower() == 'audio':
            self.convert_audio(filename,extension)
        else:
            print('Option Coming Soon to convert videofile')
            #self.convert_video(filename,extension)

    def convert_audio(self,audio_file:str,ext):
        clip = converter.AudioFileClip(audio_file)
        default_ext = audio_file.split('.')[-1]
        clip.write_audiofile(audio_file.replace(default_ext,ext))
        if default_ext != ext:
            os.remove(audio_file)
    def convert_video(self,video_file:str,ext):
        clip = converter.VideoFileClip(video_file)
        default_ext = video_file.split('.')[-1]
        clip.write_videofile(video_file.replace(default_ext,ext))
        if default_ext != ext:
            os.remove(video_file)
