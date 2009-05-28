import module, elementary, os

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


class DirectorySelectWindow(elementary.Window):
    def __init__(self, title, start_dir):
        self.parentObj = start_dir
        self.currentSelection = self.parentObj[0]

        super(DirectorySelectWindow, self).__init__(win, title, elementary.ELM_WIN_BASIC)
        self.title_set(title)
        self.autodel_set(1)

        bg = elementary.Background(self)
        bg.show()

        box = elementary.Box(self)
        box.show()

        self.lab = elementary.Label(self)
        self.lab.show()

        fr = elementary.Frame(self)
        fr.label_set(_("Select directory"))
        fr.size_hint_align_set(-1.0, 0.0)
        fr.content_set(self.lab)
        fr.show()

        self.scr = elementary.Scroller(self)
        self.scr.size_hint_weight_set(1.0, 1.0)
        self.scr.size_hint_align_set(-1.0, -1.0)
        self.scr.show()

        btnBar = elementary.Box(self)
        btnBar.size_hint_weight_set(1.0, 0.0)
        btnBar.size_hint_align_set(-1.0, -1.0)
        btnBar.show()

        opendir = elementary.Button(self)
        opendir.label_set(_("Open"))
        opendir.size_hint_weight_set(1.0, 0.0)
        opendir.size_hint_align_set(-1.0, -1.0)
        opendir.clicked = self.changeDir
        opendir.show()

        exitbtn = elementary.Button(self)
        exitbtn.label_set(_("Done"))
        exitbtn.size_hint_weight_set(1.0, 0.0)
        exitbtn.size_hint_align_set(-1.0, -1.0)
        exitbtn.clicked = self.destroy
        exitbtn.show()

        btnBar.pack_end(opendir)
        btnBar.pack_end(exitbtn)

        box.pack_start(fr)
        box.pack_end(scr)
        box.pack_end(btnBar)

        self.resize_object_add(bg)
        self.resize_object_add(box)
        self.show()

        self.update()

    def update(self):
        self.parentObj[0] = self.currentSelection
        self.lab.label_set(_("Current Selection is:")+"<br>"+self.currentSelection)

        self.box1 = elementary.Box(self)
        self.box1.size_hint_weight_set(1.0, 0.0)
        self.box1.show()

        files = [f for f in os.listdir(self.currentSelection) if os.path.isdir(self.currentSelection+f)]
        files.insert(0,self.currentSelection+"/..")

        for filename in files:
            filebtn = FileButton(self)
            filebtn.set_filename(filename)
            filebtn.clicked = self.changeDir
            filebtn.size_hint_align_set(-1.0, 0.0)
            filebtn.show()

            self.box1.pack_end(filebtn)

        self.scr.content_set(self.box1)

    def changeDir(self, obj, event, *args, **kargs):
        """
        Callback function to change the current directory
        """
        self.currentSelection = str(obj.get_filename())

        self.update()

    def destroy(self, obj, event, *args, **kargs):
        """
        Callback function to destroy the Selection window
        """
        self.hide()

class HomeDir(module.AbstractModule):
    name = _("Home Directory")

    def archive(self):
        """
        1) Tar the contents of /home/${USER} to ${ARCHIVE}
        2) Store in ${ARCHIVE_DIR}
        """
        pass

    def restore(self):
        """
        1) Clean out /home/${USER}, except for 'DIRECTORY_BLACKLIST'
        2) untar the contents of ${ARCHIVE_DIR}/${ARCHIVE} to /home/${USER}
        """
        pass

    def createView(self):

        # defaults
        #   yes, they are unitary lists.
        #   This is to allow for interclass communication.
        #   Anyone know a better way?
        self.archiveDir  = ["/media/card/archive/"]
        self.archiveFile = ["archive-{0}.tar"] # {0} to be the date, filled in later

        # create the box
        self.main = elementary.Box(self.window)
        self.main.size_hint_weight_set(1.0, 1.0)
        self.main.size_hint_align_set(-1.0, 0.0)

        # Archive Button
        archive = FileButton(self.window)
        archive.set_filename(self.archiveDir)
        archive.clicked = self.archive
        archive.size_hint_align_set(-1.0, 0.0)
        archive.show()

        # Restor Button
        archive = FileButton(self.window)
        archive.set_filename(self.archiveDir)
        archive.clicked = self.restore
        archive.size_hint_align_set(-1.0, 0.0)
        archive.show()

        self.main.pack_start(text)

        self.main.show()

        return self.main
