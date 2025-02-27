from pytube import YouTube
url=input('Enter youtube video link: ')
yt=YouTube(url,use_oauth=True,allow_oauth_cache=True)
video=yt.streams.filter(only_audio=True).first()
video.download()