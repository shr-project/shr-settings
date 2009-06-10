import module, elementary, os, time, re
from glob import glob

from functools import partial

# Locale support
import gettext

"""
TODO: Make Home directory backup/restore module

NOTES:
  - Archive to a .tar file on the uSD card
  - Include all files in /home/${USER} except those listed in [DIRECTORY_BLACKLIST]
  - On restore (e.g. after a reflash) untar archived files, overriding the
    current /home/${USER}
"""

# Defaults
ARCHIVE_DIR  = "/media/card/"
ARCHIVE_FILE = "archive-{0}.tar" # {0} to be the date, filled in later
DATE_FORMAT  = "%Y%m%d-%H%M" # rather dense, but long archive names screw up the display

CONFIG_LIST = {
    'conf'      : '/etc/shr/settings/backup.conf',
    'whitelist' : '/etc/shr/settings/backup.whitelist',
    'blacklist' : '/etc/shr/settings/backup.blacklist',
    }

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class FileButton(elementary.Button):
    def set_filename( self, filename ):
        self.filename = filename
        self.label = self.get_trunc_path()
        self.set_label(self.label)

    def set_label( self, label):
        self.label_set( label )

    def set_objectLink( self, obj ):
        self.linked_object = obj

    def set_valueLink( self, obj ):
        self.linked_value = obj

    def get_trunc_path( self, length = 32 ):
        # deal with long file paths
        s = self.filename
        while len( s ) > length:
            s = s.split('/')
            if len( s ) == 2 :
                s = '.../' + '/'.join( s[1:] )
                break
            s = '.../' + '/'.join( s[2:] )
        return s

    def get_label( self ):
        return self.label

    def get_filename( self ):
        return self.filename

    def get_objectLink( self ):
        return self.linked_object

    def get_valueLink( self ):
        return self.linked_value

class SelectWindow(elementary.Window):
    def __init__(self, title, status_set, obj, event, *args, **kargs):

        self.parentObj = obj # 'Change' Button
        self.targetObj = self.parentObj.get_objectLink()
        self.currentSelection = self.targetObj[0]
        self.title = title[0]
        self.status_set = status_set
        self.isFiles = self.parentObj.get_valueLink()

        super(SelectWindow, self).__init__(self.title, elementary.ELM_WIN_BASIC)
        self.title_set(self.title)
        self.destroy = self.quit
        self.resize(480, 640)
        self.autodel_set(1)
        self.show()

        self.filebuttons = []

        bg = elementary.Background(self)
        bg.show()

        box = elementary.Box(self)
        box.show()

        self.lab = elementary.Label(self)
        self.lab.show()

        fr = elementary.Frame(self)
        fr.label_set(_("Select Item"))
        fr.size_hint_align_set(-1.0, 0.0)
        fr.content_set(self.lab)
        fr.show()

        self.box1 = elementary.Box(self)
        self.box1.size_hint_weight_set(1.0, 0.0)
        self.box1.show()

        self.scr = elementary.Scroller(self)
        self.scr.bounce_set(0,0)
        self.scr.size_hint_weight_set(1.0, 1.0)
        self.scr.size_hint_align_set(-1.0, -1.0)
        self.scr.show()

        self.scr.content_set(self.box1)

        btnBar = elementary.Box(self)
        btnBar.horizontal_set(True)
        btnBar.size_hint_weight_set(1.0, 0.0)
        btnBar.size_hint_align_set(-1.0, -1.0)
        btnBar.show()

        updir = elementary.Button(self)
        updir.label_set(_("Up"))
        updir.size_hint_weight_set(1.0, 0.0)
        updir.size_hint_align_set(-1.0, -1.0)
        updir.clicked = self.changeDirUp
        updir.show()

        exitbtn = elementary.Button(self)
        exitbtn.label_set(_("Done"))
        exitbtn.size_hint_weight_set(1.0, 0.0)
        exitbtn.size_hint_align_set(-1.0, -1.0)
        exitbtn.clicked = self.quit
        exitbtn.show()

        btnBar.pack_end(updir)
        btnBar.pack_end(exitbtn)

        box.pack_start(fr)
        box.pack_end(self.scr)
        box.pack_end(btnBar)

        self.resize_object_add(bg)
        self.resize_object_add(box)
        self.show()

        self.update()

    def update(self):
        # clear status message on new selection
        self.status_set(" ")

        cs = self.currentSelection
        self.targetObj[0] = cs

        self.parentObj.set_filename(cs)
        self.lab.label_set(self.title +":<br>"+ self.parentObj.get_trunc_path(40))

        if os.path.isdir(cs):
            dirs = sorted([ cs+f+"/" for f in os.listdir(cs) if os.path.isdir(cs+f) ])
            if self.isFiles:
                dirs  = sorted([ cs+f+"/" for f in os.listdir(cs) if os.path.isdir(cs+f)])
                files = sorted([ cs+f for f in os.listdir(cs) if os.path.isfile(cs+f) and str(cs+f)[-4:] == '.tar'], reverse=True)
                dirs.extend(files)

            for f in self.filebuttons:
                f.delete()
            del self.filebuttons

            self.filebuttons = []

            for d in dirs:
                self.filebuttons.append(FileButton(self))
                self.filebuttons[-1].set_filename(d)
                self.filebuttons[-1].clicked = self.changeDir
                self.filebuttons[-1].size_hint_align_set(-1.0, 0.0)
                self.filebuttons[-1].show()

                self.box1.pack_end(self.filebuttons[-1])


    def changeDir(self, obj, event, *args, **kargs):
        """
        Callback function to change the current directory
        """
        self.currentSelection = str(obj.get_filename())

        self.update()

    def changeDirUp(self, obj, event, *args, **kargs):
        """
        Callback function to change the current directory
        """
        a = self.currentSelection.split('/')
        del a[-2]
        a[-1] = ''
        self.currentSelection = "/".join(a)

        self.update()

    def quit(self, obj, event, *args, **kargs):
        """
        Callback function to destroy the Selection window
        """
        self.delete()


class OptionsBox(elementary.Box):
    def __init__(self, window, dir):
        self.window = window
        self.dir = dir

        super(OptionsBox, self).__init__(self.window)
        self.size_hint_weight_set(1.0, 0.0)
        self.size_hint_align_set(-1.0, 0.0)
        self.show()

        # Options Frame
        frame = elementary.Frame(self.window)
        frame.label_set("Options")
        frame.size_hint_weight_set(1.0, 0.0)
        frame.size_hint_align_set(-1.0, 0.0)
        frame.show()

        # Options H Box
        vbox = elementary.Box(self.window)
        vbox.size_hint_weight_set(1.0, 0.0)
        vbox.size_hint_align_set(-1.0, 0.0)
        vbox.horizontal_set(True)
        vbox.show()

        # Options ClearAll Archives Button
        clearAll = FileButton(self.window)
        clearAll.size_hint_weight_set(1.0, 0.0)
        clearAll.size_hint_align_set(-1.0, 0.0)
        clearAll.set_filename(self.dir[0])
        clearAll.label_set(_("Delete Archives"))
        clearAll.clicked = self.clearAllArchives
        clearAll.size_hint_align_set(-1.0, 0.0)
        clearAll.show()

        vbox.pack_end(clearAll)

        frame.content_set(vbox)

        self.pack_end(frame)

    def clearAllArchives(self, obj, event, *args, **kargs):
        deleteCmd = "rm " + self.dir[0] + "home_archive-*.tar"
        os.system(deleteCmd)

class ArchiveBox(elementary.Box):
    def __init__(self, window):
        self.window = window
        self.target = None
        self.title = [""]



        super(ArchiveBox, self).__init__(self.window)
        self.size_hint_weight_set(1.0, 0.0)
        self.size_hint_align_set(-1.0, 0.0)
        self.show()

        # Archive V Box
        vbox = elementary.Box(self.window)
        vbox.size_hint_weight_set(1.0, 0.0)
        vbox.size_hint_align_set(-1.0, 0.0)
        vbox.horizontal_set(False)
        vbox.show()

        # Archive H Box
        hbox = elementary.Box(self.window)
        hbox.size_hint_weight_set(1.0, 0.0)
        hbox.size_hint_align_set(-1.0, 0.0)
        hbox.horizontal_set(True)
        hbox.show()

        # Archive Change Button
        self.change = FileButton(self.window)
        self.change.size_hint_weight_set(1.0, 0.0)
        self.change.size_hint_align_set(-1.0, 0.0)
        self.change.clicked = partial(SelectWindow, self.title, self.status_set)
        self.change.show()

        # Archive Do Button
        self.do = elementary.Button(self.window)
        self.do.label_set(_(" Go "))
        self.do.size_hint_align_set(-1.0, 0.0)
        self.do.clicked = self.runDoCallback
        self.do.show()

        # Pack Archive H Box
        hbox.pack_end(self.change)
        hbox.pack_end(self.do)

        # Archive Status
        self.status = elementary.Label(self.window)
        self.status.size_hint_weight_set(1.0, 0.0)
        self.status.size_hint_align_set(-1.0, 0.0)
        self.status.label_set(" ")
        self.status.show()

        # Pack Archive V Box
        vbox.pack_end(hbox)
        vbox.pack_end(self.status)

        # Pack the top level box
        self.pack_end(vbox)

    def runDoCallback(self, obj, event, *args, **kargs):
        self.callback()

    def status_set(self, status):
        self.status.label_set(status)

    def target_set( self, targetObj ):
        self.change.set_filename(targetObj[0])
        self.change.set_objectLink(targetObj)

    def title_set( self, title ):
        self.title[0] = title[0]

    def callback_set( self, cb ):
        self.callback = cb

    def files_set( self, filesBool ):
        self.change.set_valueLink( filesBool )


class Backup(module.AbstractModule):
    name = _("Userspace Backup")

    def expand( self, path ):
        return glob( os.path.expanduser( os.path.expandvars( path ) ) )

    def file_filter(self, f):
        reCommentBlank = re.compile(r'^\s*(#|$)')
        output = []

        with open( f, 'r' ) as file:
            for line in file:
                line = line.strip()
                if not re.match( reCommentBlank, line ):
                    output.append(line)
        # print 'From',f,output
        return output

    def set_config(self):
        """
        Get config data from config files
        """

        # defaults
        #   yes, self.activeFile is a unitary list.
        #   This is to allow for interclass communication.
        #   Anyone know a better way?

        self.blacklist      = []                    # list of blacklist files/dirs
        self.whitelist      = []                    # files to include
        self.date_format    = DATE_FORMAT
        self.archiveFile    = ARCHIVE_FILE
        self.activeFile     = [ ARCHIVE_DIR ]       # double duty as archive dir and restore file
        self.userdir        = os.environ[ 'HOME' ]
        self.mode           = True                  # True:False == Archive:Restore


        # Read whitelist
        whitelist = self.file_filter(CONFIG_LIST['whitelist'])
        for line in whitelist:
            self.add_to_list( line, self.whitelist )

        # Read blacklists
        blacklist = self.file_filter(CONFIG_LIST['blacklist'])
        for line in blacklist:
            self.add_to_list( line, self.blacklist )

        # Read config
        conf = self.file_filter(CONFIG_LIST['conf'])
        for c in conf:
            conf_item, conf_value   = c.split(':')

            conf_item   = conf_item.strip()
            conf_value  = conf_value.strip()

            if conf_item == 'DATE':
                self.date_format = conf_value

            elif conf_item == 'ARCHIVE_FILE':
                self.archiveFile = conf_value

            elif conf_item == 'WHITELISTS':
                for files in conf_value.split(','):
                    for file in self.expand(files):
                        if os.path.isfile(file):
                            for line in self.file_filter(file):
                                self.add_to_list( line, self.whitelist )
                # print 'Whitelist',self.whitelist

            elif conf_item == 'BLACKLISTS':
                for files in conf_value.split(','):
                    for file in self.expand(files):
                        if os.path.isfile(file):
                            for line in self.file_filter(file):
                                self.add_to_list( line, self.blacklist )
                # print 'Blacklist',self.blacklist

        # whitelist minus blacklists
        self.whitelist = [ path for path in self.whitelist if not path in self.blacklist]

        print "Config Loaded, Black/Whitelists read"

    def add_to_list( self, input , output ):
        input = input.strip()
        for e in self.expand(input):
            if os.path.isfile( e ) and not e in output:
                output.append( e )
            elif os.path.islink( e ) and not e in output:
                output.append( e )
            elif os.path.isdir( e ):
                for files in os.listdir( e ):
                    self.add_to_list( e.rstrip( '/' ) + '/' + files, output )

    def archive(self):
        """
        1) Tar the contents of /home/${USER} to ${ARCHIVE}
        2) Store in ${ARCHIVE_DIR}
        """
        if os.path.isdir(self.activeFile[0]):
            t = time.strftime(self.date_format)
            outfile =  self.activeFile[0]+self.archiveFile.format(t)

            files = ' '.join( [ '"' + f + '"' for f in self.whitelist ] )

            cmd = 'tar -cf "' + outfile + '" ' + files
            self.run_command(cmd, "Archiving")
        else:
            self.status_set(_("Directory required."))

    def restore(self):
        """
        1) untar the contents of ${ARCHIVE_DIR}/${ARCHIVE} to /home/${USER}
        """
        if os.path.isfile(self.activeFile[0]):
            cmd = 'tar -xf "' + self.activeFile[0] + '"'  + " -C /"# + self.userdir + "/restoreTest" # testing target
            self.run_command(cmd, "Restoring")
        else:
            self.status_set(_("File required."))

    def run_command(self, cmd, status_string):
##        print cmd
        self.status_set(_(status_string+" In Progress."))
        c = os.popen(cmd)
        exitCode = c.close()
        if not exitCode:
            self.status_set(_(status_string+" Complete."))
        else:
            self.status_set(_(status_string+" Failed. "+os.WEXITSTATUS(exitCode)))

    def update(self):
        if self.mode:
            # Set to Archive mode
            self.archiveBox.target_set(self.activeFile)
            self.archiveBox.title_set([_("Archive Directory")])
            self.archiveBox.callback_set(self.archive)
            self.archiveBox.files_set(False)
        else:
            # Set to Restore mode
            self.archiveBox.target_set(self.activeFile)
            self.archiveBox.title_set([_("Restore File")])
            self.archiveBox.callback_set(self.restore)
            self.archiveBox.files_set(True)
        self.status_set(" ")

    def toggleChanged(self, obj, event, *args, **kargs):
        """
        Toggle the mode
        """
        self.mode = obj.state_get()
        self.update()

    def createView(self):

        # setup config
        self.set_config()

        # create the main box
        self.main = elementary.Box( self.window )
        self.main.size_hint_weight_set( 1.0, 1.0 )
        self.main.size_hint_align_set( -1.0, 0.0 )

        # create mode toggle
        self.toggle = elementary.Toggle( self.window )
        self.toggle.label_set( _( "Backup Mode" ) )
        self.toggle.states_labels_set( _( "Archive" ), _( "Restore" ) )
        self.toggle.changed = self.toggleChanged
        self.toggle.size_hint_align_set( -1.0, 0.0 )
        self.toggle.size_hint_weight_set( 1.0, 0.0 )
        self.toggle.state_set( self.mode )
        self.toggle.show()

        # create the box
        self.archiveBox = ArchiveBox( self.window )
        self.status_set = self.archiveBox.status_set
        ## self.optionsBox = OptionsBox(self.window, self.archiveDir) # This line has some concerns

        # pack the boxes
        self.main.pack_end(self.toggle)
        self.main.pack_end(self.archiveBox)
        ## self.main.pack_end(self.optionsBox) # This line has some concerns

        # update display
        self.update()

        self.main.show()

        return self.main
