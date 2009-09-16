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
    def __init__(self, buspower):
        self.state = 0
#        self.dbusObjBT = busres
        self.dbusObj = buspower


    def getPolicy(self):
        return self.dbusObj.GetResourcePolicy('Bluetooth')

    def getPower(self):
        return self.dbusObj.GetResourceState('Bluetooth')

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

    def callback(self):
        print "async dbus callback"

    def error(self):
        label = elementary.Label(self.window)
        label.label_set(_("Couldn't connect to FSO"))
        label.show()
        self.main.pack_start(label)

    def update(self):
        s = self.btmc.getPower()
        r = self.btmc.getPolicy()
        v = self.btmc.getVisibility()
        print "BT update [info] power:"+str(s)+"; visibility:"+str(v)
        if r != 'auto': 
            self.toggles.state_set( 0 )
            self.toggle0show()
            if r=='enabled':
                self.toggle0.state_set(1)
            else:
                self.toggle0.state_set(0)
        else:
            self.toggles.state_set( 1 )
        if s == 1:
            self.toggle1show()
            if v:
                self.toggle1.state_set(1)
            else:
                self.toggle1.state_set(0)


        else:
            self.toggle0hide()
            self.toggle1hide()

#    def togglesClick(self, obj, event, *args, **kargs):
 #       if not self.btmc.getPower() == obj.state_get():
  #         self.btmc.setPower( obj.state_get() )
   #         self.update()

    def toggle1Click(self, obj, event, *args, **kargs):
        if not self.btmc.getVisibility() == obj.state_get():
            self.btmc.setVisibility( obj.state_get() )
            self.update()

    def power_handle(self, obj, event, *args, **kargs):
       # if ResourceState already equals off/on setting do nothing
       if self.bt.GetResourceState("Bluetooth") == obj.state_get():
            return 0
       if obj.state_get():
           self.bt.SetResourcePolicy("Bluetooth","enabled",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(1)
       else:
           self.bt.SetResourcePolicy("Bluetooth","disabled",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(0)

    def res_handle(self, obj, event, *args, **kargs):
        if obj.state_get():
            # slider has been moved to 'Auto'
            self.bt.SetResourcePolicy("Bluetooth","auto",reply_handler=self.callback,error_handler=self.error)
            self.toggle0hide()
        else:
            if self.toggle0hidden:
                self.toggle0show()
                # slider has been moved to 'Manual'
                if self.bt.GetResourceState("Bluetooth"):
                    self.bt.SetResourcePolicy("Bluetooth","enabled",reply_handler=self.callback,error_handler=self.error)
                    self.toggle0.state_set(1)
                else:
                    self.bt.SetResourcePolicy("Bluetooth","disabled",reply_handler=self.callback,error_handler=self.error)
                    self.toggle0.state_set(0)


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

    def toggle0hide(self):
        try:
            self.toggle0.delete()
        except:
            pass
        self.toggle0hidden=1

    def toggle0show(self):
        self.toggle0 = elementary.Toggle(self.window)
        self.toggle0.size_hint_align_set(-1.0, 0.0)
        self.toggle0.states_labels_set(_("On"),_("Off"))
        self.toggle0.changed = self.power_handle
        self.main.pack_end(self.toggle0)
        self.toggle0hidden=0
        btstate = self.bt.GetResourceState("Bluetooth")
        self.toggle0.state_set(btstate)
        self.toggle0.show()

    def stopUpdate(self):
        #self.signal.remove()
        pass

    def createView(self):
        self.main = elementary.Box(self.window)

        try:
            '''
            # connect to dbus
            self.dbusObjBT = getDbusObject (self.dbus,
                "org.freesmartphone.odeviced",
                "/org/freesmartphone/Device/PowerControl/Bluetooth",
                "org.freesmartphone.Resource" )
            '''
            self.dbusObjPower = getDbusObject (self.dbus,
                "org.freesmartphone.ousaged",
                "/org/freesmartphone/Usage",
                "org.freesmartphone.Usage" )

            # set update triggers
#            self.signal = self.dbusObjBT.connect_to_signal("Power",      self.update)

            self.bt = self.dbusObjPower
            self.btmc = BtMstateContener(self.dbusObjPower)

            self.toggles = elementary.Toggle(self.window)
            self.toggles.label_set(_("Bluetooth radio:"))
            self.toggles.size_hint_align_set(-1.0, 0.0)
            self.toggles.states_labels_set(_("Auto"),_("Manual"))
            self.toggles.show()
            self.toggles.changed = self.res_handle
            self.main.pack_start(self.toggles)

            self.toggle0hidden=1
            self.toggle1hidden=1

            self.update()

        except dbus.exceptions.DBusException, e:

            print "DBus is not running", repr(e)
            self.error()

        return self.main
