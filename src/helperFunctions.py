# -*- coding: utf-8 -*-
# PiMP - A mpd-frontend to be used as a jukebox at parties.
# Copyright (C) 2010 Peter Bjørn
# Copyright (C) 2010 Thomas Lundgaard
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unicodedata, sys
import re       # regex
import string

def parseTrackInfo(description):
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

    if isinstance(genre,list):
        genre = " ".join(genre)
    if isinstance(artist,list):
        artist = " & ".join(artist)

    if not title or not artist:
        try:
            regex = "[^a-zA-Z]*[^0-9a-zA-Z]?(.*)[^0-9a-zA-Z]*[\.\-]+\
[^0-9a-zA-Z]*(.*)\..*?$"
            m = re.search(regex, filename.split("/")[-1] )
            artist = m.group(1)
            title = m.group(2)
        except (IndexError, AttributeError):
            artist = "Unknown"
            try:
                m = re.search("(.*)\..*?$", filename.split("/")[-1] )
                title = m.group(1)
            except (IndexError, AttributeError):
                title = "Unknown"
    searchString = asciify(unicode(("%s %s %s %s %s" % \
            (artist, title, album, genre, filename)), 'utf-8').lower())

    return {'title':    unicode(title,'utf-8').strip().title(),\
            'artist':   unicode(artist,'utf-8').strip().title(),\
            'file':     unicode(filename,'utf-8'),\
            'time':     time,\
            'pos':      pos,\
            'tag':      searchString,\
           }
 
charmap={
    0xc6: u"a", # Æ LATIN CAPITAL LETTER AE
    0xd0: u"d",  # Ð LATIN CAPITAL LETTER ETH
    0xd8: u"o", # Ø LATIN CAPITAL LETTER O WITH STROKE
    0xde: u"t", # Þ LATIN CAPITAL LETTER THORN
    0xc4: u'a', # Ä LATIN CAPITAL LETTER A WITH DIAERESIS
    0xd6: u'o', # Ö LATIN CAPITAL LETTER O WITH DIAERESIS
    0xdc: u'u', # Ü LATIN CAPITAL LETTER U WITH DIAERESIS

    0xc0: u"a", # À LATIN CAPITAL LETTER A WITH GRAVE
    0xc1: u"a", # Á LATIN CAPITAL LETTER A WITH ACUTE
    0xc3: u"a", # Ã LATIN CAPITAL LETTER A WITH TILDE
    0xc7: u"c", # Ç LATIN CAPITAL LETTER C WITH CEDILLA
    0xc8: u"e", # È LATIN CAPITAL LETTER E WITH GRAVE
    0xc9: u"e", # É LATIN CAPITAL LETTER E WITH ACUTE
    0xca: u"e", # Ê LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    0xcc: u"i", # Ì LATIN CAPITAL LETTER I WITH GRAVE
    0xcd: u"i", # Í LATIN CAPITAL LETTER I WITH ACUTE
    0xd2: u"o", # Ò LATIN CAPITAL LETTER O WITH GRAVE
    0xd3: u"o", # Ó LATIN CAPITAL LETTER O WITH ACUTE
    0xd5: u"o", # Õ LATIN CAPITAL LETTER O WITH TILDE
    0xd9: u"u", # Ù LATIN CAPITAL LETTER U WITH GRAVE
    0xda: u"u", # Ú LATIN CAPITAL LETTER U WITH ACUTE

    0xdf: u"s", # ß LATIN SMALL LETTER SHARP S
    0xe6: u"a", # æ LATIN SMALL LETTER AE
    0xf0: u"d",  # ð LATIN SMALL LETTER ETH
    0xf8: u"o", # ø LATIN SMALL LETTER O WITH STROKE
    0xfe: u"t", # þ LATIN SMALL LETTER THORN,
    0xe4: u'a', # ä LATIN SMALL LETTER A WITH DIAERESIS
    0xf6: u'o', # ö LATIN SMALL LETTER O WITH DIAERESIS
    0xfc: u'u', # ü LATIN SMALL LETTER U WITH DIAERESIS

    0xe0: u"a", # à LATIN SMALL LETTER A WITH GRAVE
    0xe1: u"a", # á LATIN SMALL LETTER A WITH ACUTE
    0xe3: u"a", # ã LATIN SMALL LETTER A WITH TILDE
    0xe7: u"c", # ç LATIN SMALL LETTER C WITH CEDILLA
    0xe8: u"e", # è LATIN SMALL LETTER E WITH GRAVE
    0xe9: u"e", # é LATIN SMALL LETTER E WITH ACUTE
    0xea: u"e", # ê LATIN SMALL LETTER E WITH CIRCUMFLEX
    0xec: u"i", # ì LATIN SMALL LETTER I WITH GRAVE
    0xed: u"i", # í LATIN SMALL LETTER I WITH ACUTE
    0xf2: u"o", # ò LATIN SMALL LETTER O WITH GRAVE
    0xf3: u"o", # ó LATIN SMALL LETTER O WITH ACUTE
    0xf5: u"o", # õ LATIN SMALL LETTER O WITH TILDE
    0xf9: u"u", # ù LATIN SMALL LETTER U WITH GRAVE
    0xfa: u"u", # ú LATIN SMALL LETTER U WITH ACUTE

    0x2018: u"'", # ‘ LEFT SINGLE QUOTATION MARK
    0x2019: u"'", # ’ RIGHT SINGLE QUOTATION MARK
    0x201c: u'"', # “ LEFT DOUBLE QUOTATION MARK
    0x201d: u'"', # ” RIGHT DOUBLE QUOTATION MARK
}

class unaccented_map(dict):
    def mapchar(self,key):
        ch = self.get(key)
        if ch is not None:
            return ch
        de = unicodedata.decomposition(unichr(key))
        if de:
            try:
                ch = int(de.split(None,1)[0],16)
            except (IndexError, ValueError):
                ch = key
        else:
            ch = charmap.get(key,key)
        self[key] = ch
        return ch
    if sys.version >= "2.5":
        __missing__ = mapchar
    else:
        __getitem__ = mapchar
tranmap = unaccented_map()
def asciify(input):
    return input.translate(tranmap)

