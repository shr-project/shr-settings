import elementary, module, dbus

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
    name = _("Call settings")

    def isEnabled(self):
        return True
    

    def error(self, result):
        print "async dbus error"

    def callback(self):
        print "async dbus callback"

    def power_handle(self, obj, event, *args, **kargs):
       if obj.state_get(): 
           self.gps.SetCallingIdentification("on",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(1)
       else:
           self.gps.SetCallingIdentification("off",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(0)


    def res_handle(self, obj, event, *args, **kargs):
        if obj.state_get():
            self.gps.SetCallingIdentification("network",reply_handler=self.callback,error_handler=self.error)
            self.toggle1hide()
        else:
            self.gps.SetCallingIdentification("on",reply_handler=self.callback,error_handler=self.error)
            self.toggle1show()
            self.toggle1.state_set(1)

    def cb_get_callidenti(self, state):
        if state == "network":
            self.toggle0.state_set(1)
        else:
            self.toggle0.state_set(0)
            self.toggle1show()
            self.toggle1.state_set(state=="on")
        self.toggle0.show()

    def toggle1hide(self):
        self.toggle1.delete()

    def toggle1show(self):
        self.toggle1 = elementary.Toggle(self.window)
        self.toggle1.size_hint_align_set(-1.0, 0.0)
        self.toggle1.states_labels_set(_("On"),_("Off"))
        self.toggle1.changed = self.power_handle
        self.box1.pack_end(self.toggle1)
        self.toggle1.show()

    def createView(self):
        try:
            self.gps = getDbusObject (self.dbus, "org.freesmartphone.ogsmd", "/org/freesmartphone/GSM/Device", "org.freesmartphone.GSM.Network") 
        except:
            label = elementary.Label(self.window)
            label.label_set(_("can't connect to dbus"))
            return label

        self.box1 = elementary.Box(self.window)

        self.toggle0 = elementary.Toggle(self.window)
        self.toggle0.label_set(_("Show my number:"))
        self.toggle0.size_hint_align_set(-1.0, 0.0)
        self.toggle0.states_labels_set(_("By network"),_("Manual"))
        self.toggle0.changed = self.res_handle
        self.box1.pack_start(self.toggle0)

        self.gps.GetCallingIdentification(reply_handler=self.cb_get_callidenti, error_handler=self.error)

        return self.box1
