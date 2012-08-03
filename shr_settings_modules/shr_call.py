import elementary, module, dbus

from helper import getDbusObject

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class Call(module.AbstractModule):
    name = _("Call settings")

    def isEnabled(self):
        return True
    

    def error(self, result):
        print "async dbus error"
        self.loading.text_set(_("Turn GSM on."))

    def callback(self):
        print "async dbus callback"

    def power_handle(self, obj, *args, **kargs):
       if obj.state_get(): 
           self.gps.SetCallingIdentification("on",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(1)
       else:
           self.gps.SetCallingIdentification("off",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(0)


    def res_handle(self, obj, *args, **kargs):
        if obj.state_get():
            self.gps.SetCallingIdentification("network",reply_handler=self.callback,error_handler=self.error)
            self.toggle1hide()
        else:
            if self.toggle1hidden:
              self.gps.SetCallingIdentification("on",reply_handler=self.callback,error_handler=self.error)
              self.toggle1show()
              self.toggle1.state_set(1)

    def cb_get_callidenti(self, state):
        self.loading.delete()

        self.toggle0 = elementary.Check(self.window)
        self.toggle0.style_set("toggle");
        self.toggle0.text_set(_("Show my number:"))
        self.toggle0.size_hint_align_set(-1.0, 0.0)
        self.toggle0.part_text_set("on", _("By network"));
        self.toggle0.part_text_set("off", _("Manual"));
        self.toggle0._callback_add('changed', self.res_handle)
        self.box1.pack_start(self.toggle0)

        if state == "network":
            self.toggle0.state_set(1)
            self.toggle1hidden=1
        else:
            self.toggle0.state_set(0)
            self.toggle1show()
            self.toggle1.state_set(state=="on")
        self.toggle0.show()

    def toggle1hide(self):
        self.toggle1.delete()
        self.toggle1hidden=1

    def toggle1show(self):
        self.toggle1 = elementary.Check(self.window)
        self.toggle1.style_set("toggle");
        self.toggle1.size_hint_align_set(-1.0, 0.0)
        self.toggle1.part_text_set("on", _("On"));
        self.toggle1.part_text_set("off", _("Off"));
        self.toggle1._callback_add('changed', self.power_handle)
        self.box1.pack_end(self.toggle1)
        self.toggle1.show()
        self.toggle1hidden=0

    def createView(self):
        try:
            self.gps = getDbusObject (self.dbus, "org.freesmartphone.ogsmd", "/org/freesmartphone/GSM/Device", "org.freesmartphone.GSM.Network") 
        except:
            label = elementary.Label(self.window)
            label.text_set(_("Couldn't connect to FSO"))
            return label

        self.box1 = elementary.Box(self.window)

        self.loading = elementary.Label(self.window)
        self.loading.text_set(_("Please wait..."))
        self.loading.show()
        self.box1.pack_start(self.loading)

        self.gps.GetCallingIdentification(reply_handler=self.cb_get_callidenti, error_handler=self.error)

        return self.box1
