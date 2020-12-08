import string
import os
import requests
from tube_dl.extras import Convert
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36','referer':'https://youtube.com'}
class Format:
    def __init__(self,meta,title,thumbnail,stream_data:dict):
        self.meta = meta
        self.data = stream_data
        self.thumbnail = thumbnail
        self.title = title
        self.itag = self.data['itag']
        self.mime = self.data['mimeType']
        self.acodec =self.data['acodec']
        self.vcodec = self.data['vcodec']
        self.size = self.data['size']
        self.fps = self.data['fps']
        self.quality = self.data['quality']
        self.abr = self.data['abr']
        self.url = self.data['url']
        self.adaptive = self.data['adaptive']
        self.progressive = self.data['progressive']
    def safe_filename(self,name:str,):
        valid_chars = "-_() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(char for char in name if char in valid_chars)
        return filename
    def download(self, onprogress = None, convert:str = None, path = None, file_name = None, ):
        '''
        This Function downloads the format selected by user. 

        Params :
            onprogress: Function - If defined, following data will be returned to the specified function 
                1. Chunk - The file Chunk
                2. bytes_done - Total count of bytes done downloading
                3. total_size - Total size of the file. Extracted from header
            merge [Coming Soon] : Bool - If True, will download the best quality audio and merge it with the video stream. For this, the download function should have Video File as input
            convert : Bool - If defined, convert the file to the desired extension without losing important metadata.
            path : Str - Defines the path where to keep the file
            file_name : Str - Defines the file name to be used in the file. To avoid any saving error, function safe_filename will be used to extract the filename without unsafe characters.
        
        '''
        url = self.url
        if type(url) != str:
            raise Exception('Download should be a single Format. Not List(Format)')
        if file_name == None:
            file_name = self.title
        file_name = self.safe_filename(file_name)
        Type,extension = self.mime.split('/')
        if path is None:
            path = os.getcwd()
        final_path = f'{path}\\{file_name}.{extension}'
        response = requests.get(url, stream = True,headers = headers)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        block_size = total_size_in_bytes//200
        bytes_done = 0
        with open(final_path, 'wb') as f:
            for data in response.iter_content(block_size):
                f.write(data)
                bytes_done += block_size
                if onprogress != None:
                    onprogress(chunk = data, bytes_done = bytes_done, total_bytes = total_size_in_bytes)
        f.close()
        if convert is not None:
            Convert(self.meta,final_path,self.thumbnail,convert.split('.')[0],Type)
    def __repr__(self):
        return f'<Format : itag={self.itag}, mimeType={self.mime}, size={self.size}, acodec={self.acodec}, vcodec={self.vcodec}, fps={self.fps}, quality={self.quality}, abr={self.abr}, progressive={self.progressive}, adaptive={self.adaptive} >'
class list_streams:
    def __init__(self,data):
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
        only_audio = False,
        adaptive=False,
        itag = None,
        fps = None,
        quality = None,
        no_audio = None
        ):
        content = self.data
        content_list = list()
        for i in content:
            if no_audio == True:
                if i.acodec == None:
                    content_list.append(i)
            if only_audio == True:
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
            if adaptive == True:
                if i.adaptive == True:
                    content_list.append(i)
            if progressive == True:
                if i.progressive == True:
                    content_list.append(i)
        self.data = content_list 
        return content_list
        