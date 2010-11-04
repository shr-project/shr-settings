import elementary
import module
import os


# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x



class EntryBox(elementary.Box):
    """
    Class for Interface info entry
    """

    def entry_get(self):
        return self.Entry.entry_get()

    def entry_set(self, value):
        return self.Entry.entry_set(value)

    def __init__(self, win, label, value):
        """
        """

        super(EntryBox, self).__init__(win)
        self.horizontal_set(True)

        self.size_hint_weight_set(1.0, 0.0)
        self.size_hint_align_set(-1.0, 0.0)

        self.window = win
        self.label  = label
        self.value  = value

        self.Label = elementary.Label(self.window)
        self.Label.size_hint_align_set(-1.0, 0.0)
        self.Label.label_set(self.label)
        self.Label.show()

        self.Entry = elementary.Entry(self.window)
        self.Entry.size_hint_align_set(-1.0, 0.0)
        self.Entry.size_hint_weight_set(1.0, 0.0)
        self.Entry.single_line_set(True)
        self.Entry.entry_set(self.value)
        self.Entry.show()

        self.EntryFrame = elementary.Frame(self.window)
        self.EntryFrame.size_hint_align_set(-1.0, 0.0)
        self.EntryFrame.size_hint_weight_set(1.0, 0.0)
        self.EntryFrame.style_set("outdent_top")
        self.EntryFrame.content_set(self.Entry)
        self.EntryFrame.show()

        self.pack_start(self.Label)
        self.pack_end(self.EntryFrame)
        self.show()


class NTP(module.AbstractModule):
    name = _("NTP settings")
    ntpconf = "/etc/ntp.conf"


    def GetNTPServer(self):
        server="unknown"
        try:
            ntpfile = open(self.ntpconf, "r+")
            while True:
                line = ntpfile.readline()
                if line=="": #EOF
                    break

                li = line.strip('\t\n').split(' ')
                if li[0]=="server":
                    server=li[1]
                    break
            ntpfile.close()
        except:
            print "could not open "+self.ntpconf+" for reading"
        return server

    def SetNTPServer(self, server):
        if self.GetNTPServer()=="unknown":
            os.system("echo \"server "+server+"\" >> "+self.ntpconf)
        else:
            os.system("sed \"s#server .*#server "+server+"#\" -i "+self.ntpconf)


    def btClicked(self, obj, *args, **kwargs):
        self.SetNTPServer(self.NTPserver.entry_get())
        os.system("ntpclient -s -h "+self.NTPserver.entry_get()+" && hwclock -w")

    def createButton(self):
        self.bt = elementary.Button(self.window)
        self.bt.label_set(_("Sync Time"))
        self.bt.size_hint_weight_set(-1.0, 0.0)
        self.bt.size_hint_align_set(-1.0, 0.0)
        self.main.pack_end(self.bt)
        self.bt.show()
        self.bt._callback_add('clicked', self.btClicked)

    def createView(self):
        self.main = elementary.Box(self.window)

        server=self.GetNTPServer()
        if server=="unknown":
            server="europe.pool.ntp.org"

        self.NTPserver = EntryBox(self.window, _("NTP Server: "), server)
        self.main.pack_end(self.NTPserver)
        self.createButton()
        return self.main
