'''
This is the main file of YTDL. 
This file is responsible for parsing Youtube's html file and then processing the same.

Options Coming SOON : 

1. Captions
2. Merging Audio and Video
3. Youtube Search

'''


import requests
import json
import re
from tube_dl.decipher import Decipher
from tube_dl.formats import Format,list_streams
from tube_dl.captions import Caption
import time 
import os
from urllib.parse import unquote
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36','referer':'https://youtube.com'}
class Youtube:
    def __init__(self,url):
        '''
        This class takes the Youtube URL as an argument and then perform regex to get the important data from the HTML file.
    
        Params:
            url:str Takes Youtube URL

        Usage:
            yt = Youtube('https://youtube.com/watch?v=xhaI-lLiUFA')

        '''
        for i in re.search(r'watch\?v=(.*?)&|youtu.be/(.*?)&',url+'&').groups():
            if i is not None:
                vid = i
                break
        self.url = 'https://youtube.com/watch?v='+vid
        html = unquote(requests.get(self.url,headers = headers).text)
        self.algo_js = self.get_js(html)

        raw_itags = ''
        self.html = re.search(r'<script.*?>.*?responseContext.*?</script>',html).group()
        for i in re.findall(r'\[(\{.itag.*?\})\]',self.html):
            raw_itags += i+','
        if raw_itags == '':
            try:
                self.html = self.html.replace('\\"','"')
                for i in re.findall(r'\[(\{.itag.*?\})\]',self.html):
                    raw_itags += i+','
            except:
                raise Exception("Not a Valid Youtube ID.")
        raw_itags = '['+raw_itags.replace('\\\\"',"'").rsplit(',',1)[0]+']'
        self.stream_data = json.loads(raw_itags)
        self.video_details()
        self.formats = list_streams(self.Formats())
    def get_js(self,html):
        js_file = requests.get('https://youtube.com'+re.search(r'"jsUrl":"(.*?)"',html).groups()[0]).text
        return Decipher(js_file,process=True).get_full_function()
    def video_details(self,html:str = None):
        '''
        Contains:
            All the MetaData about the video
        
        Params:
            html:str - Takes the html file that contains the metadata
        
        '''
        self.channel_name = re.search(r'"ownerChannelName":"(.*?)"',self.html).groups()[0]
        self.channel_url = re.search(r'"ownerProfileUrl":"(.*?)"',self.html).groups()[0]
        regex_group = re.findall(r'"videoDetails":.*?\}',html)[0]
        self.title = re.search(r'"videoId":".*?","title":"(.*?)"',regex_group).groups()[0]
        self.length = re.search(r'"lengthSeconds":"(.*?)"',regex_group).groups()[0]
        self.views = re.search(r'"viewCount":"(.*?)"',self.html).groups()[0]
        self.upload_date = re.search(r'"uploadDate":"(.*?)"',self.html).groups()[0]
        try:
            self.description = re.search(r'"description":\{"simpleText":"(.*?)"',self.html).groups()[0]
        except:
            self.description = re.search(r'"shortDescription":"(.*?)"',self.html).groups()[0]
    def Formats(self,stream_data:list() = None):
        '''
        Returns:
            Returns List of all stream formats available for the video. 

        Return Type : 
            List(streams_objects)
        '''
        formats = list()
        if stream_data == None:
            stream_data = self.stream_data
        for stream in stream_data:
            itag = stream['itag']
            Mime,Codecs = stream['mimeType'].replace("'",'').split(';')
            Codecs = Codecs.split('=')[-1].replace(' ','').split(',')
            Type = Mime.split('/')[0]
            adaptive = False
            progressive = False
            if Type.lower() == 'video':
                if len(Codecs) > 1:
                    vcodec,acodec = Codecs
                    progressive = True
                else:
                    vcodec = Codecs[0]
                    acodec = None
                    adaptive = True
            else:
                acodec = Codecs[0]
                vcodec = None
                adaptive = True
            try:
                abr = stream['averageBitrate']
            except:
                abr = stream['bitrate']
            if 'signatureCipher' in str(stream):
                try:
                    signature,url = unquote(stream['signatureCipher']).split('&sp=sig&')
                except:
                    signature,url = stream['signatureCipher'].split('\\u0026sp=sig\\u0026')

                deciphered_signature = Decipher().deciphered_signature(signature = signature.split('s=')[-1],algo_js=self.algo_js)
                url = unquote(url).split('=',1)[1]+'&sig='+deciphered_signature
            else:
                url = stream['url'].replace('\\u0026','&')
            try:
                fps = stream['fps']
                quality = stream['qualityLabel']
            except:
                fps = None
                quality = stream['quality']
            try:
                size = stream['contentLength']
            except:
                size = 0
            if round(stream['approxDurationMs']/1000) == self.length:
                formats.append(Format(self.title,{'itag':itag,'mimeType':Mime,'vcodec':vcodec,'acodec':acodec,'fps':fps,'abr':abr,'quality':quality,'url':url,'size':size,'adaptive':adaptive,'progressive':progressive}))
        return formats
        
class Playlist:
    
    def __init__(self,url:str,start:int = None,end:int = None):
        '''
        This Class is responsible for:
            1. Get list of all the Videos
            2. Create Continuation URL if len(videos)>100
            3. Get Continuation data and append all the video IDs to IDS variable
        
        Parameters : 
            url: str - URL of the PlayList
            start,end - Defines the range of Videos you want.
        
        Returns :
            Tuple : All the Video IDs within the Range variable( if Defined)
        '''
        headers['referer'] = url
        url = 'https://youtube.com/playlist?'+re.search(r'(list=.*?)&',url+'&').groups()[0]
        html = unquote(requests.get(url.replace('music.',''),headers = headers).text)
        regex = r'playlistVideoRenderer":\{"videoId":"(.*?)"'
        self.IDs = re.findall(regex,html)
        if len(self.IDs) == 0:
            raise  Exception('Not a Youtube Playlist.')
        print('Gathering Video IDs')
        try:
            total_count = int(re.search(r'"text":"([0-9]*)"',html).groups()[0])
        except:
            total_count = int(re.search(r'"stats":\[\{"runs":\[\{"text":"(.*?)"\}',html).groups()[0].replace(',',''))
        self.Api_key = re.search(r'"innertubeApiKey":"(.*?)"',html).groups()[0]
        self.version = re.search(r'"INNERTUBE_CONTEXT_CLIENT_VERSION":"(.*?)"',html).groups()[0]
        if total_count > 100:
            for _ in range(0,total_count//100):
                self.fetch_continuation(html)
        if start == None:
            start = 0
        if end == None:
            end = len(self.IDs)
        self.videos = self.return_URLs(start,end)
    def return_URLs(self,start,end):
        '''
            Returns the Video URLs
        '''
        return self.IDs[start:end]
    def fetch_continuation(self,html):
        '''
        If there are more than 100 videos in a playlist, Youtube shows them in sets of 100 each.
        This set of code uses the continuation URL and appends it regex match to the IDs variable.
        '''
        regex = r'"continuationCommand":{"token":"(.*?)"'
        Token = re.search(regex,html).groups()[0]
        url, payload = self.get_continuation_data(Token)
        data = requests.post(url,json = payload,headers = headers).text.replace(' ','').replace('\n','')
        for i in re.findall(r'"videoId":"(.*?)"',data):
            if i not in self.IDs:
                self.IDs.append(i)
    def get_continuation_data(self,Token):
        '''
        To get next set of videos, Continuation Token is required to be passed to the Youtube API.
        This function fetches the Continuation token from the Requests Response text    
        
        Returns : Tuple containing Final_Url and JSON post data
            (
                final_url:str - Continuation URL,
                payload:str - JSON post data to fetch next set of videos
            )
       
        Parameters:    
            
            Token:str - Continuation Token to access next page

        '''        
        payload = {
            "context":
                {"client":
                    {"clientName": "WEB","clientVersion": self.version}},
            "continuation":Token}
        final_url = f'https://www.youtube.com/youtubei/v1/browse?key={self.Api_key}'
        return (final_url,payload)
