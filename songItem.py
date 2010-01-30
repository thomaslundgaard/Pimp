# -*- coding: utf-8 -*-
class SongItem:
    def __init__(self,description):
        try: self.title=description['title']
        except KeyError: self.title = None
        try: self.artist=description['artist']
        except KeyError: self.artist = None
        try: self.filename=description['file']
        except KeyError: self.filename = None
        try: self.album = description['album']
        except KeyError: self.album = None
        try: self.time =int( description['time'])
        except KeyError: self.time = None
        try: self.pos = int( description['pos'])
        except KeyError: self.pos = None

        # Generate text entry
        self.textEntry = ""
        if self.artist or self.title:
            if self.artist:
                self.textEntry = self.textEntry + self.artist + " - "
            else:
                self.textEntry = self.textEntry + "Unknown Artist - "
            if self.title:
                self.textEntry = self.textEntry + self.title
            else:
                self.textEntry += "Unknown Title"
        else:
            self.textEntry += self.filename
        self.textEntry += ' (%i:%02i)' % (self.time/60, self.time%60)
