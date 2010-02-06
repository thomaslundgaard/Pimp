#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#    Cover Fetcher (for AmaroK 1.4) v1.0-2009-02-09
#    Copyright (C) 2008-2009 Markus Straub <code@ravage.at>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
#    Tested with: Python 2.5.2, PyQt 4.4.4, Amarok 1.4.10, KDE 4.2
#                 (Kubuntu 8.10)
################################################################################

import ConfigParser, commands, os, re, signal, shutil, sys, string, time
import thread, threading, traceback, Queue
import cStringIO, gzip, urllib, urllib2, xml.dom.minidom

from FetcherGui import Ui_Dialog as DcGui

try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
except:
    os.popen( "kdialog --sorry 'PyQt (Qt bindings for Python) is required for this script.'" )
    raise

# program options
debug_prefix = "[Cover Fetcher]"
discogsApiKey = "54050f373c"
playfmApiKey = "c4eeb5aa39807b0d21d420ab64b42bf6"
tmpDir = "/tmp/amarokcoverfetcher"
config = None # global instance of Configuration
configFile = "coverfetcher.conf" # contains limits for fetching
extensions = ("jpg", "jpeg", "png", "gif")

# global thread / qApp variables
debug = None # instance of debug output class 
mainThread = None
stdinReader = None
qApp = None # QApplication
releasesHandler = None

############################################################################
# class Gui ################################################################
############################################################################
class Gui( QFrame, DcGui ):
    
    def __init__(self):
        QFrame.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Cover Fetcher")
        
        # working path = ~/.kde/share/apps/amarok/scripts-data
        self.lastfmLabel.setPixmap(QPixmap("../scripts/CoverFetcher/lastfm.gif"))
        self.discogsLabel.setPixmap(QPixmap("../scripts/CoverFetcher/discogs.gif"))
        
        self.releasesHandler = None
        self.debugHandler = None # to call when updateStatus() signal is received
        
        # start with a clean state (disable buttons)
        self.updateGui(clean=True)
        
        self.__progressDots = 0 # amount of progressdots shown in GUI
        self.__coverScaled = False
        
    def keyPressEvent(self, keyEvent):
        if(keyEvent.key() == Qt.Key_Escape):
            self.onCancel()
        if(keyEvent.key() == Qt.Key_Z and keyEvent.modifiers() == Qt.AltModifier):
            self.onCoverClick()
            
    def connectToReleasesHandler(self, releasesHandler):
        self.releasesHandler = releasesHandler
        
        self.connect(self.pushButtonSave, SIGNAL("clicked()"), self.releasesHandler.onSave)
        self.connect(self.pushButtonDelete, SIGNAL("clicked()"), self.releasesHandler.onDelete)
        self.connect(self.pushButtonNext, SIGNAL("clicked()"), self.releasesHandler.onNext)
        self.connect(self.pushButtonPrev, SIGNAL("clicked()"), self.releasesHandler.onPrev)
        self.connect(self.pushButtonSearch, SIGNAL("clicked()"), self.onReturn)
        self.connect(self.searchLineEdit, SIGNAL("returnPressed()"), self.onReturn)
        self.connect(self.coverLabel, SIGNAL("clicked()"), self.onCoverClick)
        self.connect(self.listWidget, SIGNAL("itemSelectionChanged()"), self.onListItemChanged)
        buttons = self.configButtonBox.buttons()
        for button in buttons:
            if(self.configButtonBox.buttonRole(button) == QDialogButtonBox.ResetRole):
                self.connect(button, SIGNAL("clicked()"), self.configReset)
            else:
                self.connect(button, SIGNAL("clicked()"), self.configSave)
        
    def setDebugHandler(self, debugHandler):
        self.debugHandler = debugHandler
        # update to display already queued debug output
        self.updateStatus(waitingMessage=False)
    
    def closeEvent(self, event):
        # override alt+f4 or closing of window
        self.onCancel()
        event.ignore() 
    
    def configSave(self):
        namingScheme = None
        if(self.idRadioButton.isChecked()):
            namingScheme = Configuration.ID_SCHEME
        elif(self.albumRadioButton.isChecked()):
            namingScheme = Configuration.ALBUM_SCHEME
        elif(self.fixedRadioButton.isChecked()):
            namingScheme = Configuration.FIXED_SCHEME
        config.setValues(self.discogsSpinBox.value(), self.lastfmSpinBox.value(),
                         self.overWriteCheckBox.isChecked(), namingScheme,
                         self.fixedLineEdit.text())
        # update GUI to enable / disable buttons
        self.releasesHandler.prepareGuiData()
        
    def configReset(self):
        self.discogsSpinBox.setValue(config.getDiscogsLimit())
        self.lastfmSpinBox.setValue(config.getLastfmLimit())
        self.fixedLineEdit.setText(config.getFixedName())
        self.overWriteCheckBox.setChecked(config.getAllowOverwrite())
        scheme = config.getFileNameScheme()
        if(scheme == Configuration.ID_SCHEME):
            self.idRadioButton.setChecked(True)
        elif(scheme == Configuration.ALBUM_SCHEME):
            self.albumRadioButton.setChecked(True)
        else:
            self.fixedRadioButton.setChecked(True)
    
    def onListItemChanged(self):
        index = self.listWidget.currentRow()
        self.releasesHandler.setListRow(index)
    
    def onReturn(self):
        string = self.searchLineEdit.text().toUtf8()
        searchString = str(string).decode('utf-8')
        self.releasesHandler.setSearchString(searchString)
        self.updateGui(clean=True)
        self.releasesHandler.start()
  
    def onCoverClick(self):
        if(self.coverLabel.pixmap() != None and self.coverLabel.pixmap().isNull() == False):
            if(self.__coverScaled):
                self.coverLabel.setPixmap(QPixmap(self.releasesHandler.getImagePath()))
            else:
                w = self.coverLabel.width()
                h = self.coverLabel.height()
                self.coverLabel.setPixmap(self.coverLabel.pixmap().scaled(w, h, Qt.KeepAspectRatio))
            self.__coverScaled = not self.__coverScaled 
                
    def onCancel(self):
        # the next line would eat up stdin for readStdin method .. 
        # no more input after the gui has been closed once!
        # so we just resort to having one GUI instance :)
        #self.close()
        self.hide()
        
    def showConfig(self):
        index = self.tabWidget.indexOf(self.configurationTab)
        self.tabWidget.setCurrentIndex(index)
        self.show()
        
    def showGui(self):
        #self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive);
        index = self.tabWidget.indexOf(self.coverTab)
        self.tabWidget.setCurrentIndex(index)
        self.updateGui(clean=True)
        self.show()
        
    def updateGui(self, clean=False):
        # don't allow late updates of hidden GUI (user already closed 
        # the window!) .. only allow cleanup calls
        if(self.isHidden() and clean == False):
            return
        
        list = QStringList()
        if(clean):
            # cover image
            imagePath = ""
            # buttons
            btDisable = [True]*4
        else:
            # result list
            listEntries = self.releasesHandler.getListEntries()
            for str in listEntries:
                list.append(str)
            #listRow = self.releasesHandler.getListRow()
            # cover image
            imagePath = self.releasesHandler.getImagePath()
            # buttons
            btDisable = self.releasesHandler.getButtonStates()
        
        # update search field (always show it, also in clean state!)
        # search string
        if(self.releasesHandler != None):
            searchString = self.releasesHandler.getSearchString()
            self.searchLineEdit.setText(searchString)
        
        # update result list (only nr of local images can vary)
        widgetItem = self.listWidget.item(0)
        if(clean or widgetItem == None):
            # we shall clean the gui or the list empty, add entries
            self.listWidget.clear()
            self.listWidget.addItems(list)
            # this triggers another gui update, but that shouldn't bother us
            if(len(list) > 0):
                self.listWidget.setCurrentRow(0)
        else:
            # list already exists, only update first entry
            widgetItem.setText(list.first())
        
        # set cover image (or debug text)
        self.__progressDots = 0
        self.__coverScaled = False
        debug.debug("Create pixmap from %s\n" % imagePath)
        self.coverLabel.setText("")
        self.coverLabel.setPixmap(QPixmap(imagePath))

        # en/disable buttons
        self.pushButtonSave.setDisabled(btDisable[0])
        self.pushButtonDelete.setDisabled(btDisable[1])
        self.pushButtonPrev.setDisabled(btDisable[2])
        self.pushButtonNext.setDisabled(btDisable[3])

        # init configuration
        self.configReset()
    
    def updateStatusWithProgressDots(self):
        self.updateStatus(waitingMessage = True)
    
    def updateStatus(self, waitingMessage=False):
        while(self.debugHandler.hasStatusMessage()):
            msg = self.debugHandler.getStatusMessage()
            msgHtml = msg.replace("\n", "<br />")
            # move textCursor to the end
            textCursor = self.logTextEdit.textCursor()
            textCursor.movePosition(QTextCursor.End)
            self.logTextEdit.setTextCursor(textCursor)
            
            # insert text
            if("ERROR" in msg):
                self.logTextEdit.textCursor().insertHtml('<span style=" font-weight:600; color:#ff0000;">' + msgHtml+ '</span>')
            elif("WARNING" in msg):
                self.logTextEdit.textCursor().insertHtml('<span style=" font-weight:600; color:#ffaa00;">' + msgHtml+ '</span>')
            elif("NEW SEARCH" in msg):
                self.logTextEdit.textCursor().insertHtml('<span style=" font-weight:600; color:#ffffff; background-color:#000000">' + msgHtml+ '</span>')
            else:
                self.logTextEdit.textCursor().insertHtml(msgHtml)
                
            if(waitingMessage):
                self.coverLabel.setText("fetching data, please wait" + "."*self.__progressDots)
                self.__progressDots = (self.__progressDots + 1)
            else:
                self.coverLabel.setText("")
                self.__progressDots = 0
                
            if("ERROR" in msg):
                self.coverLabel.setText(msg)
                #self.searchLineEdit.setEnabled(False)
                index = self.tabWidget.indexOf(self.logTab)
                self.tabWidget.setCurrentIndex(index)
        

############################################################################
# class Releases ###########################################################
############################################################################
class Release:
    """ Container class for images of a Discogs Release
        handles image downloading / copying / deleting """
    
    def __init__(self, path, name, albumName, isLocal=False):
        """ create new Release, path must end with a slash """
        if(path[-1] != "/"):
            path = path + "/"
        self.__path = path
        self.__name = name # name as shown in GUI
        self.__albumName = albumName
        self.__img = [] # local or remote images
        self.__imgTmp = [] # tmp images in case of remote images
        self.__isLocal = isLocal
        
        if(isLocal):
            for ext in extensions:
                #stream = os.popen2('find "%s" -maxdepth 1 -iname "*.%s"' % (self.__path.replace("\"", "\\\""), ext))[1]
                #time.sleep(0.1)    # to avoid "IOError: [Errno 4] Interrupted system call"
                # see http://jbrout.python-hosting.com/changeset/19
                cmd = 'find "%s" -maxdepth 1 -iname "*.%s"' % (self.__path.replace("\"", "\\\""), ext)
                files = commands.getoutput(cmd.encode('utf-8'))
                for fileName in files.split("\n"):
                    if(fileName != ""):
                        self.__img.append(unicode(fileName, 'utf-8'))
            self.__imgTmp = self.__img[:]
            debug.debug("Found %d existing local images\n" % len(self.__img), informGui=True)
        
    def __download( self, url ):
        """ Copy the contents of a file from a given URL to a tmp local file. 
            return name of local file or "" if download failed """
        try:
            tmpFileName = tmpDir + "/" + (url.split('/')[-1])
            webFile = urllib.urlopen(url)
            tmpFile = open(tmpFileName, 'w')
            tmpFile.write(webFile.read())
            webFile.close()
            tmpFile.close()
        except IOError:
            debug.debug("ERROR: Download of file '%s' to '%s' failed\n" % (url, tmpFileName), informGui=True )
            return ""
        return tmpFileName
        
    def addImages(self, images, isLocal=False):
        """ add images, supply list of strings """
        if(images == None or len(images) == 0):
            return
        self.__img.extend(images)
        if(isLocal):
            self.__imgTmp.extend(images)
        else:
            self.__imgTmp.extend([""] * len(images))
 
    def getImage(self, imageNr):
        """ returns the tmp path of the image (or an empty string) 
            tmp path for local images = normal path
            tmp path for remote images = path in local temporary folder """
        if(imageNr < 0 or imageNr >= len(self.__img)):
            return "" 
        elif(self.__imgTmp[imageNr] == ""):
            debug.debug("Downloading '%s'... " % self.__img[imageNr], informGui=True, progressDots=True)
            tmpFile = self.__download(self.__img[imageNr])
            if(tmpFile != ""):
                self.__imgTmp[imageNr] = tmpFile
                debug.debug("done\n", informGui=True, progressDots=True)
            else:
                debug.debug("failed\n", informGui=True, progressDots=True)
        return self.__imgTmp[imageNr]
    
    def getLocalImage(self, imageNr):
        """ returns path where image will be stored
            (respects the current configuration (fixed/id/album name!) """
        if(imageNr < 0 or imageNr >= len(self.__img)):
            return ""
        
        if(config.getFileNameScheme() == Configuration.ID_SCHEME):
            dest = self.__path + self.__imgTmp[imageNr].rsplit("/", 1)[1]
        elif(config.getFileNameScheme() == Configuration.ALBUM_SCHEME):
            dest = self.__path + self.__albumName + "." + self.__imgTmp[imageNr].rsplit(".", 1)[1]
        else:
            dest = self.__path + config.getFixedName() + "." + self.__imgTmp[imageNr].rsplit(".", 1)[1]
        # must use unicode, since after config changes a QString is returned, not a python string
        return unicode(dest)
       
    def saveRemoteImage(self, imageNr):
        """ copy an image from tmp to path
            returns a tuple of the path of the copy or "" if copying failed 
            and a list of files to delete from local covers """
            
        if(self.__isLocal or self.__path == "" or imageNr >= len(self.__img)):
            return ("", None)
        
        try:
            if(self.__imgTmp[imageNr] != ""):
                try:
                    dest = self.getLocalImage(imageNr)
                    
                    # check images with the same name (and different extension) exist
                    existingFiles = [] 
                    destNoExt = dest.rsplit(".",1)[0]
                    for ext in extensions:
                        if(os.path.exists(destNoExt + "." + ext)):
                            existingFiles.append(destNoExt + "." + ext)
                    
                    if(len(existingFiles) == 0):
                        # new cover image, just add it
                        shutil.copyfile(self.__imgTmp[imageNr], dest)
                        return (dest, None)
                    elif(len(existingFiles) == 1 and dest in existingFiles):
                        # a cover exists (same name, same extension)
                        if(config.getAllowOverwrite() == True):
                            shutil.copyfile(self.__imgTmp[imageNr], dest)
                        return ("", None)
                    else:
                        # one or several covers exists (same name, maybe different extension)
                        if(config.getAllowOverwrite() == True):
                            # overwrite / store new image
                            shutil.copyfile(self.__imgTmp[imageNr], dest)
                            # if image was overwritten delete it here
                            if(dest in existingFiles):
                                existingFiles.remove(dest)
                            return (dest, existingFiles)
                        else:
                            return ("", None)
                    
                except OSError, e:
                    debug.debug( "ERROR: Copying of file failed\n", informGui=True)
                    traceback.print_exc(file=sys.stderr)
                    return ("", None)
        except IndexError:
            return ("", None)
    
    def deleteLocalImageByFileName(self, filename):
        """ deletes a local image, returns True / False """
        if(filename in self.__img):
            index = self.__img.index(filename)
            return self.deleteLocalImage(index)
        else:
            return False
    
    def deleteLocalImage(self, imageNr):
        """ delete an image from path
            returns True / False """
        if(not self.__isLocal or self.__path == "" or imageNr >= len(self.__img)):
            return False
        
        if(self.__img[imageNr] != ""):
            try:
                os.remove(self.__img[imageNr])
                self.__img.pop(imageNr)
                self.__imgTmp.pop(imageNr)
                return True
            except OSError, e:
                # if not "No such file or directory"
                if(e.errno == 2):
                    debug.debug( "ERROR: Could not delete image, file doesn't exist: '%s'\n" % self.__img[imageNr], informGui=True)
                else:
                    debug.debug( "ERROR: Could not delete image '%s'\n" % self.__img[imageNr], informGui=True)
                    return False
        
    def getImageCount(self):
        return len(self.__img)

    def getPath(self):
        return self.__path

    def getName(self):
        return "%d - %s" % (len(self.__img), self.__name)
    
    def isLocalRelease(self):
        return self.__isLocal
        
class ReleasesHandler(QThread):
    """ core of the model (from MVC), gets signals from gui and
        fetches according releases.
        then it signals GUI to get the fetched information """
        
    def __init__(self):
        QThread.__init__(self)
        self.discogsFetcher = DiscogsDataFetcher()
        self.lastfmFetcher = LastFmDataFetcher()
        self.stdinReader = None
        self.releases = []
        """ Releases that were fetched from Discogs """
        self.activeRelease = None
        """ Release currently being shown """
        self.activeImageNr = -1
        """ ImageNr currently being shown """
        self.userdefinedSearch = False
        """ did the user refine the searchterm or shall it be fetched from amarok """
        self.searchString = ""
        """ current search string, for display in the GUI """
        self.listEntries = []
        """ list of strings with album names """
        self.listRow = 0
        """ currently marked row in the list of entries """
        self.path = "/tmp/test.mp3" # this value is for debugging purposes only!
        """ current path into which images are stored 
            (path is usually fetched for currently playing track from amarok) """
        
        self.mutex = QMutex()
        
        # gui-relevant variables
        #standard: disable all buttons
        self.btDisable = [True]*4 # which buttons in the GUI are en/disabled
        self.imagePath = "" # path of current image
        self.description = ""
        
    def run(self):
        """ searches discogs for covers.
            searchString is set: no path will be fetched from amarok,
            since the user is trying to find a coveralbum the song
            that was playing the instance when he clicked the button, song may
            be different now
            
            searchString is omitted (normal usage):
            information about the currently
            playing track will be received from amarok over dcop.
            fetched information will be stored in self.releases """
        
        debug.debug("NEW SEARCH...\n", informGui=True, progressDots=True)
        
        # thread must run only once a time
        self.mutex.lock()
        
        if(not self.userdefinedSearch):
            # old variant:
            #stream = os.popen2("dcop amarok player isPlaying")[1]
            #time.sleep(0.1)    # to avoid "IOError: [Errno 4] Interrupted system call"  
            #isPlaying = stream.readline().replace("\n","")
            isPlaying = commands.getoutput("dcop amarok player isPlaying")
            if(isPlaying != "true"):
                debug.debug("ERROR: No track is playing\n", informGui=True)
                self.activeRelease = None
                self.activeImageNr = -1
                self.prepareGuiData()
                self.mutex.unlock()
                return
            
            # get information from Amarok
            artist = commands.getoutput("dcop amarok player artist").decode('utf-8')
            title = commands.getoutput("dcop amarok player title").decode('utf-8')
            album = commands.getoutput("dcop amarok player album").decode('utf-8')
            self.albumName = album
            # path actually means path+filename here
            self.path = commands.getoutput("dcop amarok player path").decode('utf-8')
    
            if(artist != "" and album != ""):
                self.searchString = artist + " - " + album
            elif(artist != "" and title != ""):
                self.searchString = artist + " - " + title
            elif(self.path != ""):
                # strip filename from path (without extension)
                filename = self.path.rsplit("/", 1)[1]
                self.searchString = filename.rsplit(".", 1)[0]
            
            debug.debug("Using search term '%s'\n" % self.searchString, informGui=True)
        else: #userdefinedSearch==True
            self.userdefinedSearch = False
        
        # now that we know the new searchTerm show the GUI
        self.emit(SIGNAL("updateGui()"))
        self.emit(SIGNAL("showGui()"))
         
        # remove filename from path
        self.albumPath = self.path.rsplit("/", 1)[0]
        debug.debug("Local path to store covers: %s\n" % self.albumPath, informGui=True)
        
        # add local covers
        self.releases = [Release(self.albumPath, "[Local Covers] " + self.albumPath, "", isLocal=True)]
        # search for and add covers from last.fm
        if(config.getLastfmLimit() > 0):
            r = self.lastfmFetcher.search(self.searchString, self.albumPath)
            if(len(r) > 0):
                self.releases.extend(r)
        # search for and add covers from discogs 
        if(config.getDiscogsLimit() > 0):
            r = self.discogsFetcher.search(self.searchString, self.albumPath)
            if(len(r) > 0):
                self.releases.extend(r)

        # reset currently shown information
        self.activeImageNr = -1
        self.activeRelease = None
        
        self.prepareGuiData()
        self.mutex.unlock()
        
    def setSearchString(self, searchString):
        self.searchString = searchString
        self.userdefinedSearch = True
    
    def setStdinReader(self, stdinReader):
        self.stdinReader = stdinReader
        
    def getStdinMessage(self):
        """ a message from Amarok has been received from StinReader, get it """
        
        line = self.stdinReader.getLine()
                
        debug.debug( "Received notification: " + line )

        if (line.find( "configure" ) != -1):
            self.onConfigure()
        elif (line.find( "customMenuClicked: F&etch Cover &For Currently Playing Track" ) != -1 or
              line.find( "searchDcop" ) != -1):
            # run run() once
            self.start()
        
############################################################################
# Gui Event Handling
# these methods are called via signals:

    def onNext(self):
        # check if there is a next image
        if(self.activeRelease != None):
            if(self.activeImageNr < self.activeRelease.getImageCount()-1):
                self.activeImageNr += 1
        self.prepareGuiData()
    
    def onPrev(self):
        # check if there is a prev image
        if(self.activeImageNr > 0):
            self.activeImageNr -= 1
        self.prepareGuiData()
    
    def onSave(self):
        path, toDelete = self.activeRelease.saveRemoteImage(self.activeImageNr)
        # first delete obsolete image(s)
        localRelease = self.releases[0]
        if(toDelete != None):
            for fileName in toDelete:
                localRelease.deleteLocalImageByFileName(fileName)
        # then add new one
        if(path != ""):
            localRelease.addImages([path], isLocal=True)
        self.prepareGuiData()

    def onDelete(self):
        self.activeRelease.deleteLocalImage(self.activeImageNr)
        if(self.activeRelease.getImageCount() == 0):
            self.activeImageNr = -1
        elif(self.activeImageNr >= self.activeRelease.getImageCount()):
            # last image was deleted, go one prev
            self.activeImageNr -= 1
        
        # else:
        #     let activeImageNr as it is -> will display next image
        self.prepareGuiData()
        
    def onConfigure(self):
        self.emit(SIGNAL("showConfig()"))
        
    def setListRow(self, row):
        self.listRow = row
        self.activeRelease = self.releases[self.listRow]
        self.activeImageNr = -1
        self.prepareGuiData()
        
    def getListRow(self):
        return self.listRow
        
    def prepareGuiData(self):
        debug.debug("prepareGuiData - %d releases available, show imageNr %d" % (len(self.releases), self.activeImageNr))
        
        # try to set an active release and image
        if(self.activeRelease == None):
            if(len(self.releases) > 0):
                self.activeRelease = self.releases[0]
                self.activeImageNr = -1
            else:
                return
        if(self.activeImageNr == -1):
            if(self.activeRelease.getImageCount() > 0):
                self.activeImageNr = 0
        
        btDisable = [True]*4
        imagePath = ""
        listEntries = []
        for release in self.releases:
            listEntries.append(release.getName())

        # if it succeeded, get information
        if(self.activeImageNr >= 0):
            imagePath = self.activeRelease.getImage(self.activeImageNr)
            debug.debug("imagePath: %s, imageNr: %d" % (imagePath, self.activeImageNr))
            if(self.activeRelease.isLocalRelease()):
                if(imagePath != ""):
                    btDisable[1] = False #enable delete
            else:
                if(imagePath != ""):
                    dest = self.activeRelease.getLocalImage(self.activeImageNr)
                    # don't overwrite files if user doesn't want it
                    # check for all extensions!
                    exists = False 
                    destNoExt = dest.rsplit(".",1)[0]
                    for ext in extensions:
                        if(os.path.exists(destNoExt + "." + ext)):
                            exists = True
                    
                    if(not exists or (exists and config.getAllowOverwrite())):
                        btDisable[0] = False #enable save
                
            if(self.activeImageNr > 0):
                btDisable[2] = False # enable prev
            
            if(self.activeImageNr < self.activeRelease.getImageCount()-1):
                btDisable[3] = False # enable next
            
        # store results for GUI
        self.btDisable = btDisable
        self.imagePath = imagePath
        self.listEntries = listEntries
        # update gui
        self.emit(SIGNAL("updateGui()"))
        
    def getButtonStates(self):
        return self.btDisable
    def getListEntries(self):
        return self.listEntries
    def getImagePath(self):
        return self.imagePath
    def getSearchString(self):
        return self.searchString


############################################################################
# class DiscogsDataFetcher##################################################
############################################################################
class DiscogsDataFetcher:
    """ searches discogs for releases / covers """
    
    def __init__(self):
        self.searchString = ""
        self.albumPath = ""
        self.releases = []
        """ Releases that were found for searchString """
   
    def __askDiscogs( self, requestUrl ):
        """ @param requestUrl: url for the xml request where f=xml&api_key=<key> 
            will be added
            takes the first part of a request-URL, adds the api key, requests
            data, unzips it and returns the XML response """
        requestUrl = requestUrl + "f=xml&api_key=" + discogsApiKey
        debug.debug("Requesting from Discogs: %s\n" % requestUrl, informGui=True, progressDots=True)
        request = urllib2.Request(requestUrl)
        request.add_header('Accept-Encoding', 'gzip')
        try:
            response = urllib2.urlopen(request) #TODO Interrupted system call possible here!!
        except urllib2.URLError, e:
            debug.debug("ERROR: No connection to discogs.com\n(Probably your internet connection or discogs.com is down)\n", informGui=True, progressDots=True)
            return ""
        data = response.read()
        try:
            return gzip.GzipFile(fileobj = cStringIO.StringIO(data)).read()
        except IOError:
            # in case of IOError data is not gzipped
            return data
    
    def __parseReleaseXml( self, xmlString ):
        """ parses XML response and creates a Release instance
            if a Release doesn't contain images or an error occured
            None is returned """
        try:
            tree = xml.dom.minidom.parseString(xmlString)
            if(tree.documentElement.getAttribute("stat") != "ok"):
                debug.debug("ERROR: Bad response from Discogs server\n", informGui=True, progressDots=True)
                return None
            
            requestNr = tree.documentElement.getAttribute("requests")
            release = tree.documentElement.firstChild
            releaseId = release.getAttribute("id")
            imageUris = []
            imagesNodes = release.getElementsByTagName("images")
            if(len(imagesNodes) < 1):
                return None
            for image in imagesNodes[0].childNodes:
                imageUris.append(image.getAttribute("uri"))
            
            artistList = []
            for a in tree.getElementsByTagName("artists"):
                art = a.getElementsByTagName("name")[0].firstChild.data
                if(art not in artistList):
                    artistList.append(art)
            try:
                artistList.remove("Various")
            except ValueError, e:
                pass
            artists = string.join(artistList, " & ")
            title = tree.getElementsByTagName("title")[0].firstChild.data
            catalogNr = tree.getElementsByTagName("label")[0].getAttribute("catno")
            format = tree.getElementsByTagName("format")[0].getAttribute("name")
            desc = "[%s/%s] %s - %s" % (catalogNr, format, artists, title)
            
            # create Release
            r = Release(self.albumPath, desc, title, isLocal=False)
            r.addImages(imageUris)
            return r
                           
        except xml.parsers.expat.ExpatError:
            debug.debug("ERROR: Discogs server sent invalid XML response\n", informGui=True, progressDots=True)
    
    def __parseSearchXml( self, xmlString ):
        """ parses XMl responses for a search and returns a list 
            with all Releases """
        releases = []
        if(xmlString == ""):
            return releases
        if(xmlString.find("<!DOCTYPE html PUBLIC") > -1):
            debug.debug("WARNING: Received data is HTML (Parser error)\n", informGui=True)
            return releases
        
        try:
            tree = xml.dom.minidom.parseString(xmlString)
            if(tree.documentElement.getAttribute("stat") != "ok"):
                debug.debug("ERROR: Bad response from server (Status not ok)\n", informGui=True, progressDots=True)
                return
              
            reqestNr = tree.documentElement.getAttribute("requests")
            searchResults = tree.documentElement.firstChild
            searchResultNr = searchResults.getAttribute("numResults")
            
            debug.debug("Found %d possibly matching releases on Discogs\n" % int(searchResultNr), informGui=True, progressDots=True)
            if(int(searchResultNr) <= 0):
                return releases

            count = 0
            for searchResult in searchResults.childNodes: # for all releases
                element = searchResult.getElementsByTagName("uri")[0]
                #uri = element.firstChild.data
                # above method doesn't work since feb 2009, the
                # provided url can't be fetched in api-xml format, so
                # let's extract the release id
                uri = element.firstChild.data
                releaseId = uri[uri.rfind('/')+1:]
                uri = "http://www.discogs.com/release/" + releaseId
                release = self.__parseReleaseXml(self.__askDiscogs(uri + "?"))
                if(release != None):
                    releases.append(release)
                    count += 1
                if(count >= config.getDiscogsLimit()):
                    break
            debug.debug("Showing %d releases. (Max results = %d)\n" % (count, config.getDiscogsLimit()), informGui=True, progressDots=True)
            return releases
        except xml.parsers.expat.ExpatError, e:
            debug.debug("ERROR: Received data is invalid XML (Parser error)\n", informGui=True)
    

    def search (self, searchString, albumPath):
        """ search with provided searchString for matching releases,
            returns a List<Release> """
        self.searchString = searchString
        self.albumPath = albumPath
        self.releases = []
        try:
            # brute force (not good)
            #m = re.sub("[^a-zA-Z0-9 ]", "", searchString)
            #encode to utf-8, otherwise urllib quote will fail
            searchString = searchString.encode('utf-8')
            searchString = urllib.quote_plus(searchString)
            url = "http://www.discogs.com/search?type=releases&q=" + searchString + "&"
            xmlResponse = self.__askDiscogs(url)
            if(xmlResponse == None):
                debug.debug("ERROR: No response from Discogs server\n", informGui=True, progressDots=True)
                return;
            
            self.releases = []
            # fetch releases from discogs
            releases = self.__parseSearchXml(xmlResponse)
            if(releases == None or len(releases) == 0):
                debug.debug("WARNING: No matching release found on Discogs\n", informGui=True, progressDots=True)
            else:
                self.releases.extend(releases)
                
            return self.releases
        except Exception:
            debug.debug("ERROR: Fetching '%s' from Discogs failed\n" % searchString, informGui=True, progressDots=True)
            traceback.print_exc(file=sys.stderr)
            self.releases = []
            return self.releases
        
############################################################################
# class LastFmDataFetcher ##################################################
############################################################################
class LastFmDataFetcher:
    
    def __init__(self):
        self.artist = ""
        self.album = ""
        self.albumPath = ""
        self.releases = []
    
    def __askLastfm(self, requestUrl):
        """ @param requestUrl: url for the xml request
            returns the XML response """
        debug.debug("Requesting from Last.fm: %s\n" % requestUrl, informGui=True)
        request = urllib2.Request(requestUrl)
        request.add_header('Accept-Encoding', 'gzip')
        data = None
        try:
            print "shit"
            response = urllib2.urlopen(request) #TODO Interrupted system call possible here!!
            data = response.read()
        except urllib2.URLError, e:
            print " off line "
            if hasattr(e, 'reason'):
                debug.debug("ERROR: No connection to last.fm\n(Probably your internet connection or last.fm is down)\n", informGui=True, progressDots=True)
                return ""
            data = e.read()
        try:
            return gzip.GzipFile(fileobj = cStringIO.StringIO(data)).read()
        except IOError:
            # in case of IOError data is not gzipped
            return data
        
    def search(self, searchString, albumPath):
        """ search with provided searchString for matching releases,
            returns a List<Release> or an empty list"""
        if(searchString == ""):
            return []
        self.albumPath = albumPath
        self.releases = []
        tokens = searchString.split(" - ")
        if(len(tokens) < 2):
            debug.debug("WARNING: Search term not of form 'artist - album', can't query last.fm\n", informGui=True, progressDots=True)
        for i in range(1, len(tokens)):
            # create all possible artist / album variations
            
            artistUnicode = string.join(tokens[:i], " - ")
            artist = artistUnicode.encode('utf-8')
            artist = urllib.quote_plus(artist)
            
            albumUnicode = string.join(tokens[i:], " - ")
            album = albumUnicode.encode('utf-8')
            album = urllib.quote_plus(album)
            
            url = "http://ws.audioscrobbler.com/2.0/?method=album.getInfo&artist=" \
                  + artist + "&album=" + album + "&api_key=" + playfmApiKey
        
            xmlResponse = self.__askLastfm(url)
            if(xmlResponse == ""):
                continue
            cover = ""
            try:
                xmlParser = xml.dom.minidom.parseString(xmlResponse)
                # check for errors
                errTags = xmlParser.getElementsByTagName("error")
                if(len(errTags) > 0):
                    if(errTags[0].getAttribute("code") == "6"):
                        # code 6 = no release found
                        pass
                    else:
                        errorString = errTags[0].firstChild.data
                        debug.debug("ERROR while getting data from play.fm: %s\n" % errorString, informGui=True, progressDots=True)
                    # error ocured, no valid release
                    continue
                
                covers = xmlParser.getElementsByTagName("image")
                for c in covers:
                    if(c.getAttribute("size") == "large"):
                        cover = c.firstChild.data
                        break
                xmlParser.unlink()
            except xml.parsers.expat.ExpatError, e:
                debug.debug("ERROR: Parsing of Play.fm response failed: %s\n" % e, informGui=True, progressDots=True)
                continue
        
            desc = "[LastFM] " + artistUnicode + " - " + albumUnicode
            r = Release(self.albumPath, desc, albumUnicode, isLocal=False)
            r.addImages([cover])
            self.releases.append(r)
        
        debug.debug("Found %d possibly matching releases on last.fm\n" % len(self.releases), informGui=True, progressDots=True)
        if(len(self.releases) == 0):
            debug.debug("WARNING: No matching release found on last.fm\n", informGui=True, progressDots=True)
        return self.releases

############################################################################
# class DebugHandler #######################################################
############################################################################
class DebugHandler(QObject):
    
    def __init__(self):
        QObject.__init__(self)
        self.statusQueue = Queue.Queue() # statusmessage while fetching data
        
    def debug(self, message, level=2, informGui=False, progressDots=False):
        """ Prints debug message to stdout (level 1) or stderr (level 2)
            and shows up as message in the GUI if informGui is set
            use informGui to put the message into the Log window.
            additionally set progressDots for a please wait message in the 
            cover display"""
        debugString = "%s %s" % (debug_prefix, message)
        
        #file = open("/home/voodoo/Desktop/log","a")
        #file.write(message.encode('utf-8', 'replace')+"\n")
        #file.close()
        
        if(sys.stdout.encoding != None):
            debugStringEnc = debugString.encode(sys.stdout.encoding)
        else:
            debugStringEnc = debugString.encode('ascii', 'replace')
            
        if level == 1: # stdout
            print debugStringEnc
        elif level >= 2: # stderr (visible in Amarok Scripts -> Debug Output) 
            print >> sys.stderr, debugStringEnc
    
        if(informGui and progressDots):
            self.statusQueue.put(message, block=False)
            self.emit(SIGNAL("updateStatusWithProgressDots()"))
        elif(informGui):
            self.statusQueue.put(message, block=False)
            self.emit(SIGNAL("updateStatus()"))
        
    def getStatusMessage(self):
        return self.statusQueue.get(block=False)
    
    def hasStatusMessage(self):
        return not self.statusQueue.empty()
    
############################################################################
# class StdinReader ########################################################
############################################################################
class StdinReader(QThread):
    """ Amarok sends notifications to all running scripts 
    by writing strings to their stdin channel, this class catches all these
    notifications """
    def __init__(self):
        QThread.__init__(self)
        self.running = True
        self.queue = Queue.Queue()
    
    def pleaseStop(self):
        self.running = False
    
    def run(self):
        """ Reads incoming notifications from stdin """
        while self.running:
            # Read data from stdin. Will block until data arrives.
            line = 0
            try:
                line = sys.stdin.readline()
            except IOError:
                # TODO - any way to fix IOError: [Errno 4] Interrupted system call
                debug.debug( "WARNING: readStdin - IOError" )
                if line:
                    self.queue.put(line)
                    self.emit(SIGNAL("stdinMessage()"))
                continue
            
            if line:
                self.queue.put(line)
                self.emit(SIGNAL("stdinMessage()"))
            else:
                debug ("stop reading from Stdin")
                break
            
    def getLine(self):
        """ get the last queued line from stdin (or an empty string if
            something failed) """
        try:
            line = self.queue.get(False)
        except Queue.Empty:
            line = ""
        return line


############################################################################
# class Configuration ######################################################
############################################################################
class Configuration:
    
    ID_SCHEME = 0
    ALBUM_SCHEME = 1
    FIXED_SCHEME = 2
    
    def __init__(self, configFile):
        self.__configFile = configFile
        self.__discogsFetchLimit = None
        self.__lastfmFetchLimit = None
        self.__allowOverwrite = None
        self.__fileNameScheme = None
        self.__fixedName = None
        
        # read from config file / sanitize if it doesn't exist or contains errors
        self.__config = ConfigParser.ConfigParser()
        self.__config.read(configFile)
        write = False
        if(not self.__config.has_section("CoverFetcher")):
            self.__config.add_section("CoverFetcher")
            write = True
        
        discogs = None
        try:
            discogs = self.__config.getint("CoverFetcher", "discogsFetchLimit")
        except (ValueError, ConfigParser.NoOptionError):
            write = True
        
        lastfm = None
        try:
            lastfm = self.__config.getint("CoverFetcher", "lastfmFetchLimit")
        except (ValueError, ConfigParser.NoOptionError):
            write = True
            
        
        allowOverwrite = None
        try:
            allowOverwrite = self.__config.getboolean("CoverFetcher", "allowOverwrite")
        except (ValueError, ConfigParser.NoOptionError):
            write = True
        
        fileNameScheme = None
        try:
            fileNameScheme = self.__config.getint("CoverFetcher", "fileNameScheme")
        except (ValueError, ConfigParser.NoOptionError):
            write = True
        
        fixedName = None
        try:
            fixedName = self.__config.get("CoverFetcher", "fixedName")
        except (ValueError, ConfigParser.NoOptionError):
            write = True   
        
        self.setValues(discogs, lastfm, allowOverwrite, fileNameScheme, fixedName, write)
    
    def setValues(self, discogs, lastfm, allowOverwrite, fileNameScheme, fixedName, write=True):
        """ sanitize values and store them to the config file.
            contains all default config settings.
            write=False will be the case for loading a sane config file """
        
        if(discogs == None or discogs < 0 or discogs > 15):
            discogs = 3
            write = True
        if(lastfm == None or lastfm < 0 or lastfm > 1):
            lastfm = 1
            write = True
        if(allowOverwrite == None):
            allowOverwrite = False
            write = True
        if(fileNameScheme == None or fileNameScheme < self.ID_SCHEME or fileNameScheme > self.FIXED_SCHEME):
            fileNameScheme = self.ID_SCHEME
            write = True
        if(fixedName == None or len(fixedName) == 0):
            fixedName = "cover"
            write = True
        self.__discogsFetchLimit = discogs
        self.__lastfmFetchLimit = lastfm
        self.__allowOverwrite = allowOverwrite
        self.__fileNameScheme = fileNameScheme
        self.__fixedName = fixedName
        self.__config.set("CoverFetcher", "discogsFetchLimit", discogs)
        self.__config.set("CoverFetcher", "lastfmFetchLimit", lastfm)
        self.__config.set("CoverFetcher", "allowOverwrite", allowOverwrite)
        self.__config.set("CoverFetcher", "fileNameScheme", fileNameScheme)
        self.__config.set("CoverFetcher", "fixedName", fixedName)
        
        if(write):
            file = open(self.__configFile, 'w')
            self.__config.write(file)
            file.close()
            debug.debug("Configuration file written\n", informGui=True)
            
        
    def getDiscogsLimit(self):
        return self.__discogsFetchLimit
   
    def getLastfmLimit(self):
        return self.__lastfmFetchLimit
    
    def getAllowOverwrite(self):
        return self.__allowOverwrite
    
    def getFileNameScheme(self):
        return self.__fileNameScheme
    
    def getFixedName(self):
        return self.__fixedName

############################################################################
# class AmarokQApplication #################################################
############################################################################
class AmarokQApplication (QApplication):
    """ as pointed out in Amarok wiki:
        When using PyQt it is important to instruct the session manager
        NOT to handle the script's session state, otherwise the script
        will be started by KDE and by amarok, resulting (over time)
        in lots of processes running """
    def __init__(self, args):
        QApplication.__init__(self, args)
    
    def saveState(self, sessionmanager):
        # script is started by amarok, not by KDE's session manager
        sessionmanager.setRestartHint(QSessionManager.RestartNever)

def onStop(signum, stackframe):
    """ Called when script receives SIGTERM """
    global qApp, stdinReader
    
    # don't use debug output here, otherwise the script can't be terminated
    # when stopped from Amarok!
    
    #debug.debug("stopping script..")
    os.system("dcop amarok script removeCustomMenuItem 'F&etch Cover' '&For Currently Playing Track'")
    
    #debug.debug("exit QApplication main loop..")
    # exit qApplication (leave main-loop entered with exec_()
    qApp.exit(0)
    
    # and terminate running threads
    #stdinReader.pleaseStop()
    
    #clear tmp directory
    for name in os.listdir(tmpDir):
        fullName = os.path.join(tmpDir, name)
        os.remove(fullName)
    try:
        os.rmdir(tmpDir)
    except:
        pass
    #debug.debug("stopped.")


def main( ):
    global config, qApp, stdinReader, releasesHandler
    
    # create temp directory
    try:
        os.makedirs(tmpDir, 0777)
    except OSError, e:
        if(e.errno != 17):
            debug.debug("ERROR: could not create tmp directory %s" % tmpDir)
            return
        
    # read / sanitize configuration
    config = Configuration(configFile)
    
    # create qApp and GUI (=View)
    qApp = AmarokQApplication(sys.argv)
    gui = Gui()

    # Start separate thread for reading data from stdin (=Controller)
    stdinReader = StdinReader()
    stdinReader.start()
    
    # create releases handler (=Model)
    releasesHandler = ReleasesHandler()
    
    # establish communications connection between M V and C
    releasesHandler.setStdinReader(stdinReader)
    gui.connectToReleasesHandler(releasesHandler)
    gui.setDebugHandler(debug)
    QObject.connect(releasesHandler, SIGNAL("updateGui()"), gui.updateGui)
    QObject.connect(releasesHandler, SIGNAL("showGui()"), gui.showGui)
    QObject.connect(releasesHandler, SIGNAL("showConfig()"), gui.showConfig)
    QObject.connect(debug, SIGNAL("updateStatus()"), gui.updateStatus)
    QObject.connect(debug, SIGNAL("updateStatusWithProgressDots()"), gui.updateStatusWithProgressDots)
    QObject.connect(stdinReader, SIGNAL("stdinMessage()"), releasesHandler.getStdinMessage)
    
    # register functionality in Amarok
    os.system("dcop amarok script addCustomMenuItem 'F&etch Cover' '&For Currently Playing Track'")
        
    # start QT main loop
    qApp.exec_()

if __name__ == "__main__":
    # init debug handler
    debug = DebugHandler()
    # check if amarok is available
    result = commands.getstatusoutput("dcop amarok player version")
    if(result[0] == 0):
        workingpath = os.getcwd()
        debug.debug("Found Amarok %s, working path: %s\n" % (result[1], workingpath), informGui=True)
    else:
        debug.debug("ERROR: Amarok is not running or there is a problem with dcop (%s)" % result[1])
        debug.debug("Exiting..")
        sys.exit()
        
    # create new thread for program
    mainThread = threading.Thread(target=main)
    mainThread.start()
    debug.debug("main()-thread started")
    
    # listen for signal 15 / SIGTERM
    signal.signal(signal.SIGTERM, onStop)
    debug.debug("waiting for SIGTERM...")
    signal.pause()

