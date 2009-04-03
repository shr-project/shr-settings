import elementary
import module
import dbus
import ecore

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

def handler():
    return 0

def error(msg):
    return 0

class Display(module.AbstractModule):
    name = _("Display")

    def setbacklight(self, obj, event, *args, **kargs):
        if self.value != self.slider.value:
            self.display.SetBrightness(self.slider.value, reply_handler=handler, error_handler=error)
            self.value = self.slider.value
        return 1

    def getbacklight(self):
        return self.display.GetBrightness()
    
    def isEnabled(self):
        try:
            self.display = getDbusObject (self.dbus, "org.freesmartphone.odeviced", "/org/freesmartphone/Device/Display/0", "org.freesmartphone.Device.Display")
            return 1
        except:
            return 0

    def createView(self):
        self.slider = elementary.Slider(self.window)
        self.slider.label_set(_("Backlight "))
        #slider.span_size_set(160)
        #slider.size_hint_align_set(0, 0.5)
        #slider.size_hint_weight_set(0, 1)
        self.slider.unit_format_set(" %3.0f%% ")
        self.slider.min_max_set(2, 100)
        self.value = self.getbacklight()
        self.slider.value = self.value
        self.slider.show()
        self.slider._callback_add("changed", self.setbacklight)
        return self.slider
