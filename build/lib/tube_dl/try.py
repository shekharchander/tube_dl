from moviepy.editor import *
a =VideoFileClip('c://users//shekhar chander//music//satisfy.mp4')
b = AudioFileClip('c://users//shekhar chander//music//7 rings.mp3')
c = a.set_audio(b)
c.write_videofile("a.mp4")
