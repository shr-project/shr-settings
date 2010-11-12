import module, os, elementary
import dbus

# Locale support
import gettext


SYSNODE = {
    # "short name"  : ("/sys/node/location", scaling_factor = 1)
    "charge_limit"  : ("/sys/devices/platform/s3c2440-i2c/i2c-0/0-0073/pcf50633-mbc.0/chg_curlim", 1),
    "usb_limit"     : ("/sys/devices/platform/s3c2440-i2c/i2c-0/0-0073/pcf50633-mbc.0/usb_curlim", 1),
    "capacity"      : ("/sys/class/power_supply/battery/capacity", 1),
    "current"       : ("/sys/class/power_supply/battery/current_now", 1e-3),
    "temperature"   : ("/sys/class/power_supply/battery/temp", 1e-1),
    "voltage"       : ("/sys/class/power_supply/battery/voltage_now", 1e-6),
    "status"        : ("/sys/class/power_supply/battery/status", 1),
    "time_to_full"  : ("/sys/class/power_supply/battery/time_to_full_now", 1),
    "time_to_empty" : ("/sys/class/power_supply/battery/time_to_empty_now", 1),
    "present" : ("/sys/class/power_supply/battery/present", 1),
    }


try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)

def read_file(filename):
    f = file(filename, 'r')
    val = f.readline().strip()
    f.close()
    return val

def write_file(filename, content):
    f = file(filename, 'w')
    f.write(content)
    f.close()

class BatteryLabel(elementary.Label):
    """
    Generic class for the labels used below
    """

    def __init__(self,win, format_string, static_label, bak_format_string = ''):
        super(BatteryLabel, self).__init__(win)
        self.size_hint_align_set(-1.0, 0.0)

        self.fs = format_string
        self.sl = static_label
        self.fs2 = bak_format_string
        self.show()

    def setLabel(self, dynamic_label):
        """
        Call elementary.Label.label_set with static label values
        and formatted appropriately
        """
        try:
            finalLabel = str(self.fs).format(self.sl, dynamic_label)
        except:
            try:
                finalLabel = str(self.fs2).format(self.sl, dynamic_label)
            except:
                finalLabel = self.sl + 'N/A'
        self.label_set(finalLabel)


class FastChargeBox(elementary.Box):
    """
    Class for fast charge toggle
    """

    def update(self):
        """
        Set toggle visibility
        """

        try:
            value   = read_file(self.chgNodePath)
        except:
            self.toggle.hide()
            return False

        if int(value) >= 500:
            self.toggle.state_set(True)
        else:
            self.toggle.state_set(False)
        self.toggle.show()

    def toggleChanged(self, obj, *args, **kargs):
        """
        Toggle the charge rate on/off
        """
        if obj.state_get():
            write_file(self.usbNodePath, "500")
        else:
            write_file(self.usbNodePath, "100")
        self.update()

    def __init__(self, win):
        """
        initialize the box and load objects
        Update the toggles to match current system settings
        """

        super(FastChargeBox, self).__init__(win)
        self.window = win

        self.chgNodePath    = SYSNODE["charge_limit"][0]
        self.usbNodePath    = SYSNODE["usb_limit"][0]

        self.toggle = elementary.Toggle(self.window)
        self.toggle.label_set(_("USB charging rate:"))
        self.toggle.states_labels_set("500 mA","100 mA")
        self.toggle._callback_add('changed', self.toggleChanged)
        self.toggle.size_hint_align_set(-1.0, 0.0)

        self.pack_start(self.toggle)
        self.size_hint_align_set(-1.0, 0.0)

        self.update()
        self.show()

class Battery(module.AbstractModule):
    name = _("Battery settings")

    def error(self):
        """
        Report the DBus is fsck'd
        """
        label = elementary.Label(self.window)
        label.label_set(_("Couldn't connect to FSO"))
        self.main.pack_start(label)
        label.show()

    def getValue(self,nodePath):
        """
        Given a /sys node path and scaling factor,
        return the intelligent result (int, float, str)

        Bool is not covered or required currently,
        but is implicit with int values
        """
        # retrieve raw value
        try:
            value = read_file(SYSNODE[nodePath][0])
        except:
            return 'N/A'
        scale = SYSNODE[nodePath][1]

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
        

    def doupdate(self, obj, *args, **kargs):
        self.update()

    def update(self, signalData = None):
        """
        Update the data displayed in BatteryLabel
        """

        # read data from /sys nodes
        cap     = self.getValue("capacity")
        cur     = self.getValue("current")
        temp    = self.getValue("temperature")
        vol     = self.getValue("voltage")
        sta     = self.getValue("status")
        time = self.getValue("time_to_full")
        if time == 3932100:
            time = self.getValue("time_to_empty")

        # calculate hours and minutes from the found time value
        try:
            time = self.sectotime(time)
        except:
            time = 'N/A'

        # set the displayed labels
        #
        self.charge.setLabel( (cap, time) )
        self.power.setLabel(  (cur, vol) )
        self.status.setLabel( (sta, temp) )

        self.fastChargeToggle.update()

    def stopUpdate(self):
        self.signal1.remove()
        self.signal2.remove()

    def switchToDumb(self, obj, *args, **kwargs):
        write_file('/sys/bus/platform/drivers/bq27000-battery/unbind', 'bq27000-battery.0')
        os.system('modprobe platform_battery')
        obj.delete()
        self.update()

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
            self.signal1 = self.dbusObj.connect_to_signal("Capacity",      self.update)
            self.signal2 = self.dbusObj.connect_to_signal("PowerStatus",   self.update)

            # create labels, setting the display formats and static labels

            # label display formats
            #
            #   !!! This needs improvement !!!
            #   !!! Anyone have suggestions on presentation?
            #
            chargeFormat    = "{0}{1[0]}% ({1[1][0]:d}h {1[1][1]:02d}m)"
            powerFormat     = "{0}{1[0]:.0f} mA; {1[1]:.3f} V"
            statusFormat    = "{0}{1[0]} ({1[1]:.1f} 'C)"
            chargeBakFormat = "{0}{1[0]}%"
            powerBakFormat  = "{0}{1[1]:.3f} V"
            statusBakFormat = "{0}{1[0]}"

            self.charge = BatteryLabel(self.window, chargeFormat,   _("Charge: "), chargeBakFormat)
            self.power  = BatteryLabel(self.window, powerFormat,    _("Power info: "), powerBakFormat)
            self.status = BatteryLabel(self.window, statusFormat,   _("Status: "), statusBakFormat)

            self.fastChargeToggle = FastChargeBox(self.window)

            # pack labels into the labels box
            labels_box = elementary.Box(self.window)
            labels_box.size_hint_weight_set(1.0, 0.0)
            labels_box.size_hint_align_set(-1.0, 0.0)
            labels_box.show()

            labels_box.pack_end(self.charge)
            labels_box.pack_end(self.power)
            labels_box.pack_end(self.status)

            # pack labels_box and update button into a box
            status_box = elementary.Box(self.window)
            status_box.horizontal_set(True)
            status_box.size_hint_weight_set(1.0, 0.0)
            status_box.size_hint_align_set(-1.0, 0.0)
            status_box.show()

            update_button = elementary.Button(self.window)
            update_button.size_hint_weight_set(0.0, 1.0)
            update_button.size_hint_align_set(0.0, -1.0)
            update_button._callback_add('clicked', self.doupdate)
            update_button.label_set(_("Update"))
            update_button.show()

            status_box.pack_end(labels_box)
            status_box.pack_end(update_button)

            try:
                present = int(read_file(SYSNODE['present'][0]))
            except:
                present = 0

            self.main.pack_start(status_box)
            self.main.pack_end(self.fastChargeToggle)
            if not present:
                switchbtn = elementary.Button(self.window)
                switchbtn.label_set(_('Switch to dumb battery driver'))
                switchbtn.size_hint_weight_set(1.0, 0.0)
                switchbtn.size_hint_align_set(-1.0, 0.0)
                switchbtn._callback_add('clicked', self.switchToDumb)
                self.main.pack_end(switchbtn)
                switchbtn.show()

            # update the labels
            self.update()

            self.main.show()

        except dbus.exceptions.DBusException, e:

            print "DBus is not running", repr(e)
            self.error()

        return self.main
