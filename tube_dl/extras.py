import requests
import re
import os
import eyed3
try:
    import moviepy.editor as converter
except:
    print('MoviePy is required to continue.')
    import subprocess
    subprocess.call('pip install moviepy --no-deps')
class Convert:
    def __init__(self,meta,filename:str,thumbnail:str,extension,Type):
        self.thumbnail = thumbnail
        if Type.lower() == 'audio':
            self.convert_audio(meta,filename,extension)
        else:
            print('Option Coming Soon to convert videofile')
            #self.convert_video(filename,extension)

    def convert_audio(self,meta,audio_file:str,ext):
        clip = converter.AudioFileClip(audio_file)
        default_ext = audio_file.split('.')[-1]
        clip.write_audiofile(audio_file.replace(default_ext,ext))
        if default_ext != ext:
            os.remove(audio_file)
        audio = eyed3.load(audio_file)
        if type(details) == dict:
            details = meta.keys()
            if 'Artist' in details:
                audio.tag.artist =  meta['Artist']
            if 'Song' in details:
                audio.tag.title =  meta['Song']
            if 'Album' in details:
                audio.tag.album =  meta['Album']
            else:
                try:
                    audio.tag.album = meta['Song']
                except:
                    pass
        else:
            for i in meta.split('\n'):
                if 'singer' in i.lower():
                    a = i.split(':')
                    b = i.split('-')
                    if len( a == 2) & a[0].replace(' ','').lower() == 'singer':
                        audio.tag.artist = a[-1]
                    elif len( b == 2) & b[0].replace(' ','').lower() == 'singer':
                        audio.tag.artist = b[-1]
                if 'film' or 'movie' or 'album' in i.lower():
                    a = i.split(':')
                    b = i.split('-')
                    if len( a == 2) & a[0].replace(' ','').lower() == 'film' or 'movie' or 'album':
                        audio.tag.album = a[-1]
                    elif len( b == 2) & b[0].replace(' ','').lower() == 'film' or 'movie' or 'album':
                        audio.tag.album = b[-1]  
                    else:
                        audio.tag.album = audio.tag.title   
        audio.tag.images.set(3, requests.get(self.thumbnail).content, 'image/jpeg')
        audio.tag.save(version=eyed3.id3.ID3_V2_3)
