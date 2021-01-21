import string
import os
import requests
from tube_dl.extras import Output
headers = {'user-agent':  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,  like Gecko) Chrome/86.0.4240.198 Safari/537.36', 'referer': 'https: //youtube.com'}


class Format:
    def __init__(self,  category,  description, title, stream_data: dict):
        self.data = stream_data
        self.category = category
        self.description = description
        self.title = title
        self.itag = self.data['itag']
        self.mime = self.data['mimeType']
        self.acodec = self.data['acodec']
        self.vcodec = self.data['vcodec']
        self.size = self.data['size']
        self.fps = self.data['fps']
        self.quality = self.data['quality']
        self.abr = self.data['abr']
        self.url = self.data['url']
        self.adaptive = self.data['adaptive']
        self.progressive = self.data['progressive']

    def safe_filename(self, name: str, ):
        valid_chars = "-_() %s%s" % (string.ascii_letters,  string.digits)
        filename = ''.join(char for char in name if char in valid_chars)
        return filename

    def download(self,  force_filename=False, onprogress=None,  path=None,  file_name=None, skip_existing=False):
        '''
        This Function downloads the format selected by user.

        Params :
            onprogress:  Function - If defined,  following data will be returned to the specified function
                1. Chunk - The file Chunk
                2. bytes_done - Total count of bytes done downloading
                3. total_size - Total size of the file. Extracted from header
            path :  Str - Defines the path where to keep the file
            file_name :  Str - Defines the file name to be used in the file. To avoid any saving error,  function safe_filename will be used to extract the filename without unsafe characters.

        '''
        url = self.url
        if type(url) != str:
            raise Exception('Download should be a single Format. Not List(Format)')
        if file_name is None:
            file_name = self.title
        if force_filename is False:
            file_name = self.safe_filename(file_name)
        else:
            file_name = file_name
        _, extension = self.mime.split('/')
        if path is None:
            path = os.getcwd()
        final_path = f'{path}{os.path.sep}{file_name}.{extension}'

        def start():
            response = requests.get(url,  stream=True, headers=headers)
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024
            bytes_done = 0
            f = open(final_path,  'wb')
            try:
                for data in response.iter_content(block_size):
                    f.write(data)
                    bytes_done += block_size
                    if onprogress is not None:
                        onprogress(bytes_done=bytes_done, total_bytes=total_size_in_bytes)
                f.close()
            except Exception:
                start()
        if skip_existing is False:
            start()
        else:
            if os.path.exists(final_path) is False:
                start()
            else:
                print('Skipping Files :  Existing check is True')
        return Output(self.description, final_path)

    def __repr__(self):
        return f'<Format :  itag={self.itag},  mimeType={self.mime},  size={self.size},  acodec={self.acodec},  vcodec={self.vcodec},  fps={self.fps},  quality={self.quality},  abr={self.abr},  progressive={self.progressive},  adaptive={self.adaptive} >'


class list_streams:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f'{self.data}'

    def first(self):
        return self.data[0]

    def last(self):
        return self.data[-1]

    def filter_by(
        self,
        progressive=False,
        only_audio=False,
        adaptive=False,
        itag=None,
        fps=None,
        quality=None,
        no_audio=None
            ):
        content = self.data
        content_list = list()
        for i in content:
            if no_audio is True:
                if i.acodec is None:
                    content_list.append(i)
            if only_audio is True:
                if i.mime.split('/')[0].lower() == 'audio':
                    content_list.append(i)
            if quality is not None:
                if i.quality.lower() == quality.lower():
                    content_list.append(i)
            if fps is not None:
                if i.fps == fps:
                    content_list.append(i)
            if itag is not None:
                if i.itag == itag:
                    content_list.append(i)
            if adaptive is True:
                if i.adaptive is True:
                    content_list.append(i)
            if progressive is True:
                if i.progressive is True:
                    content_list.append(i)
        self.data = content_list
        return content_list
