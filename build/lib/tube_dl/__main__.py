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
        extra_details = ''
        while True:
            self.html = unquote(requests.get(f'https://www.youtube.com/get_video_info?html5=1&video_id={vid}&el=detailpage',headers = headers).text)
            for j in re.findall(r'=(\{.*?)&',self.html):
                j = j.replace('+',' ')
                if 'streamingData' in j:
                    json_data = json.loads(j)
                else:
                    extra_details = json.loads(j)
            if extra_details != '':
                break
        primary_details = json_data['videoDetails']
        details = extra_details['contents']['twoColumnWatchNextResults']['results']['results']['contents']
        other_details = details[1]["videoSecondaryInfoRenderer"]
        vid_details = details[0]["videoPrimaryInfoRenderer"]
        self.description = ' '.join([i['text'] for i in other_details['description']['runs']])
        self.category = json_data["microformat"]["playerMicroformatRenderer"]["category"]
        self.is_live = primary_details["isLiveContent"]
        self.keywords = primary_details['keywords']
        self.channel_id = primary_details['channelId']
        self.title = primary_details['title']
        self.length = primary_details['lengthSeconds']
        self.upload_date = vid_details["dateText"]["simpleText"].replace(' ','-')
        self.rating = primary_details['averageRating']
        self.is_live = primary_details["isLiveContent"]
        self.channel_name = primary_details["author"]
        if 'captions' in json_data.keys():
            self.caption_data = json_data['captions']["playerCaptionsTracklistRenderer"]["captionTracks"]
        else:
            self.caption_data = None
        self.views = vid_details["viewCount"]["videoViewCountRenderer"]["viewCount"]["simpleText"]
        self.likes,self.dislikes = map(int,vid_details["sentimentBar"]["sentimentBarRenderer"]["tooltip"].replace(',','').split('/'))
        self.streamingData = list()
        for k in json_data['streamingData'].keys():
            if type(json_data['streamingData'][k]) == list:
                for stream in json_data['streamingData'][k]:
                    self.streamingData.append(stream)
        self.thumbnail_url = f'https://i.ytimg.com/vi/{vid}/maxresdefault.jpg'
        try:
            self.metadata = other_details["metadataRowContainer"]["metadataRowContainerRenderer"]['rows']
            meta = dict({'uploaded':self.upload_date})
            for i in self.metadata:
                if 'metadataRowRenderer' in i.keys():
                    m = i['metadataRowRenderer']
                    meta[m['title']['simpleText']] = ','.join([h['simpleText'] for h in m['contents']])
        except:
            self.meta = None
        self.algo_js = None
        self.formats = list_streams(self.Formats())
    def get_js(self,error=False):
        file_name = __file__.rsplit('\\',1)[0]+'\\yt.js'
        try:
            js_data = open(file_name,'rb').read().decode('utf-8')
        except:
            js_data = open(file_name,'w').write('')
            js_data = open(file_name,'rb').read().decode('utf-8')
        if js_data == '' or float(js_data.split('||')[0]) > time.time()-3600000 or error == True:
            html = unquote(requests.get(self.url).text)
            js_file = requests.get('https://youtube.com'+re.search(r'"jsUrl":"(.*?)"',html).groups()[0]).text
            data = Decipher(js_file,process=True).get_full_function()
            open(file_name,'wb').write(f'{time.time()}||{data}'.encode('utf-8'))
        else:
            data =  js_data.split('||')[-1]
        return data
    
    def Formats(self,stream_data:list() = None):
        '''
        Returns:
            Returns List of all stream formats available for the video. 

        Return Type : 
            List(streams_objects)
        '''
        formats = list()
        if stream_data == None:
            stream_data = self.streamingData
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
                if self.algo_js is None:
                    self.algo_js = self.get_js()   
                signature,url = stream['signatureCipher'].split('&sp=sig&')
                deciphered_signature = Decipher().deciphered_signature(signature = signature.split('s=')[-1].replace('%253D','=').replace('%3D','='),algo_js=self.algo_js)
                url = unquote(url).split('=',1)[1]+'&sig='+deciphered_signature
            else:
                url = stream['url'].replace('\\u0026','&')
            url = url+'&rbuf=0'
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
            if self.meta is not None:
                description = self.meta
            else:
                description = self.description
            formats.append(Format(self.category,description,self.title,{'itag':itag,'mimeType':Mime,'vcodec':vcodec,'acodec':acodec,'fps':fps,'abr':abr,'quality':quality,'url':url,'size':size,'adaptive':adaptive,'progressive':progressive}))
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
