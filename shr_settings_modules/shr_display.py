import elementary
import module
import dbus

from helper import getDbusObject

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


def handler():
    return 0

def error(msg):
    return 0

class Display(module.AbstractModule):
    name = _("Display settings")

    def setbacklight(self, obj, *args, **kargs):
        if self.value != self.slider.value:
            self.display.SetDefaultBrightness(self.slider.value, reply_handler=handler, error_handler=error)
            self.value = self.slider.value
        return 1

    def getbacklight(self):
        return self.display.GetDefaultBrightness()
    
    def isEnabled(self):
        try:
            self.display = getDbusObject (self.dbus, "org.shr.phonefso", 
                                          "/org/shr/phonefso/Usage",
                                          "org.shr.phonefso.Usage")
            return 1
        except:
            return 0

    def createView(self):
        self.slider = elementary.Slider(self.window)
        self.slider.text_set(_("Backlight "))
        self.slider.unit_format_set(" %3.0f%% ")
        self.slider.min_max_set(2, 100)
        self.value = self.getbacklight()
        self.slider.value = self.value
        self.slider.show()
        self.slider._callback_add("delay,changed", self.setbacklight)
        return self.slider
