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


class ResourceToggleBox(elementary.Box):

    def update(self):
        """
        Set the object state to be opposite the current state of the resource
        Set the toggle to the object state
        """
        self.state = True if self.dbusObj.GetResourcePolicy(self.resource) == "enabled" else False
        self.toggle.state_set(self.state)

    def toggleChanged(self, obj, *args, **kargs):
        """
        Toggle the resource to opposite the toggle changed-to state
        Update the toggles to match current system settings
        """
        if not(obj.state_get()):
            self.dbusObj.SetResourcePolicy(self.resource, "auto")
        else:
            self.dbusObj.SetResourcePolicy(self.resource, "enabled")
        self.update()

    def __init__(self, win, dbusObj, resource, label):
        """
        initialize the box and load objects
        Update the toggles to match current system settings
        """

        super(ResourceToggleBox, self).__init__(win)
        self.window = win
        self.resource = resource
        self.dbusObj = dbusObj
        self.state = None

        self.toggle = elementary.Check(self.window)
        self.toggle.style_set("toggle");
        self.toggle.text_set(label)
        self.toggle.part_text_set("on", _("Forbid"));
        self.toggle.part_text_set("off", _("Allow"));
        self.toggle._callback_add('changed', self.toggleChanged)
        self.toggle.size_hint_align_set(-1.0, 0.0)
        self.toggle.show()

        self.pack_start(self.toggle)
        self.size_hint_align_set(-1.0, 0.0)

        self.update()
        self.show()


class Pm(module.AbstractModule):
    name = _("Power settings")

    def error(self):
        """
        Report the DBus is fsck'd
        """
        label = elementary.Label(self.window)
        label.text_set(_("Couldn't connect to FSO or phonefsod"))
        label.show()

        self.main.pack_start(label)

    def update(self, resourceName, resourceState, resourceInfo):
        self.cpu.update()
        self.display.update()

    def stopUpdate(self):
        self.signal.remove()

    def createView(self):

        # create the box
        self.main = elementary.Box(self.window)

        try:

            # connect to dbus
            self.dbusObj = getDbusObject(self.dbus,
                "org.freesmartphone.ousaged",
                "/org/freesmartphone/Usage",
                "org.freesmartphone.Usage")

            # set update triggers
            self.signal = self.dbusObj.connect_to_signal("ResourceChanged", self.update)

            # Create ToggleBoxes
            self.display = ResourceToggleBox(self.window, self.dbusObj, 'Display', _("Auto-dimming:"))
            self.cpu     = ResourceToggleBox(self.window, self.dbusObj, 'CPU', _("Auto-suspend:"))

            # Pack ToggleBoxes
            self.main.pack_start(self.display)
            self.main.pack_end(self.cpu)

        except dbus.exceptions.DBusException, e:
            print "DBus is not running", repr(e)
            self.error()

        return self.main
