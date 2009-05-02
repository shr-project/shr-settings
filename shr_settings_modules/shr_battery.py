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
    name = _("Battery")

    def error(self):
        """
        Report the DBus is fsck'd
        """
        label = elementary.Label(self.window)
        label.label_set("DBus is borked")
        self.main.pack_start(label)
        label.show()

    def sectotime(self, sec):
        hours   = int( sec / 3600 )
        min     = int( ( sec % 3600 ) / 60 )
        return ( hours, min )

    def refreshAct(self, signalData = None):
        vol     = "1234"
        temp    = "1234"
        cur     = "1234"
        cap     = "1234"
        time    = "1234"
        rate    = ""

        try:
            cap     = os.popen("cat /sys/class/power_su*ply/bat*/capacity").readline().strip()
            cur     = int(os.popen("cat /sys/class/power_su*ply/bat*/current_now").readline())/1000
            temp    = float(os.popen("cat /sys/class/power_sup*ly/bat*/temp").readline())/10
            vol     = float(os.popen("cat /sys/class/power_sup*ly/bat*/voltage_now").readline())/(1000*1000)
            sta     = os.popen("cat /sys/class/power_su*ply/bat*/status").readline().strip()
            if sta == "Charging":
                time = int(os.popen("cat /sys/class/power_su*ply/bat*/time_to_full_now").readline())
                try:
                    rate = int(os.popen("cat /sys/class/i2c-adapter/i2c-0/0-0073/pcf50633-mbc/chg_curlim").readline())
                    rate = " ({0} mA)".format(rate)
                except:
                    pass
            else:
                time = int(os.popen("cat /sys/class/power_su*ply/bat*/time_to_empty_now").readline())

            self.timel.setLabel(self.sectotime(time))
            self.capl.setLabel(cap)
            self.curl.setLabel(cur)
            self.templ.setLabel(temp)
            self.voll.setLabel(vol)
            self.stal.setLabel(sta+rate)

        except:
            return 1
            print ":("

    def createView(self):

        # create the box
        self.box = elementary.Box(self.window)
        self.box.size_hint_weight_set(1.0, 1.0)
        self.box.size_hint_align_set(-1.0, 0.0)

        try:

            # connect to dbus
            self.dbusObj = getDbusObject(self.dbus,
                "org.freesmartphone.odeviced",
                "/org/freesmartphone/Device/PowerSupply/battery",
                "org.freesmartphone.Device.PowerSupply")

            # set update triggers
            self.dbusObj.connect_to_signal("Capacity",      self.refreshAct)
            self.dbusObj.connect_to_signal("PowerStatus",   self.refreshAct)

            # create labels
            self.stal   = BatteryLabel(self.window, "{0}{1}",                       _("Status: "))
            self.voll   = BatteryLabel(self.window, "{0}{1:.3f} V",                 _("Voltage: "))
            self.templ  = BatteryLabel(self.window, "{0}{1:.1f} 'C",                _("Temperature: "))
            self.curl   = BatteryLabel(self.window, "{0}{1} mA",                    _("Current: "))
            self.capl   = BatteryLabel(self.window, "{0}{1} %",                     _("Capacity: "))
            self.timel  = BatteryLabel(self.window, "{0}{1[0]:d} h {1[1]:02d} min", _("Remaining time: "))

            # pack labels into the box
            self.box.pack_start(self.stal)
            self.box.pack_start(self.voll)
            self.box.pack_start(self.templ)
            self.box.pack_start(self.curl)
            self.box.pack_start(self.capl)
            self.box.pack_start(self.timel)

            # update the labels
            self.refreshAct()

            self.box.show()

        except dbus.exceptions.DBusException, e:

            print "DBus is not running", repr(e)
            self.error()

        return self.box

