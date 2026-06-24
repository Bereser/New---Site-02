import yt_dlp

url = 'https://www.youtube.com/watch?v=nnio_Z2IIJQ'
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'format': 'best'
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    print('requested_subtitles=', info.get('requested_subtitles'))
    print('subtitles=', info.get('subtitles'))
    print('automatic_captions=', info.get('automatic_captions'))
    print('captions=', info.get('captions'))
    print('webpage_url=', info.get('webpage_url'))
    print('subtitles_keys=', list(info.get('subtitles', {}).keys()))
    print('automatic_captions_keys=', list(info.get('automatic_captions', {}).keys()))
    print('formats count=', len(info.get('formats', [])))
