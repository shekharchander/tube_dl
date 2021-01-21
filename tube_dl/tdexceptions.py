class VideoError(Exception):
    def __init__(self, vid):
        self.message = f'Invalid video ID. Are you sure "{vid}" is a valid URL?'
        super().__init__(self.message)


class PlaylistError(Exception):
    def __init__(self, pid):
        self.message = f'Invalid Playlist ID. Are you sure "{pid}" is a valid URL and available?'
        super().__init__(self.message)
