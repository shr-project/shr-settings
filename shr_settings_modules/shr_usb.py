import elementary, module, dbus
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)


#-------------------------------------------------------------------
class Usb(module.AbstractModule):
    """ USB Module """
    name = _("USB settings")

    def error(self, result):
        print "async dbus error"

    def callback(self):
        print "async dbus callback"

    def isEnabled(self):
        return True
    
    def power_handle(self, obj, *args, **kargs):
       # if ResourceState already equals off/on setting do nothing
       if self.usb.GetResourceState("UsbHost") == obj.state_get():
            return 0
       if obj.state_get():
           self.usb.SetResourcePolicy("UsbHost","enabled",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(1)
       else:
           self.usb.SetResourcePolicy("UsbHost","disabled",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(0)


    def res_handle(self, obj, *args, **kargs):
        if obj.state_get():
            # slider has been moved to 'Auto'
            self.usb.SetResourcePolicy("UsbHost","auto",reply_handler=self.callback,error_handler=self.error)
            self.toggle1hide()
        else:
            if self.toggle1hidden:
                self.toggle1show()
                # slider has been moved to 'Manual'
                if self.usb.GetResourceState("UsbHost"):
                    self.usb.SetResourcePolicy("UsbHost","enabled",reply_handler=self.callback,error_handler=self.error)
                    self.toggle1.state_set(1)
                else:
                    self.usb.SetResourcePolicy("UsbHost","disabled",reply_handler=self.callback,error_handler=self.error)
                    self.toggle1.state_set(0)

    def toggle1hide(self):
        try:
            self.toggle1.delete()
        except:
            pass
        self.toggle1hidden=1

    def toggle1show(self):
        self.toggle1 = elementary.Toggle(self.window)
        self.toggle1.size_hint_align_set(-1.0, 0.0)
        self.toggle1.states_labels_set(_("Host"),_("Device"))
        self.toggle1._callback_add('changed', self.power_handle)
        self.box1.pack_end(self.toggle1)
        self.toggle1hidden=0  
        usbstate =  self.usb.GetResourceState("UsbHost")
        self.toggle1.state_set(usbstate)
        self.toggle1.show()

    def createView(self):
        try:
            self.usb = getDbusObject (self.dbus, "org.freesmartphone.ousaged", "/org/freesmartphone/Usage", "org.freesmartphone.Usage") 
        except:
            label = elementary.Label(self.window)
            label.label_set(_("Couldn't connect to FSO"))
            return label

        self.box1 = elementary.Box(self.window)

        self.toggle0 = elementary.Toggle(self.window)
        self.toggle0.label_set(_("USB mode:"))
        self.toggle0.size_hint_align_set(-1.0, 0.0)
        self.toggle0.states_labels_set(_("Auto"),_("Manual"))
        self.toggle0._callback_add('changed', self.res_handle)
        self.box1.pack_start(self.toggle0)
        self.toggle0.show()

        usbpolicy =  self.usb.GetResourcePolicy("UsbHost")
        if usbpolicy == "auto":
            self.toggle0.state_set(1)
            self.toggle1hidden=1
        else:
            self.toggle0.state_set(0)
            self.toggle1show()

        return self.box1
