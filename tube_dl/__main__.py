import requests
import re
from tube_dl.decipher import Decipher
from tube_dl.formats import Format,list_streams
from urllib.parse import unquote
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36','referer':'https://youtube.com'}
class Youtube:
    def __init__(self,id):
        '''
        This class takes the Youtube URL as an argument and then perform regex to get the important data from the HTML file.
    
        Params:
            url:str Takes Youtube URL

        Usage:
            yt = Youtube('https://youtube.com/watch?v=xhaI-lLiUFA')

        '''
        vid_regex=re.search(r'v=(.*?)&|youtu.be\/(.*?)&',id+'&')
        if vid_regex is None:
            vid_id=id
        else:
            for i in vid_regex.groups():
                if i != None:
                    vid_id=i
        base_data=requests.get('https://youtube.com/watch?v=1').text
        self.js_url='https://youtube.com/'+re.findall(r'"jsUrl":"(.*?)"',base_data)[0]
        headers['x-youtube-client-version']=re.findall(r'"INNERTUBE_CLIENT_VERSION":"(.*?)"',base_data)[0]
        headers['x-youtube-client-name']='1'
        try:
            yt_data=requests.get(f'https://youtube.com/watch?v={vid_id}&pbj=1',headers=headers).json()
        except:
            raise Exception('----------| Not a valid youtube ID |----------')
        for i in yt_data:
            d=i.keys()
            if 'playerResponse' in d:
                if 'streamingData' not in i['playerResponse']:
                    return
                streamingData=i["playerResponse"]["streamingData"]
                videoDetails = i["playerResponse"]["videoDetails"]
                D = i["playerResponse"]["microformat"]["playerMicroformatRenderer"]
                self.thumbnail=D["thumbnail"]["thumbnails"][0]["url"]
                self.channelUrl = D["ownerProfileUrl"]
                self.category = D["category"]
            if 'response' in d:
                video_info=[i for i in i["response"]["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"]]
        self.formats_data=list()
        for i in streamingData.keys():
            if i.startswith('expires') is False and i.startswith('dash') is False and i.startswith('hls') is False:
                for j in streamingData[i]:
                    self.formats_data.append(j)
            if "dashManifestUrl" in i:
                self.dashUrl = streamingData["dashManifestUrl"]
            else:
                self.dashUrl = None
            if "hlsManifestUrl" in i:
                self.hlsUrl = streamingData["hlsManifestUrl"]
            else:
                self.hlsUrl = None
        self.title=videoDetails["title"]
        if 'keywords' in videoDetails.keys():
            self.keywords=videoDetails["keywords"]
        else:
            self.keywords = ''
        self.length=videoDetails["lengthSeconds"]
        self.uploadDate = D["uploadDate"]
        for i in video_info:
            if "videoPrimaryInfoRenderer" in i.keys():
                i=i["videoPrimaryInfoRenderer"]
                self.views = i["viewCount"]["videoViewCountRenderer"]["viewCount"]
                if "simpleText" in self.views.keys():
                    self.views=self.views["simpleText"].replace(',','')
                    self.is_live = False
                else:
                    self.views = self.views["runs"][0]["text"].replace(',','').split(" ")[0]
                    self.is_live = True
                self.likes=re.findall(r"'label': '(.*?) likes'",str(i))[0].replace(',','')
                check = re.findall(r"\{'label': '([0-9\,]*) dislikes'\}",str(i))
                self.dislikes= 0
                if len(check):
                    self.dislikes = check[0].replace(',','')
                #print(f'self.dislikes = {self.dislikes}\tcheck len = {len(check)}')
                
            if "videoSecondaryInfoRenderer" in i.keys():
                i=i["videoSecondaryInfoRenderer"]
                self.channelThumb=i["owner"]["videoOwnerRenderer"]["thumbnail"]["thumbnails"]
                self.channelName=i["owner"]["videoOwnerRenderer"]["title"]["runs"][0]["text"]
                #print(i["owner"]["videoOwnerRenderer"]["subscriberCountText"]["runs"])
                self.subscribers= 0
                check = i["owner"]["videoOwnerRenderer"]
                if 'subscriberCountText' in check.keys():
                    self.subscribers = check["subscriberCountText"]["runs"][0]["text"].split(' ')[0]
                self.description="".join([j["text"] for j in i["description"]["runs"]])
                self.meta = dict()
                if "rows" in i["metadataRowContainer"]["metadataRowContainerRenderer"]:
                    mD = i["metadataRowContainer"]["metadataRowContainerRenderer"]["rows"]
                    for i in mD:
                        if "metadataRowRenderer" in i.keys():
                            contents = i["metadataRowRenderer"]["contents"]
                            #print(contents)
                            if 'simpleText' in contents[0]:
                                self.meta[i["metadataRowRenderer"]["title"]["simpleText"]] = i["metadataRowRenderer"]["contents"][0]["simpleText"]
                            else:
                                self.meta[i["metadataRowRenderer"]["title"]["simpleText"]] = ''


        self.algo_js = None
        self.formats = list_streams(self.Formats())
    def get_js(self):
        js_file = requests.get(self.js_url).text
        data = Decipher(js_file,process=True).get_full_function()
        return data
    
    def Formats(self):
        '''
        Returns:
            Returns List of all stream formats available for the video. 

        Return Type : 
            List(streams_objects)
        '''
        fmt = list()
        for stream in self.formats_data:
            itag = stream["itag"]
            Mime,Codecs = stream["mimeType"].replace("'",'').split(';')
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
                abr = stream["averageBitrate"]
            except:
                abr = stream["bitrate"]
            if 'signatureCipher' in stream.keys():
                if self.algo_js is None:
                    self.algo_js = self.get_js()   
                signature,url = stream["signatureCipher"].split('&sp=sig&')
                deciphered_signature = Decipher().deciphered_signature(signature = signature.split('s=')[-1].replace('%253D','=').replace('%3D','='),algo_js=self.algo_js)
                url = unquote(url).split('=',1)[1]+'&sig='+deciphered_signature
            else:
                url = stream["url"].replace('\\u0026','&')
            try:
                fps = stream["fps"]
                quality = stream["qualityLabel"]
            except:
                fps = None
                quality = stream["quality"]
            try:
                size = stream["contentLength"]
            except:
                size = 0
            if self.meta is not None:
                description = self.meta
            else:
                description = self.description
            fmt.append(Format(self.category,description,self.title,{'itag':itag,'mimeType':Mime,'vcodec':vcodec,'acodec':acodec,'fps':fps,'abr':abr,'quality':quality,'url':url,'size':size,'adaptive':adaptive,'progressive':progressive}))
        return fmt
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
