import elementary
import module
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


class Pm(module.AbstractModule):
    name = _("Power")

    def request(self, name, state):
        if state:
            self.ophonekitd.RequestResource(name)
        else:
            self.ophonekitd.ReleaseResource(name)

    def cpurequest(self, obj, event):
        self.request('CPU',not(obj.state_get()))

    def displayrequest(self, obj, event):
        self.request('Display',not(obj.state_get()))
    
    def isEnabled(self):
        try:
            self.ophonekitd = getDbusObject (self.dbus, "org.shr.ophonekitd.Usage", "/org/shr/ophonekitd/Usage", "org.shr.ophonekitd.Usage")
            return 1
        except:
            return 0


    def createView(self):
    	self.main = elementary.Box(self.window)
        cpu = elementary.Toggle(self.window)
        cpu.label_set(_("Auto-suspend:"))
        cpu.changed = self.cpurequest
        self.main.pack_start(cpu)
        cpu.size_hint_align_set(-1.0, 0.0)
        cpu.state_set(not(self.ophonekitd.GetResourceState('CPU')))
        cpu.show()
        display = elementary.Toggle(self.window)
        display.label_set(_("Auto-dimming:"))
        display.changed = self.displayrequest
        self.main.pack_start(display)
        display.size_hint_align_set(-1.0, 0.0)
        display.state_set(not(self.ophonekitd.GetResourceState('Display')))
        display.show()
        return self.main
