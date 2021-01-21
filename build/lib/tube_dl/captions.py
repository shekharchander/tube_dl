import re
import json
import requests
import time
from urllib.parse import unquote
import os
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/86.0.4240.198 Safari/537.36', 'referer': 'https://youtube.com'}


class Caption:
    def __init__(self,  url,  language=None):
        for i in re.search(r'watch\?v=(.*?)&|youtu.be/(.*?)&', url+'&').groups():
            if i is not None:
                vid = i
                break
        url = 'https://youtube.com/watch?v='+vid
        html = unquote(requests.get(url, headers=headers).text).replace('\\"', '"')
        title = re.search(r'"videoId":".*?", "title":"(.*?)"', html).groups()[0]
        self.caption_details = self.get_caption_details(html)
        if language is not None:
            try:
                captions = self.fetch_captions(self.caption_details[language])
                self.convert_to_srt(caption_file=captions, path=os.getcwd(), file_name=title)
            except Exception:
                raise Exception(f'No captions were found for {language}. Available Captions : {self.caption_details.keys()}')

    def get_caption_details(self, html=None):
        urls_regex = re.search(r'(\{"captionTracks":\[.*?\])', html)
        caption_details = dict()
        if urls_regex.groups()[0] is not None:
            urls_regex = urls_regex.groups()[0]+'}'
            for i in json.loads(urls_regex)['captionTracks']:
                caption_details[i['languageCode']] = i['baseUrl']
            return caption_details
        else:
            raise Exception('Captions not available for this Video')

    def fetch_captions(self, url):
        caption_file = requests.get(url).text.replace('\n', '')
        return caption_file

    def convert_to_srt(self, caption_file=None, path=None, file_name=None):
        if caption_file is not None:
            srt_text = ''
            lines = 1
            for i in re.findall(r'<text start="(.*?)" dur="(.*?)">(.*?)</text>', caption_file):
                start = float(i[0])
                dur = float(i[1])
                end = start+dur
                text = i[2]
                start_time = time.strftime("%H:%M:%S"+", 000",  time.gmtime(start))
                end_time = time.strftime("%H:%M:%S"+", 000",  time.gmtime(end))
                text_line = f'{lines}\n{start_time} --> {end_time}\n{text}\n'
                srt_text += text_line
                lines += 1
            if file_name is not None:
                file_name = file_name.split('.srt')[0]
                open(f'{path}' + os.path.sep + f'{file_name}.srt', 'wb').write(srt_text.encode('utf-8'))
            else:
                raise Exception('Please provide file name and path to covert_to_srt function')
