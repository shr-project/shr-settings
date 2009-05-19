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


class ResourceToggleBox(elementary.Box):

    def update(self):
        """
        Set the object state to be opposite the current state of the resource
        Set the toggle to the object state
        """
        self.state = not(self.dbusObj.GetResourceState(self.resource))
        self.toggle.state_set(self.state)

    def toggleChanged(self, obj, event, *args, **kargs):
        """
        Toggle the resource to opposite the toggle changed-to state
        Update the toggles to match current system settings
        """
        if not(obj.state_get()):
            self.dbusObj.RequestResource(self.resource)
        else:
            self.dbusObj.ReleaseResource(self.resource)
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

        self.toggle = elementary.Toggle(self.window)
        self.toggle.label_set(label)
        self.toggle.states_labels_set(_("On"),_("Off"))
        self.toggle.changed = self.toggleChanged
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
        label.label_set("DBus is borked")
        label.show()

        self.main.pack_start(label)

    def update(self, resourceName, resourceState, resourceInfo):
        self.cpu.update()
        self.display.update()

    def createView(self):

        # create the box
        self.main = elementary.Box(self.window)

        try:

            # connect to dbus
            # (controls and info;
            #   some abilities are not implemented in org.freesmartphone.Usage)
            #
            # Will the differences between org.shr.ophonekitd.Usage and
            # org.freesmartphone.ousaged ever be resolved into one?
            #       - Cameron
            #
            self.dbusObj = getDbusObject (self.dbus,
                "org.shr.ophonekitd.Usage",
                "/org/shr/ophonekitd/Usage",
                "org.shr.ophonekitd.Usage")

            # connect to dbus
            # (signals;
            #   which are not implemented in org.shr.ophonekitd.Usage)
            self.dbusSignalsObj = getDbusObject(self.dbus,
                "org.freesmartphone.ousaged",
                "/org/freesmartphone/Usage",
                "org.freesmartphone.Usage")

            # set update triggers
            self.dbusSignalsObj.connect_to_signal("ResourceChanged", self.update)

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
