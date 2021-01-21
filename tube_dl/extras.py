import requests
try:
    import moviepy.editor as converter
    import eyed3
except ModuleNotFoundError as e:
    print(e)
import os
headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        }


class Output:
    def __init__(self, meta, file_path):
        self.meta = meta
        self.file_path = file_path

    def __repr__(self):
        return f'< Output : Path={self.file_path} >'


class Spotify:
    def __init__(self):
        headers['authorization'] = self.get_access_token()

    def get_access_token(self):
        token = requests.get('https://open.spotify.com/get_access_token?reason=transport&productType=web_player', headers=headers).json()['accessToken']
        return f'Bearer {token}'

    def search(self, query, limit=20):
        link = f'https://api.spotify.com/v1/search?type=track&query={query.replace(" ","+")}&limit={limit}'
        data = requests.get(link, headers=headers).json()
        songs_list = list()
        try:
            for i in data['tracks']['items']:
                songs_list.append(i)
        except Exception:
            pass
        return songs_list


class Merge:
    def __init__(self, video=None, audio=None, result='videoplayback.mp4', keep_original=False):
        video_file = video.file_path
        audio_file = audio.file_path
        a = converter.VideoFileClip(video_file)
        b = converter.AudioFileClip(audio_file)
        a.set_audio(b).write_videofile(result)
        if keep_original is False:
            if result != video:
                os.remove(video_file)
            os.remove(audio_file)


class Convert:
    def __init__(self, media, extension='mp3', add_meta=True, keep_original=False):

        self.keep = keep_original
        self.file = media.file_path
        if extension == 'mp3':
            self.convert_audio(add_meta, self.file, media.meta)
        elif extension == 'mp4':
            self.convert_video(media.file)
        else:
            raise Exception(f'{extension} extension is not supported. Supported extensions : ["mp4","mp3"]')

    def convert_video(self, video_file):
        a = converter.VideoFileClip(video_file)
        a.write_videofile(video_file.replace(video_file.split('.')[-1], 'mp4', -1), codec='mpeg4')
        if self.keep is False:
            os.remove(video_file)

    def convert_audio(self, add_meta, audio_file: str, desc):
        a_file = audio_file
        clip = converter.AudioFileClip(audio_file)
        audio_file = audio_file.replace(audio_file.split('.')[-1], 'mp3', 1)
        clip.write_audiofile(audio_file)
        if self.keep is False:
            os.remove(a_file)
        if add_meta is True:
            stopwords = ['full', 'video', 'song', 'lyric', 'lyrics', '-', 'lyrical', '']
            audio_query = ''.join(audio_file.replace('(', '||').replace(')', '||').split('||')[::2])
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
                    search_query = desc[1].replace('·', '')
            if search_query == '':
                search_query = audio_query.split('.')[0].split('\\')[-1].lower()
            search_query = ' '.join([i for i in search_query.split(' ') if i != '' and i not in stopwords][0:3])
            audio_meta = Spotify().search(query=search_query, limit=5)
            audio = eyed3.load(audio_file)
            if len(audio_meta) >= 1:
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
