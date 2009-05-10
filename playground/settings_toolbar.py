import elementary, ecore
import dbus, e_dbus
import sys, os
from functools import partial


# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x

IMAGE_DIR='/usr/share/pixmaps/'

MODULES = [ [_("Power"),        "icon_power.png",        [ 'shr_battery.Battery', 'shr_display.Display', 'shr_pm.Pm' , 'shr_device_timeouts.Timeouts' ] ],
            [_("Phone"),        "icon_phone.png",        [ 'shr_gsm.Gsm', 'shr_call.Call', 'shr_sim.Sim' ] ],
            [_("Profiles"),     "icon_profiles.png",     [ 'shr_profile.Profile', 'shr_currentprofile.CurrentProfile' ] ],
            [_("Connectivity"), "icon_connectivity.png", [ 'shr_wifi.Wifi', 'shr_gprs.Gprs', 'shr_usb.Usb', 'shr_bt.Bt' ] ],
            [_("GPS"),          "icon_gps.png",          [ 'shr_gps.Gps' ] ],
            [_("Date/time"),    "icon_datetime.png",     [ 'shr_clock.Clock' ] ],
            [_("Services"),     "icon_services.png",     [ 'shr_services.Services' ] ],
            [_("Others"),       "icon_others.png",       [ 'shr_pim.Pim', 'shr_test.Test' ] ]
    ]


class MessageFrame(elementary.Frame):
    """
    """
    def __init__(self, window, string):
        """
        """
        self.win = window

        super(MessageFrame, self).__init__(self.win)

        self.label = elementary.Label(self.win)
        self.label.label_set(string)
        self.label.show()

        self.size_hint_weight_set(0.0, 0.0)
        self.size_hint_align_set(0.5, 0.5)
        self.content_set(self.label)
        self.show()

    def label_set(self,string):
        """
        """
        self.label.label_set(string)

class ModuleBox(elementary.Box):
    """
    """
    def __init__(self, window, dbus, id):
        """
        """

        self.win = window
        self.dbus = dbus
        self.id = id

        self.module = MODULES[self.id]
        self.isLoaded = False

        super(ModuleBox, self).__init__(self.win)

        self.scroller = elementary.Scroller(self.win)
        self.scroller.size_hint_weight_set(1.0, 1.0)
        self.scroller.size_hint_align_set(-1.0, -1.0)
        self.scroller.content_min_limit(480, 640)
        self.scroller.show()

        self.pack_end(self.scroller)

        self.show()

    def loadModule(self):
        """
        """
        print "loading %s" % self.module[0]

        moduleContents = elementary.Box(self.win)
        moduleContents.size_hint_align_set(-1.0, 0.0)
        moduleContents.size_hint_weight_set(1.0, 1.0)
        for modname in self.module[2]:
            try:
                # modname: 'shr_gsm.GSM'. Import "shr_settings_modules.shr_gsm"
                # dynamically and instantiate class "GSM"
                (submodname, classname) = modname.split('.',1)
                module   = __import__('shr_settings_modules.' + submodname,
                                      globals(), locals(), classname)
                ModClass = module.__getattribute__(classname)
                modObject = ModClass(self.win, self.dbus)

                if modObject.isEnabled():
                    cont = modObject.createView()

                    frame = elementary.Frame(self.win)

                    frame.label_set(_("%s settings") % modObject.getName())
                    frame.size_hint_align_set(-1.0, 0.0)
                    frame.size_hint_weight_set(1.0, 1.0)
                    frame.show()

                    moduleContents.pack_end(frame)

                    if cont != None:
                        frame.content_set(cont)
                        cont.show()
                    else:
                        print " error! module %s method createView() returns nothing!" % modObject
                self.isLoaded = True
            except:
                print "module %s can't be loaded!" % modname
        self.scroller.content_set(moduleContents)
        return None

class Settings(object):
    def __init__(self, startId = 0):
        """
        """

        # Start dbus
        mainloop = e_dbus.DBusEcoreMainLoop()
        self.dbus_system = dbus.SystemBus(mainloop=mainloop)

        # Create window
        self.win = elementary.Window("Testing", elementary.ELM_WIN_BASIC)
        self.win.title_set("Testing")
        self.win.destroy = (self.quit, None)

        # Background Widget
        bg = elementary.Background(self.win)
        self.win.resize_object_add(bg)
        bg.size_hint_weight_set(1, 1)
        bg.show()

        # Box widget
        box = elementary.Box(self.win)
        self.win.resize_object_add(box)
        box.size_hint_weight_set(1, 1)
        box.show()

        # Toolbar widget
        tb = elementary.Toolbar(self.win)
        tb.size_hint_weight_set(0, 0)
        tb.size_hint_align_set(-1.0, -1.0)

        tbItems = []
        for i,m in enumerate(MODULES):
            ic = elementary.Icon(self.win)
            ic.file_set(IMAGE_DIR+m[1])
            tbItems.append(tb.item_add(ic, m[0], partial(self.click, id=i)))

        box.pack_end(tb)
        tb.show()

        # Pager widget
        self.pager = elementary.Pager(self.win)
        self.pager.size_hint_weight_set(1.0, 1.0)
        self.pager.size_hint_align_set(-1.0, -1.0)
        box.pack_end(self.pager)
        self.pager.show()

        self.pages = []
        for id,m in enumerate(MODULES):
            self.pages.append(ModuleBox(self.win, self.dbus_system, id))
            self.pager.content_push(self.pages[id])

        # set pager to first page, or start page if launched as such
        tbItems[startId].select()

        self.win.resize(480, 640)
        self.win.show()


    def click(self, obj, event, id):
##        print "Clicked: "+MODULES[id][0]
        if not self.pages[id].isLoaded:
            self.pages[id].loadModule()
        self.pager.content_promote(self.pages[id])

    def init_dbus_idler(self):
        # dbus init if not done before:
        if self.dbus_system == None:
            mainloop = e_dbus.DBusEcoreMainLoop()
            #self.dbus_session = dbus.SessionBus(mainloop=self.mainloop) - we don't need atm
            self.dbus_system = dbus.SystemBus(mainloop=mainloop)
            return False  #don't call idler again

    def quit(self, obj, event, data):
        elementary.exit()


#### Run Settings()


if __name__ == "__main__":

    elementary.init()
    if len(sys.argv[1:])>0:
        if sys.argv[1] in ("-h", "--help"):
                print "SHR Settings - Toolbar Edition"
                print "Settings for SHR based Openmoko phone."
                print "--------------------------------------"
                print "Call it without any argument to open"
                print "standard menu."
                print "Call it with modules names, to open"
                print "directly to typed modules in one window."
                print ""
                print "Available modules:"
                for m in MODULES:
                    print "\t{0}".format(m[0])
                print ""
                print "Eg:"
                print "\t{0} {1}".format(sys.argv[0], MODULES[0][0])
                print "--------------------------------------"
                print "http://shr-project.org/"
                exit(0)
        else:
            try:
                id = [ m[0] for m in MODULES ].index(sys.argv[1])
            except ValueError:
                id = 0 # no match, start at begining
            Settings(id)
    else:
        Settings()
    elementary.run()
    elementary.shutdown()

