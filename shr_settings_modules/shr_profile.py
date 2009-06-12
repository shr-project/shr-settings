import elementary, module
import dbus

# Locale support
import gettext

## Testing
from functools import partial


try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)


class Profile(module.AbstractModule):
    name = _("Profile settings")

    def error(self):
        """
        Report the DBus is fsck'd
        """
        label = elementary.Label(self.window)
        label.label_set("DBus is borked")
        self.main.pack_start(label)
        label.show()

    def profileChanged(self, profile):
        """
        Signal Handler for profile updates

        This is rare, but just in case the profile updates from
        elsewhere while this module is open, we need to capture
        the signal and update the current profile name
        """
        self.ProfileNameUpdate()

    def setCurrentProfile(self, obj, event, name, *args, **kargs):
        """
        Set the current profile to `name`
        """
        self.dbusObj.SetProfile(name)
        self.ProfileNameUpdate()

    def ProfileNameUpdate(self):
        """
        Updates the displayed value of the current profile
        """
        self.currentProfile = self.dbusObj.GetProfile().title()
        self.hoverSel.label_set(_("Profiles (%s)" % self.currentProfile))

    def listProfiles(self):
        """
        Displays the profiles Hoversel
        """
        self.main.size_hint_weight_set(1.0, -1.0)

        # Available Profiles
        self.profiles = self.dbusObj.GetProfiles()

        # Listing HoverSelect
        self.hoverSel = elementary.Hoversel(self.window)
        self.hoverSel.hover_parent_set(self.window)
        self.hoverSel.size_hint_weight_set(-1.0, 0.0)
        self.hoverSel.size_hint_align_set(-1.0, 0.0)
        self.main.pack_end(self.hoverSel)
        self.hoverSel.show()

        # Set current profile name to the hoverSel label
        self.ProfileNameUpdate()

        # Add HoversleItems
        # The callback is a bit of functools.partial magic
        for i in self.profiles:
            self.hoverSel.item_add(str(i).title(),
                "arrow_down",
                elementary.ELM_ICON_STANDARD,
                partial( self.setCurrentProfile, name = i ))

    def createView(self):

        self.main = elementary.Box(self.window)

        try:
            # create dbus object
            self.dbusObj = getDbusObject(self.dbus,
                "org.freesmartphone.opreferencesd",
                "/org/freesmartphone/Preferences",
                "org.freesmartphone.Preferences" )

            # creat signal listener for profile updates
            #   This is rare, but just in case the profile updates from
            #   elsewhere while this module is open, we need to capture
            #   the signal and update the current profile name
            self.dbusObj.connect_to_signal("Notify",
                self.profileChanged)

            self.listProfiles()

        except:
            self.error()

        return self.main
