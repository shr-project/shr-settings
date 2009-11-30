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

 
class WifiToggleBox(elementary.Box):
    """ Class for Wifi Connection power toggle """

    def update(self, state):
        """ Set the toggle to the wifi power state """
        self.toggle.state_set(state)

    def toggleChanged(self, obj, *args, **kargs):
        """
        Toggle the resource to opposite the toggle changed-to state
        Update the toggles to match current system settings
        """
        policy = 'disabled'
        if obj.state_get(): policy = 'enabled'
        self.dbusObj.SetResourcePolicy('WiFi', policy)

    def init_toggle_reply_handler(self, state):
        """ Handler that sets the initial toggle setting 
            It also makes the toggle visible
        """
        self.update(state)
        self.pack_start(self.toggle)
        self.toggle.show()

    def init_toggle_error_handler(self, e):
        """ if the initial state could not be retrieved """
        # we'll not show the toggle here
        print "received exception " + str(e)
        reason = 'Unknown DBus Exception'
        if e._dbus_error_name == 'org.freesmartphone.Usage.ResourceUnknown':
            reason= "Wifi not available"
        # Show an error message instead
        label = elementary.Label(self.wifi.main)
        label.label_set(reason)
        label.show()
        self.wifi.main.pack_start(label)

    def __init__(self, wifi, dbusObj):
        """
        initialize the box and load objects
        Update the toggles to match current system settings
        """

        super(WifiToggleBox, self).__init__(wifi.window)
        self.wifi = wifi
        self.dbusObj = dbusObj
        self.state = None

        self.toggle = elementary.Toggle(self.wifi.window)
        self.toggle.label_set(_("WiFi radio:"))
        self.toggle.states_labels_set(_("On"),_("Off"))
        self.toggle._callback_add('changed', self.toggleChanged)
        self.toggle.size_hint_align_set(-1.0, 0.0)

        #ask async for WiFi state and set & show toggle then
        self.dbusObj.GetResourceState('WiFi', 
          reply_handler = self.init_toggle_reply_handler,
          error_handler = self.init_toggle_error_handler)

        self.size_hint_align_set(-1.0, 0.0)
        self.show()


class Wifi(module.AbstractModule):
    name = _("WiFi settings")

    def error(self):
        label = elementary.Label(self.window)
        label.label_set(_("Couldn't connect to FSO"))
        label.show()
        self.main.pack_start(label)

    def update(self, name, state, attr):
        """ catches the ResourceChanged signal and acts if WiFi changes
        """
        if name != 'WiFi': return
        self.wifiToggle.update(state)

    def stopUpdate(self):
        self.signal.remove()

    def createView(self):
        self.main = elementary.Box(self.window)
        try:
            # connect to dbus
            self.dbusObj = getDbusObject (self.dbus,
                                          "org.freesmartphone.ousaged",
                                          "/org/freesmartphone/Usage",
                                          "org.freesmartphone.Usage")

            # connect to dbus signals
            self.signal = self.dbusObj.connect_to_signal("ResourceChanged", self.update)
            # create/pack toggle box
            self.wifiToggle = WifiToggleBox(self, self.dbusObj)
            self.main.pack_start(self.wifiToggle)

        except dbus.exceptions.DBusException, e:
            self.error()

        return self.main
