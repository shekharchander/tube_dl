from re import findall
from requests import get
from tube_dl.decipher import Decipher
from tube_dl.formats import Format, list_streams
from urllib.parse import unquote
from json import load, dumps
from os import path
cwd = path.dirname(path.abspath(__file__))
headers = {
    'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'),
    'referer': 'https://youtube.com'}


class Youtube:
    def __init__(self, vid):
        '''
        This class takes the Youtube URL as an argument,
        then perform regex to get the important data from the HTML file

        Params:
            url:str Takes Youtube URL

        Usage:
            yt = Youtube('https://youtube.com/watch?v=xhaI-lLiUFA')

        '''
        try:
            vid = "".join([i for i in findall(r"v=(.*?)&|youtu.be\/(.*?)&", vid + "&")[0]])
        except IndexError:
            vid = vid
        try:
            self.json_file = load(open(cwd+"/tube_dl_config.json", "rb"))
        except FileNotFoundError:
            self.get_js()
            self.json_file = load(open(cwd+"/tube_dl_config.json", "rb"))
        if self.json_file['js'] == '':
            self.get_js()
        headers["x-youtube-client-version"] = self.json_file['cver']
        headers["x-youtube-client-name"] = self.json_file['cname']
        try:
            y_data = get(f"https://youtube.com/watch?v={vid}&pbj=1", headers=headers).json()
        except Exception:
            from tube_dl.tdexceptions import VideoError
            raise VideoError(vid)
        yt_data = [i for i in y_data if "playerResponse" in i.keys()][0]["playerResponse"]
        if yt_data["playabilityStatus"]["status"] == "ERROR":
            from tube_dl.tdexceptions import VideoError
            raise VideoError(vid)
        self.streamingData = list()
        s_data = yt_data["streamingData"]
        videoDetails = yt_data["videoDetails"]
        self.title = videoDetails['title']
        self.keywords = videoDetails["keywords"]
        self.length = videoDetails["lengthSeconds"]
        self.channelName = videoDetails["author"]
        self.channeId = videoDetails["channelId"]
        self.isLive = videoDetails["isLiveContent"]
        self.views = videoDetails["viewCount"]
        self.videoId = videoDetails["videoId"]
        self.thumbnail = videoDetails["thumbnail"]["thumbnails"][-1]["url"]
        extraDetails = yt_data['microformat']['playerMicroformatRenderer']
        self.availableCountries = extraDetails['availableCountries']
        self.category = extraDetails['category']
        extraDetails = [i for i in y_data if "response" in i.keys()][0]["response"]["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"]
        try:
            self.subscribers = extraDetails[1]['videoSecondaryInfoRenderer']["owner"]["videoOwnerRenderer"]["subscriberCountText"]["runs"][0]
        except:
            self.subscribers = extraDetails[1]['videoSecondaryInfoRenderer']["owner"]["videoOwnerRenderer"]["subscriberCountText"]["simpleText"].replace(",","")
        self.description = ''.join([i["text"] for i in extraDetails[1]['videoSecondaryInfoRenderer']['description']["runs"]])
        extraDetails = extraDetails[0]["videoPrimaryInfoRenderer"]
        try:
            self.likes, self.dislikes = [i.strip() for i in extraDetails["sentimentBar"]["sentimentBarRenderer"]["tooltip"].split('/')]
        except:
            self.likes,self.dislikes = [0,0]
        self.uploadDate = extraDetails["dateText"]["simpleText"].split(' ')[-1]
        try:
            self.hashTags = [i["text"] for i in extraDetails['superTitleLink']["runs"] if i["text"] != ' ']
        except Exception:
            self.hashTags = None
        try:
            mD = [i for i in y_data if "response" in i.keys()][0]["response"]["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][0]["videoSecondaryInfoRenderer"]["metadataRowContainer"]["metadataRowContainerRenderer"]["rows"]
            for i in mD:
                if "metadataRowRenderer" in i.keys():
                    self.meta[i["metadataRowRenderer"]["title"]["simpleText"]] = i["metadataRowRenderer"]["contents"][0]["simpleText"]
        except Exception:
            self.meta = dict()
        if self.isLive == 'true':
            try:
                self.hlsUrl = s_data["hlsManifestUrl"]
            except Exception:
                self.hlsUrl = None
            try:
                self.dashUrl = s_data["dashManifestUrl"]
            except Exception:
                self.dashUrl = None
            self.streamingData = []
        else:
            for i in s_data.keys():
                if i != 'expiresInSeconds':
                    for k in s_data[i]:
                        self.streamingData.append(k)
        self.formats = list_streams(self.Formats())

    def get_js(self):
        base_data = get('https://youtube.com/watch?v=1').text
        js_url = 'https://youtube.com/'+findall(r'"jsUrl":"(.*?)"', base_data)[0]
        js_file = get(js_url).text
        data = Decipher(js_file, process=True).get_full_function()
        self.json_file['js'] = data
        open(cwd+'/tube_dl_config.json', 'w').write(dumps(self.json_file))
        return data

    def Formats(self):
        '''
        Returns:
            Returns List of all stream formats available for the video.

        Return Type :
            List(streams_objects)
        '''
        fmt = list()
        js_passed = False
        for stream in self.streamingData:
            itag = stream["itag"]
            Mime, Codecs = stream["mimeType"].replace("'", '').split(';')
            Codecs = Codecs.split('=')[-1].replace(' ', '').split(',')
            Type = Mime.split('/')[0]
            adaptive = False
            progressive = False
            if Type.lower() == 'video':
                if len(Codecs) > 1:
                    vcodec, acodec = Codecs
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
            except Exception:
                abr = stream["bitrate"]
            if 'signatureCipher' in stream.keys():
                signature, url = stream["signatureCipher"].split('&sp=sig&url=')
                signature = signature.replace("s=",'',1).replace('%253D', '%3D').replace('%3D', '=')
                deciphered_signature = Decipher().deciphered_signature(
                    signature, algo_js=self.json_file['js']
                    )
                url = unquote(url)+'&sig='+deciphered_signature
                if js_passed is False:
                    try:
                        if get(url, timeout=4, stream=True).status_code != 200:
                            self.get_js()
                            deciphered_signature = Decipher().deciphered_signature(signature, algo_js=self.json_file['js'])
                            url = unquote(url)+'&sig=' + deciphered_signature
                    except Exception:
                        self.get_js()
                        deciphered_signature = Decipher().deciphered_signature(signature, algo_js=self.json_file['js'])
                        url = unquote(url)+'&sig=' + deciphered_signature
                    js_passed = True
            else:
                url = stream["url"].replace('\\u0026', '&')
            try:
                fps = stream["fps"]
                quality = stream["qualityLabel"]
            except Exception:
                fps = None
                quality = stream["quality"]
            try:
                size = stream["contentLength"]
            except Exception:
                size = 0
            if self.meta is not None:
                description = self.meta
            else:
                description = self.description
            fmt.append(Format(self.category, description, self.title, {'itag': itag, 'mimeType': Mime, 'vcodec': vcodec, 'acodec': acodec, 'fps': fps, 'abr': abr, 'quality': quality, 'url': url, 'size': size, 'adaptive': adaptive, 'progressive': progressive}))
        return fmt


class Playlist:
    def __init__(self, url: str, start: int = None, end: int = None):
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
        url = 'https://youtube.com/playlist?'+findall(r'(list=.*?)&', url+'&')[0]
        html = unquote(get(url.replace('music.', ''), headers=headers).text)
        regex = r'playlistVideoRenderer":\{"videoId":"(.*?)"'
        self.IDs = findall(regex, html)
        if len(self.IDs) == 0:
            from tube_dl.tdexceptions import PlaylistError
            raise PlaylistError(url)
        try:
            total_count = int(findall(r'"text":"([0-9]*)"', html)[0])
        except Exception:
            total_count = int(findall(r'"stats":\[\{"runs":\[\{"text":"(.*?)"\}', html)[0].replace(',', ''))
        self.Api_key = findall(r'"innertubeApiKey":"(.*?)"', html)[0]
        self.version = findall(r'"INNERTUBE_CONTEXT_CLIENT_VERSION":"(.*?)"', html)[0]
        if total_count > 100:
            for _ in range(0, total_count//100):
                self.fetch_continuation(html)
        if start is None:
            start = 0
        if end is None:
            end = len(self.IDs)
        self.videos = self.return_URLs(start, end)

    def return_URLs(self, start, end):
        '''
            Returns the Video URLs
        '''
        return self.IDs[start:end]

    def fetch_continuation(self, html):
        '''
        If there are more than 100 videos in a playlist, Youtube shows them in sets of 100 each.
        This set of code uses the continuation URL and appends it regex match to the IDs variable.
        '''
        from requests import post
        Token = findall(r'"continuationCommand":{"token":"(.*?)"', html)[0]
        url, payload = self.get_continuation_data(Token)
        data = post(url, json=payload, headers=headers).text.replace(' ', '').replace('\n', '')
        for i in findall(r'"videoId":"(.*?)"', data):
            if i not in self.IDs:
                self.IDs.append(i)

    def get_continuation_data(self, Token):
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
                    {"clientName": "WEB", "clientVersion": self.version}},
            "continuation": Token}
        final_url = f'https://www.youtube.com/youtubei/v1/browse?key={self.Api_key}'
        return (final_url, payload)
