import module, elementary, os

from functools import partial

# Locale support
import gettext

"""
TODO: Make Home directory backup/restore module

NOTES:
  - Archive to a .tar file on the uSD card
  - Include all files in /home/${USER} except those listed in [DIRECTORY_BLACKLIST]
  - On restore (e.g. after a reflash) untar archived files, overriding the
    current /home/${USER} (Should we backup /home/${USER} to a temp archive
    before overwriting?


"""

# Directories in /home/${USER} that are to be ignored during archive
DIRECTORY_BLACKLIST = ['.e']

# Defaults
ARCHIVE_DIR  = "/media/card/"
ARCHIVE_FILE = "archive-{0}.tar" # {0} to be the date, filled in later

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class FileButton(elementary.Button):
    def set_filename( self, filename ):
        self.filename = filename
        self.label_set(filename)

    def get_filename( self ):
        return self.filename


class SelectWindow(elementary.Window):
    def __init__(self, title, dir, lab, isFiles, obj, event, *args, **kargs):

        self.parentObj = dir
        self.currentSelection = self.parentObj[0]
        self.parentLabel = lab
        self.title = title
        self.isFiles = isFiles

        super(SelectWindow, self).__init__(title, elementary.ELM_WIN_BASIC)
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
        cs = self.currentSelection
        self.parentObj[0] = cs
        self.parentLabel.label_set(_("Current Selection is:")+"<br>"+cs)
        self.lab.label_set(_("Current Selection is:")+"<br>"+cs)

        if os.path.isdir(cs):
            if not self.isFiles:
                files = [ cs+f+"/" for f in os.listdir(cs) if os.path.isdir(cs+f) ]
            else:
                files = [ cs+f+"/" for f in os.listdir(cs) if os.path.isdir(cs+f)]
                files.extend([cs+f for f in os.listdir(cs) if os.path.isfile(cs+f) ])

            for f in self.filebuttons:
                f.delete()
            del self.filebuttons

            self.filebuttons = []

            for filename in files:
                self.filebuttons.append(FileButton(self))
                self.filebuttons[-1].set_filename(filename)
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


class ArchiveBox(elementary.Box):
    def __init__(self, window, dir, title, callback, isFiles = False):
        self.window = window
        self.dir = dir
        self.cb = callback
        self.title = title

        super(ArchiveBox, self).__init__(self.window)
        self.size_hint_weight_set(1.0, 0.0)
        self.size_hint_align_set(-1.0, 0.0)
        self.show()

        # Archive Label
        label = elementary.Label(self.window)
        label.size_hint_weight_set(1.0, 0.0)
        label.size_hint_align_set(-1.0, 0.0)
        label.label_set(self.title+":<br>"+self.dir[0])
        label.show()

        # Archive H Box
        box = elementary.Box(self.window)
        box.size_hint_weight_set(1.0, 0.0)
        box.size_hint_align_set(-1.0, 0.0)
        box.horizontal_set(True)
        box.show()

        # Archive Change Button
        change = FileButton(self.window)
        change.size_hint_weight_set(1.0, 0.0)
        change.size_hint_align_set(-1.0, 0.0)
        change.set_filename(self.dir[0])
        change.label_set(_("Change"))
        change.clicked = partial(SelectWindow, self.title, self.dir, label, isFiles)
        change.size_hint_align_set(-1.0, 0.0)
        change.show()

        # Archive Do Button
        do = elementary.Button(self.window)
        do.label_set(_(" Go "))
        do.clicked = self.cb
        do.size_hint_align_set(-1.0, 0.0)
        do.show()

        box.pack_end(change)
        box.pack_end(do)

        self.pack_end(label)
        self.pack_end(box)


class HomeDir(module.AbstractModule):
    name = _("Home Directory")

    def archive(self, obj, event, *args, **kargs):
        """
        1) Tar the contents of /home/${USER} to ${ARCHIVE}
        2) Store in ${ARCHIVE_DIR}
        """
        time = "Some_date_stamp"
        print self.archiveDir[0]+self.archiveFile[0].format(time)

    def restore(self, obj, event, *args, **kargs):
        """
        1) Clean out /home/${USER}, except for 'DIRECTORY_BLACKLIST'
        2) untar the contents of ${ARCHIVE_DIR}/${ARCHIVE} to /home/${USER}
        """
        print self.restoreFile[0]

    def createView(self):

        # defaults
        #   yes, they are unitary lists.
        #   This is to allow for interclass communication.
        #   Anyone know a better way?
        self.archiveDir  = [ARCHIVE_DIR]
        self.archiveFile = [ARCHIVE_FILE]
        self.restoreFile = [ARCHIVE_DIR]
        self.userdir = os.environ['HOME']

        # create the box
        self.main = elementary.Box(self.window)
        self.main.size_hint_weight_set(1.0, 1.0)
        self.main.size_hint_align_set(-1.0, 0.0)

        archiveBox = ArchiveBox(self.window, self.archiveDir, "Archive Directory", self.archive)
        restoreBox = ArchiveBox(self.window, self.restoreFile, "Restore File", self.restore, True)

        self.main.pack_end(archiveBox)
        self.main.pack_end(restoreBox)

        self.main.show()

        return self.main
