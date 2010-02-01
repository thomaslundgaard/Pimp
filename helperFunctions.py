# -*- coding: utf-8 -*-
def parseTrackInfo( description):
    try: title=description['title']
    except KeyError: title = ''
    try: artist=description['artist']
    except KeyError: artist = ''
    try: filename=description['file']
    except KeyError: filename = ''
    try: album = description['album']
    except KeyError: album = ''
    try: genre = description['genre']
    except KeyError: genre = ''
    try: time =int( description['time'])
    except KeyError: time = None
    try: pos = int( description['pos'])
    except KeyError: pos = None
    if not (curSong.title or curSong.artist):
        title = curSong.filename.split('/').pop().split('-').pop().split('.')[0:-1]
        title = "".join(title).strip()
        artist = curSong.filename.split('/').pop().split('-').pop(0).split('.')[0:-1]
        artist = "".join(artist).strip()
    return {'title':    title,\
            'artist':   artist,\
            'file':     file,\
            'album':    album,\
            'genre':    genre,\
            'time':     time,\
            'pos':      pos,\
           }

