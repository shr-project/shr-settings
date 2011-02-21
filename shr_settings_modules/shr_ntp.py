import elementary
import module
from helper import ElmEntryBox
import os


# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class NTP(module.AbstractModule):
    name = _("NTP settings")
    ntpconf = "/etc/ntp.conf"
    rcsconf = "/etc/default/rcS"

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
        utcmode=False
        try:
            rcsfile = open(self.rcsconf, "r")
            while True:
                line = rcsfile.readline()
                if line=="": #EOF
                    break

                li = line.strip('\t\n').split('=')
                if li[0]=="UTC":
                    if li[1]=="yes":
                        utcmode=True
                    break
            rcsfile.close()
        except:
            print "could not open "+self.ntpconf+" for reading"

        self.SetNTPServer(self.NTPserver.entry_get())
        #os.system("ntpclient -s -h "+self.NTPserver.entry_get()+" && hwclock -w")
        if utcmode==True:
            os.system("ntpd  -q -n -p "+self.NTPserver.entry_get()+" && hwclock -uw")
        else:
            os.system("ntpd  -q -n -p "+self.NTPserver.entry_get()+" && hwclock -w")

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

        self.NTPserver = ElmEntryBox(self.window, _("NTP Server: "), server)
        self.main.pack_end(self.NTPserver)
        self.createButton()
        return self.main
