from tube_dl import Youtube
yt = Youtube('https://www.youtube.com/watch?v=jZGWknhg8kA')
def progress(chunk=None, bytes_done = None, total_bytes = None):
    print(round((bytes_done/total_bytes)*100,2),end='\r')
yt.Formats()[0].download(onprogress=progress,convert='mp3')