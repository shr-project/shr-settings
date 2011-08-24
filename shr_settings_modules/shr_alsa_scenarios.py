import elementary, module
import dbus
from helper import getDbusObject

# Locale support
import gettext

## Testing
from functools import partial


try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class AlsaScenarios(module.AbstractModule):
    name = _("Alsa Scenario settings")

    def error(self):
        """
        Report the DBus is fsck'd
        """
        label = elementary.Label(self.window)
        label.text_set(_("Couldn't connect to FSO"))
        self.main.pack_start(label)
        label.show()

    def scenarioChanged(self, scenario, reason):
        """
        Signal Handler for scenario updates

        This is rare, but just in case the scenario updates from
        elsewhere while this module is open, we need to capture
        the signal and update the current scenario name
        """
        self.ScenarioNameUpdate()

    def setCurrentScenario(self, name, obj, event, *args, **kargs):
        """
        Set the current scenario to `name`
        """
        self.dbusObj.SetScenario(name)
        self.ScenarioNameUpdate()

    def ScenarioNameUpdate(self):
        """
        Updates the displayed value of the current scenario
        """
        self.currentScenario = self.dbusObj.GetScenario().title()
        self.hoverSel.text_set(_("Scenarios (%s)") % self.currentScenario)

    def listScenarios(self):
        """
        Displays the scenarios Hoversel
        """
        self.main.size_hint_weight_set(1.0, -1.0)

        # Available Scenarios
        self.scenarios = self.dbusObj.GetAvailableScenarios()
        # Listing HoverSelect
        self.hoverSel = elementary.Hoversel(self.window)
        self.hoverSel.hover_parent_set(self.window)
        self.hoverSel.size_hint_weight_set(-1.0, 0.0)
        self.hoverSel.size_hint_align_set(-1.0, 0.0)
        self.main.pack_end(self.hoverSel)
        self.hoverSel.show()

        # Set current scenario name to the hoverSel label
        self.ScenarioNameUpdate()

        # Add HoversleItems
        # The callback is a bit of functools.partial magic
        for i in self.scenarios:
            self.hoverSel.item_add(str(i).title(),
                "arrow_down",
                elementary.ELM_ICON_STANDARD,
                partial( self.setCurrentScenario, i ))

    def stopUpdate(self):
        self.signal.remove()

    def createView(self):

        self.main = elementary.Box(self.window)

        try:
            # create dbus object
            self.dbusObj = getDbusObject(self.dbus,
                "org.freesmartphone.odeviced",
                "/org/freesmartphone/Device/Audio",
                "org.freesmartphone.Device.Audio" )

            # create signal listener for scenario updates
            #   This is rare, but just in case the scenario updates from
            #   elsewhere while this module is open, we need to capture
            #   the signal and update the current scenario name

            self.signal = self.dbusObj.connect_to_signal("Scenario",
                 self.scenarioChanged)

            self.listScenarios()

        except:
            self.error()

        return self.main
