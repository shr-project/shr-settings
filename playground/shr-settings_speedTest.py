#!/usr/bin/env python

import time
sTime = time.time()
def D(s):
	print "[shr-settings]["+str(time.time()-sTime)+"]"+str(s)

import elementary, os
D("after import elementary")
import edje
D("after import edje")
import evas
D("after import evas")
import dbus
D("after import dbus")
import e_dbus
D("after import e_dbus")



class Button2(elementary.Button):
    def set_modules(self, modules):
        self.modules = modules
    def get_modules(self):
        return self.modules

D("def Button2")


class ModulesWindow:
    def makeGui(self,  modulesList, bus):
        

        D("ModulesWindow makeGui")
        elementary.init()
        D("ModulesWindow makeGui elementary.init")
        from shr_settings_modules import shr_gsm, shr_device_timeouts,shr_pm, shr_bt, shr_wifi, shr_gprs, shr_usb, shr_clock, shr_profile, shr_services, shr_misc, shr_test
        D("ModulesWindow makeGui from shr_settings_modules")

        self.win2 = elementary.Window("settingsMods", elementary.ELM_WIN_BASIC)
        self.win2.title_set(modulesList[0])
        self.win2.destroy = self.destroy2
        

        self.bg2 = elementary.Background(self.win2)
        self.win2.resize_object_add(self.bg2)
        self.bg2.size_hint_weight_set(1.0, 1.0)
        self.bg2.show()


        box02 = elementary.Box(self.win2)
        box02.size_hint_weight_set(1.0, 1.0)
        self.win2.resize_object_add(box02)
        box02.show()



    #    toolbar = elementary.Toolbar(win)
    #    box0.pack_start(toolbar)
    #    toolbar.show()

        sc2 = elementary.Scroller(self.win2)
        sc2.size_hint_weight_set(1.0, 1.0)
        sc2.size_hint_align_set(-1.0, -1.0)
        box02.pack_end(sc2)
        sc2.show()

        quitbt2 = elementary.Button(self.win2)
        quitbt2.clicked = self.destroy2
        quitbt2.label_set("Quit")
        quitbt2.size_hint_align_set(-1.0, 0.0)
        quitbt2.show()
        box02.pack_end(quitbt2)


        box12 = elementary.Box(self.win2)
        box12.size_hint_weight_set(1.0, -1.0)
        sc2.content_set(box12)
        box12.show()

        D("ModulesWindow makeGui gui")

        D("ModulesWindow makeGui gui mod for")
        self.modList = []
        for mod in modulesList[2]:
        
            print "loading %s" % mod
            try:
                mod2 = mod(self.win2, bus)
                self.modList.append(mod2)

                if mod2.isEnabled():
                    cont = mod2.createView()

                    frame = elementary.Frame(self.win2)

                    frame.label_set(mod2.getName()+" settings")
                    box12.pack_end(frame)
                    frame.size_hint_align_set(-1.0, 0.0)
                    frame.show()

                    if cont != None:
                        frame.content_set(cont)
                        cont.show()
                    else:
                        print " error! module %s method createView() return's nothing!" % mod2
            except:
                print "module %s can't be loaded!" % mod
		D("ModulesWindow makeGui gui mod for done")

        self.win2.show()

    def destroy2(self,obj, event, *args, **kargs):
        self.win2.hide()
        for m in self.modList:
            try:
                m.stopUpdate()
            except:
                pass
        




class MainWindow:

    def destroy(self, obj, event, *args, **kargs):
        print "DEBUG: window destroy callback called! kabum!"
        elementary.exit()

    def displayModulesWin(self, obj,event):
        #odulesWindow:
        #def makeGui(self, dbus_system, modules):
        print "displayModulesWin 1"
        print "displayModulesWin 2"
        self.m.makeGui(  obj.get_modules(), self.dbus_system )
        print "displayModulesWin 3"

    def __init__(self):
        D("MainWindow __init__")
        elementary.init()
        D("MainWindow __init__ elementary.init")
        self.win = elementary.Window("settings", elementary.ELM_WIN_BASIC)
        self.win.title_set("Settings")
        self.win.destroy = self.destroy


        D("MainWindow __init__ mainloop e_dbus")
        #dbus init:
        mainloop = e_dbus.DBusEcoreMainLoop()
        #dbus_session = dbus.SessionBus(mainloop=self.mainloop) - we don't need atm
        self.dbus_system = dbus.SystemBus(mainloop=mainloop)
        D("MainWindow __init__ dbus present")

        self.m = ModulesWindow()

        self.bg = elementary.Background(self.win)
        self.win.resize_object_add(self.bg)
        self.bg.size_hint_weight_set(1.0, 1.0)
        self.bg.show()

        box0 = elementary.Box(self.win)
        box0.size_hint_weight_set(1.0, 1.0)
        self.win.resize_object_add(box0)
        box0.show()



    #    toolbar = elementary.Toolbar(win)
    #    box0.pack_start(toolbar)
    #    toolbar.show()

        sc = elementary.Scroller(self.win)
        sc.size_hint_weight_set(1.0, 1.0)
        sc.size_hint_align_set(-1.0, -1.0)
        box0.pack_end(sc)
        sc.show()

        quitbt = elementary.Button(self.win)
        quitbt.clicked = self.destroy
        quitbt.label_set("Quit")
        quitbt.size_hint_align_set(-1.0, 0.0)
        quitbt.show()
        box0.pack_end(quitbt)

        box1 = elementary.Box(self.win)
        box1.size_hint_weight_set(1.0, -1.0)
        sc.content_set(box1)
        box1.show()

        #loading modules
        D("MainWindow __init__ gui")
        from shr_settings_modules import shr_gsm,shr_sim, shr_device_timeouts,shr_pm, shr_bt, shr_wifi, shr_gprs, shr_usb, shr_clock, shr_profile, shr_services, shr_misc, shr_test
        D("MainWindow __init__ after from import")

        dirs = [    ["GSM","ico_gsm_32_32.png",                        [ shr_gsm.Gsm, shr_sim.Sim ] ],
                    ["Bluetooth","ico_bt_32_32.png",                   [ shr_bt.Bt ] ],
                    ["Internet","ico_internet_32_32.png",              [ shr_wifi.Wifi, shr_gprs.Gprs ] ],
                    ["Profiles","ico_profile_32_32.png",               [ shr_profile.Profile ] ],
                    ["Clock","ico_timeset_32_32.png",                  [ shr_clock.Clock ] ],
                    ["Power management","ico_powermanager_32_32.png",  [ shr_pm.Pm , shr_device_timeouts.Timeouts ] ],
                    ["USB","ico_usb_32_32.png",                        [ shr_usb.Usb ] ],
                    ["Services","ico_initd_32_32.png",                 [ shr_services.Services ] ],
                    ["Others", "ico_others_32_32.png",                 [ shr_misc.Misc, shr_test.Test ] ]
            ]
            

        D("MainWindow __init__ before for")
        for d in dirs:
            bt = Button2(self.win)
            bt.set_modules( d )

            bt.clicked = self.displayModulesWin
            bt.size_hint_align_set(-1.0, 0.0)
            bt.label_set( str(d[0]) )
            bt.show()


            try:
                f = open("data/icons/"+str(d[1]), "r")
                ic = elementary.Icon(self.win)
                ic.file_set("data/"+str(d[1]) )
                ic.scale_set(0, 0)
                bt.icon_set(ic)
                ic.show()

            except:
                try:
                    f = open("/usr/share/pixmaps/"+str(d[1]), "r")
                    ic = elementary.Icon(self.win)
                    ic.file_set("/usr/share/pixmaps/"+str(d[1]) )
                    ic.scale_set(0, 0)
                    bt.icon_set(ic)
                    ic.show()
                except:
                    bt.label_set( str(d[0]) )

            box1.pack_end(bt)


        D("MainWindow __init__ after for")

        #for mod in modules:
        #    print "loading %s" % mod
        #    load_module(mod, win, dbus_system)

        #end of loading modules



        self.win.show()
        

if __name__ == "__main__":

    D("MainWindow start")
    MainWindow()
    D("MainWindow end")
    elementary.run()
    elementary.shutdown()

    
