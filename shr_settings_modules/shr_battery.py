import module, os, re, sys, elementary, ecore
import dbus
import threading

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


class BatteryLabel(elementary.Label):
    """
    Generic class for the labels used below
    """

    def __init__(self,win, format_string, static_label):
        super(BatteryLabel, self).__init__(win)
        self.size_hint_align_set(-1.0, 0.0)

        self.fs = format_string
        self.sl = static_label
        self.show()

    def setLabel(self, dynamic_label):
        """
        Call elementary.Label.label_set with static label values
        and formatted appropriately
        """
        finalLabel = str(self.fs).format(self.sl, dynamic_label)
        self.label_set(finalLabel)


class Battery(module.AbstractModule):
    name = _("Battery settings")

    def error(self):
        """
        Report the DBus is fsck'd
        """
        label = elementary.Label(self.window)
        label.label_set("DBus is borked")
        self.main.pack_start(label)
        label.show()

    def getValue(self,nodePath, scale = 1):
        """
        Given a /sys node path and scaling factor,
        return the intelligent result (int, float, str)

        Bool is not covered or required currently,
        but is implicit with int values
        """
        # retrieve raw value
        value = os.popen("cat "+nodePath).readline().strip()

        # try some intelligent filtering
        try:
            # if int(a) == float(a), assume valid int value
            value = float(value) * scale
            if int(value) == float(value):
                return int(value)
            # otherwise, assume valid float value
            else:
                return float(value)
        # ValueError means that value was neither int() or float(),
        #   therefore assume str().
        except ValueError, e:
            return str(value)

    def sectotime(self, sec):
        """
        Takes a time in seconds
        Returns tuple of ( hours, minutes )
        """
        hours   = int( sec / 3600 )
        min     = int( ( sec % 3600 ) / 60 )
        return ( hours, min )

    def refreshAct(self, signalData = None):
        """
        Update the data displayed in BatteryLabel
        """

        try:

            # read data from /sys nodes
            cap     = self.getValue("/sys/class/power_su*ply/bat*/capacity")
            cur     = self.getValue("/sys/class/power_su*ply/bat*/current_now", 1e-3)
            temp    = self.getValue("/sys/class/power_sup*ly/bat*/temp", 1e-1)
            vol     = self.getValue("/sys/class/power_sup*ly/bat*/voltage_now", 1e-6)
            sta     = self.getValue("/sys/class/power_su*ply/bat*/status")
            if sta == "Charging":
                time = self.getValue("/sys/class/power_su*ply/bat*/time_to_full_now")
                try:
                    rate = self.getValue("/sys/class/i2c-adapter/i2c-0/0-0073/pcf50633-mbc/chg_curlim")
                    rate = " ({0} mA)".format(rate)
                    sta += rate
                except:
                    pass
            else:
                time = self.getValue("/sys/class/power_su*ply/bat*/time_to_empty_now")

            # calculate hours and minutes from the found time value
            time = self.sectotime(time)

            # set the displayed labels
            self.timel.setLabel(time)
            self.capl.setLabel(cap)
            self.curl.setLabel(cur)
            self.templ.setLabel(temp)
            self.voll.setLabel(vol)
            self.stal.setLabel(sta)

        except:
            return 1
            print ":("

    def createView(self):

        # create the box
        self.main = elementary.Box(self.window)
        self.main.size_hint_weight_set(1.0, 1.0)
        self.main.size_hint_align_set(-1.0, 0.0)

        try:

            # connect to dbus
            self.dbusObj = getDbusObject(self.dbus,
                "org.freesmartphone.odeviced",
                "/org/freesmartphone/Device/PowerSupply/battery",
                "org.freesmartphone.Device.PowerSupply")

            # set update triggers
            self.dbusObj.connect_to_signal("Capacity",      self.refreshAct)
            self.dbusObj.connect_to_signal("PowerStatus",   self.refreshAct)

            # create labels, setting the display formats and static labels
            self.stal   = BatteryLabel(self.window, "{0}{1}",                       _("Status: "))
            self.voll   = BatteryLabel(self.window, "{0}{1:.3f} V",                 _("Voltage: "))
            self.templ  = BatteryLabel(self.window, "{0}{1:.1f} 'C",                _("Temperature: "))
            self.curl   = BatteryLabel(self.window, "{0}{1:.0f} mA",                _("Current: "))
            self.capl   = BatteryLabel(self.window, "{0}{1} %",                     _("Capacity: "))
            self.timel  = BatteryLabel(self.window, "{0}{1[0]:d} h {1[1]:02d} min", _("Remaining time: "))

            # pack labels into the box
            self.main.pack_start(self.stal)
            self.main.pack_start(self.voll)
            self.main.pack_start(self.templ)
            self.main.pack_start(self.curl)
            self.main.pack_start(self.capl)
            self.main.pack_start(self.timel)

            # update the labels
            self.refreshAct()

            self.main.show()

        except dbus.exceptions.DBusException, e:

            print "DBus is not running", repr(e)
            self.error()

        return self.main

