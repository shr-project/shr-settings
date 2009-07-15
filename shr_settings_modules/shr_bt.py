import module
import elementary
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
        self.dbusObjBT = busres
        self.dbusObjPower = buspower

    def setPower(self, b ):
        if b:
            self.dbusObjBT.Enable()
        else:
            self.dbusObjBT.Disable()
        self.dbusObjPower.SetPower(b)

    def getPower(self):
        return self.dbusObjPower.GetPower()

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
    name = _("Bluetooth settings")
    section = _("Connectivity")

    def error(self):
        label = elementary.Label(self.window)
        label.label_set(_("Couldn't connect to FSO"))
        self.main.pack_start(label)

    def update(self):
        s = self.btmc.getPower()
        v = self.btmc.getVisibility()
        print "BT update [info] power:"+str(s)+"; visibility:"+str(v)
        if s == 1:
            self.toggle1show()
            if v:
                self.toggle1.state_set(1)
            else:
                self.toggle1.state_set(0)

            self.toggle0.state_set( 1 )

        else:
            self.toggle1hide()
            self.toggle0.state_set( 0 )

    def toggle0Click(self, obj, event, *args, **kargs):
        if not self.btmc.getPower() == obj.state_get():
            self.btmc.setPower( obj.state_get() )
            self.update()

    def toggle1Click(self, obj, event, *args, **kargs):
        if not self.btmc.getVisibility() == obj.state_get():
            self.btmc.setVisibility( obj.state_get() )
            self.update()

    def toggle1show(self):
        if self.toggle1hidden:
            self.toggle1 = elementary.Toggle(self.window)
            self.toggle1.label_set(_("Visibility:"))
            self.toggle1.size_hint_align_set(-1.0, 0.0)
            self.toggle1.states_labels_set(_("On"),_("Off"))
            self.toggle1.state_set(self.btmc.getVisibility())
            self.toggle1.changed = self.toggle1Click
            self.main.pack_end(self.toggle1)
            self.toggle1.show()
            self.toggle1hidden=0

    def toggle1hide(self):
        self.toggle1hidden=1
        try:
          self.toggle1.delete()
        except:
          pass

    def stopUpdate(self):
        self.signal.remove()

    def createView(self):
        self.main = elementary.Box(self.window)

        try:

            # connect to dbus
            self.dbusObjBT = getDbusObject (self.dbus,
                "org.freesmartphone.odeviced",
                "/org/freesmartphone/Device/PowerControl/Bluetooth",
                "org.freesmartphone.Resource" )

            self.dbusObjPower = getDbusObject (self.dbus,
                "org.freesmartphone.odeviced",
                "/org/freesmartphone/Device/PowerControl/Bluetooth",
                "org.freesmartphone.Device.PowerControl" )

            # set update triggers
            self.signal = self.dbusObjBT.connect_to_signal("Power",      self.update)

            self.btmc = BtMstateContener(self.dbusObjBT, self.dbusObjPower)

            self.toggle0 = elementary.Toggle(self.window)
            self.toggle0.label_set(_("Bluetooth radio:"))
            self.toggle0.size_hint_align_set(-1.0, 0.0)
            self.toggle0.states_labels_set(_("On"),_("Off"))
            self.toggle0.show()
            self.toggle0.changed = self.toggle0Click
            self.main.pack_start(self.toggle0)

            self.toggle1hidden=1

            self.update()

        except dbus.exceptions.DBusException, e:

            print "DBus is not running", repr(e)
            self.error()

        return self.main
