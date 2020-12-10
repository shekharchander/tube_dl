import requests
import re
import os
import eyed3
headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        }
try:
    import moviepy.editor as converter
except:
    print('MoviePy is required to continue.')
    import subprocess
    subprocess.call('pip install moviepy --no-deps')
class Spotify:
    def __init__(self):
        headers['authorization'] = self.get_access_token()
    def get_access_token(self):
        token = requests.get('https://open.spotify.com/get_access_token?reason=transport&productType=web_player',headers = headers).json()['accessToken']
        return f'Bearer {token}'
    def search(self,query,limit=20):
        link = f'https://api.spotify.com/v1/search?type=track&query={query.replace(" ","+")}&limit={limit}'
        data = requests.get(link,headers = headers).json()
        songs_list = list()
        for i in data['tracks']['items']:
            songs_list.append(i)
        return songs_list
class Convert:
    def __init__(self,filename:str,category,description,extension):
        self.category = category
        if self.category.lower() == 'music' or extension.replace('.','') == 'mp3':
            self.convert_audio(filename,extension,description)
        else:
            print('Option Coming Soon to convert videofile')
            #self.convert_video(filename,extension)

    def convert_audio(self,audio_file:str,ext,desc):
        stopwords = ['full','video','song','lyric','lyrics','-','lyrical','']
        clip = converter.AudioFileClip(audio_file)
        default_ext = audio_file.split('.')[-1]
        clip.write_audiofile(audio_file.replace(default_ext,ext))
        if default_ext != ext:
            os.remove(audio_file)
        audio_file = audio_file.replace(default_ext,ext)
        audio_query = ''.join(audio_file.replace('(','||').replace(')','||').split('||')[::2])
        search_query = ''
        if type(desc) == dict:
            if 'Song' in desc.keys():
                search_query += desc['Song']
                if 'Artist' in desc.keys():
                    search_query += ' '+desc['Artist'].split(',')[0]
                if desc['Song'] not in audio_query:
                    search_query = ''
        else:
            desc = [d.lower() for d in desc.split('\n') if d != '']
            if 'provided to youtube by' in desc[0]:
                search_query = desc[1].replace('·','')
        if search_query == '':
            search_query = audio_query.split('.')[0].split('\\')[-1].lower()
        search_query = ' '.join([i for i in search_query.split(' ') if i != '' and i not in stopwords][0:3])
        audio_meta = Spotify().search(query = search_query,limit=5)
        audio = eyed3.load(audio_file)
        if len(audio_meta)>=1:
            audio_meta = audio_meta[0]
            audio.tag.artist = ', '.join([j['name'].strip() for j in audio_meta['artists']])
            audio.tag.album = audio_meta['album']['name']
            audio.tag.title = audio_meta['name']
            audio.tag.disc_num = audio_meta['disc_number']
            audio.tag.release_date = audio_meta['album']['release_date']
            audio.tag.track_num = audio_meta['track_number']
            audio.tag.album_artist = ', '.join([j['name'].strip() for j in audio_meta['album']['artists']])
            audio.tag.images.set(3, requests.get(audio_meta['album']['images'][0]['url']).content, 'image/jpeg')
        audio.tag.save(version=eyed3.id3.ID3_V2_3)
