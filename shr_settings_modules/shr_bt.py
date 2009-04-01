import time
import module
import elementary, ecore
import os
import dbus

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)

class BtMstateContener:
    def __init__(self, busres, buspower):
        self.state = 0
        self.busres = busres
        self.buspower = buspower

    def setPower(self, b ):
        if b:
            self.busres.Enable()
        else:
            self.busres.Disable()
        self.buspower.SetPower(b)

    def getPower(self):
        return self.buspower.GetPower()

    def setVisibility(self, b):
        if b:
            print "hciconfig hci0 piscan"
            os.system("hciconfig hci0 up")
            os.system("hciconfig hci0 piscan")
        else:
            print "hciconfig hci0 pscan"
            os.system("hciconfig hci0 up")
            os.system("hciconfig hci0 pscan")

    def getVisibility(self):
        piscan = os.popen("hciconfig dev")
        self.visible = -1
        self.iscan = 0
        self.pscan = 0

        s = 1
        while s:
            line = piscan.readline()
            if not line:
                break
            else:
                s = line.split(" ")
                self.visible = 0
                for i in s:
                    if i=="ISCAN":
                        self.iscan = 1
                    elif i=="PSCAN":
                        self.pscan = 1

        if self.iscan==1:
            return 1
        return 0
        


class Bt(module.AbstractModule):
    name = _("Bluetooth")
    section = _("Connectivity")

    def BtmodGUIupdate(self):
        s = self.btmc.getPower()
        v = self.btmc.getVisibility()
        print "BT BtmodGUIupdate [info] power:"+str(s)+"; visibility:"+str(v)
        if s == 1:
            self.toggle1.show()
            if v:
                self.toggle1.state_set(1)
            else:
                self.toggle1.state_set(0)

            self.toggle0.state_set( 1 )

        else:
            self.toggle1.hide()
            self.toggle0.state_set( 0 )

        if self.guiUpdate:
            ecore.timer_add( 5.4, self.BtmodGUIupdate)

    def toggle0Click(self, obj, event, *args, **kargs):
#        if self.btmc.getPower():
	if self.btmc.getPower()==obj.state_get():
		return 0
	if obj.state_get()==0:
            print "Bt toggle0Click BT set OFF"
            self.btmc.setPower( 0 )
            #self.toggle1.hide()
        else:
            print "Bt toggle0Click BT set ON"
            self.btmc.setPower( 1 )
            #self.toggle1.show()
        self.BtmodGUIupdate()

        
        

    def toggle1Click(self, obj, event, *args, **kargs):
        print "BT toggle1Cleck set Visibility"
        if self.btmc.getVisibility()==obj.state_get():
            return 0
    #        s = self.btmc.getVisibility()
    #        print str(s)
    #        if s:
        if obj.state_get()==0:
            print "Turn off"
            self.btmc.setVisibility(0)
        else:
            print "Turn on"
            self.btmc.setVisibility(1)
        self.BtmodGUIupdate()

    def createView(self):
        box1 = elementary.Box(self.window)

        try:
            self.busres = getDbusObject (self.dbus, "org.freesmartphone.odeviced", "/org/freesmartphone/Device/PowerControl/Bluetooth", "org.freesmartphone.Resource" ) 
            self.buspower = getDbusObject (self.dbus, "org.freesmartphone.odeviced", "/org/freesmartphone/Device/PowerControl/Bluetooth", "org.freesmartphone.Device.PowerControl" )
        except:
            label =elementary.Label(self.window)
            label.label_set(_("can't connect to dbus"))
            label.size_hint_align_set(-1.0, 0.0)
            label.show()
            box1.pack_start(label)
            return box1

        self.guiUpdate = 1
        self.btmc = BtMstateContener(self.busres, self.buspower)
        vi = self.btmc.getVisibility()


        self.toggle0 = elementary.Toggle(self.window)
        self.toggle0.label_set(_("Bluetooth radio:"))
        self.toggle0.size_hint_align_set(-1.0, 0.0)
        self.toggle0.states_labels_set(_("On"),_("Off"))
        box1.pack_start(self.toggle0)
        self.toggle0.show()
        self.toggle0.changed = self.toggle0Click

        self.toggle1 = elementary.Toggle(self.window)
        self.toggle1.label_set(_("Visibility:"))
        self.toggle1.size_hint_align_set(-1.0, 0.0)
        self.toggle1.states_labels_set(_("On"),_("Off"))
        self.toggle1.state_set(vi)
        box1.pack_end(self.toggle1)
        self.toggle1.changed = self.toggle1Click

        self.BtmodGUIupdate()

        return box1

    def stopUpdate(self):
        print "BT destructor"
        self.guiUpdate = 0
