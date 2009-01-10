#!/usr/bin/env python

#FIXME: hiciu: dokoncze to jutro

import elementary
#import evas
import dbus
import e_dbus
import os.path as path

def debug(txt):
    print "DEBUG: %s..." % txt
    
class Button2(elementary.Button):
    modules = []
    def load_icon(self, icon_name):
        for loc in ["data/%s.png", "/usr/share/pixmaps/%s.png"]:
            if path.exists(loc % icon_name):
                ic = elementary.Icon(self)
                ic.file_set("data/%s.png" % icon_name)
                ic.scale_set(0, 0)
                self.icon_set(ic)
                ic.show()
                return
        debug("no such icon: %s" % icon_name);

class MainWindow(elementary.Window):
    def __init__(self):
        debug("MainWindow init")
        elementary.Window.__init__(self, "Settings", elementary.ELM_WIN_BASIC)
        self.destroy = self.on_destroy
        self.categories = {}
        self.resize(480, 600)
        self.mk_gui()               #add basic things like quit button, background etc..
        self.dbus_connect()         #connect with dbus
        self.preload_modules()      #preload modules - just import them and make category buttons

    def mk_gui(self):
        debug("creating gui")
        #elementary background
        self.__bg = elementary.Background(self)
        self.__bg.size_hint_weight_set(1.0, 1.0)
        self.resize_object_add(self.__bg)
        self.__bg.show()

        #main container
        self.__box = elementary.Box(self)
        self.__box.size_hint_weight_set(1.0, 1.0)
        self.resize_object_add(self.__box)
        self.__box.show()

        #main scroller ;)
        self.__scroller = elementary.Scroller(self)
        self.__scroller.size_hint_weight_set(1.0, 1.0)
        self.__scroller.size_hint_align_set(-1.0, -1.0)
        self.__box.pack_start(self.__scroller)
        self.__scroller.show()
        
        #aa.. container in scroller in container!
        self.__main = elementary.Box(self)
        self.__main.size_hint_weight_set(1.0, 1.0)
        self.__scroller.content_set(self.__main)
        self.__main.show()

        #Quit button
        self.__quit = elementary.Button(self)
        self.__quit.clicked = self.on_destroy
        self.__quit.label_set("Quit")
        self.__quit.size_hint_align_set(-1.0, 0.0)
        self.__box.pack_end(self.__quit)
        self.__quit.show()
        
    def dbus_connect(self):
        debug("connecting with dbus")
        #as in exposure.py:
        mainloop = e_dbus.DBusEcoreMainLoop()
        #self.dbus_session = dbus.SessionBus(mainloop=self.mainloop) - we don't need atm
        self.dbus_system = dbus.SystemBus(mainloop=mainloop)
        
    def preload_modules(self):
        debug("preloading modules")
        from shr_settings_modules import shr_gsm, shr_device_timeouts,shr_pm, shr_bt, shr_wifi, shr_gprs, shr_usb, shr_clock, shr_profile, shr_services, shr_misc, shr_test
        modules = [ shr_device_timeouts.Timeouts,
                shr_gsm.Gsm,
                shr_pm.Pm,
                shr_bt.Bt,
                shr_wifi.Wifi,
                shr_gprs.Gprs,
                shr_usb.Usb,
                shr_clock.Clock,
                shr_profile.Profile,
                shr_services.Services,
                shr_misc.Misc,
                shr_test.Test
              ]
        for mod in modules:
            self.preload(mod)
    
    def preload(self, module):
        debug("preloading %s" % module)
        mod = module(self, self.dbus_system)
        if mod.isEnabled():
            if not mod.section in self.categories:
                #this is first module in this category / section...
                self.categories[mod.section] = Button2(self)
                self.categories[mod.section].modules = []
                self.categories[mod.section].size_hint_align_set(-1.0, 0.0)
                self.categories[mod.section].label_set(mod.section)
                self.categories[mod.section].load_icon(mod.section)
                self.__main.pack_end(self.categories[mod.section])
                self.categories[mod.section].show()
            self.categories[mod.section].modules.append(mod)

    def on_destroy(self, obj, event, *args, **kargs):
        debug("self.on_destroy()! kabum!")
        elementary.exit()

if __name__ == "__main__":
    debug("app start")
    elementary.init()
    window = MainWindow()
    window.show()
    elementary.run()
    elementary.shutdown()
