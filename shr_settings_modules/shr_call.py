import elementary, module, os, dbus

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

class Call(module.AbstractModule):
    name = _("Call")

    def error(self, result):
        print "async dbus error"

    def callback(self):
        print "async dbus callback"

    def onoff(self, string):
        if string=="on":
            return 1
        else:
            return 0

    def isEnabled(self):
        return True
    
    def power_handle(self, obj, event):
       #if self.onoff(self.gps.GetCallingIdentification())==obj.state_get():
       #     return 0
       if obj.state_get(): 
           self.gps.SetCallingIdentification("on",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(1)
       else:
           self.gps.SetCallingIdentification("off",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(0)


    def res_handle(self, obj, event):
        if obj.state_get():
            self.gps.SetCallingIdentification("network",reply_handler=self.callback,error_handler=self.error)
            self.toggle1.hide()
        else:
            self.gps.SetCallingIdentification("on",reply_handler=self.callback,error_handler=self.error)
            self.toggle1.state_set(1)
            self.toggle1.show()

    def createView(self):
        try:
            self.gps = getDbusObject (self.dbus, "org.freesmartphone.ogsmd", "/org/freesmartphone/GSM/Device", "org.freesmartphone.GSM.Network") 
        except:
            label = elementary.Label(self.window)
            label.label_set(_("can't connect to dbus"))
            return label

        box1 = elementary.Box(self.window)

        toggle0 = elementary.Toggle(self.window)
        toggle0.label_set(_("Show my number:"))
        toggle0.size_hint_align_set(-1.0, 0.0)
        toggle0.states_labels_set(_("By network"),_("Manual"))
        toggle0.changed = self.res_handle
        box1.pack_start(toggle0)
        toggle0.show()

        self.toggle1 = elementary.Toggle(self.window)
        self.toggle1.size_hint_align_set(-1.0, 0.0)
        self.toggle1.states_labels_set(_("On"),_("Off"))
        self.toggle1.changed = self.power_handle
        box1.pack_end(self.toggle1)


        if self.gps.GetCallingIdentification()=="network":
            toggle0.state_set(1)
            self.toggle1.hide()
        else:
            toggle0.state_set(0)
            self.toggle1.show()
        self.toggle1.state_set(self.onoff(self.gps.GetCallingIdentification()))

        return box1
