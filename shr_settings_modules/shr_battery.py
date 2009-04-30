
import module, os, re, sys, elementary, ecore
import threading

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class BatteryLabel(elementary.Label):
    """
    Generic class for the labels used below
    """

    def __init__(self,win):
        super(BatteryLabel, self).__init__(win)
        self.size_hint_align_set(-1.0, 0.0)
        self.show()


class Battery(module.AbstractModule):
    name = _("Battery")

    def sectotime(self, sec):
        minutes = int(str(sec/60))
        hours = int(str(minutes/60))
        min = minutes - (hours*60)
        if min<10:
            strmin="0"+str(min)
        else:
            strmin=str(min)
        return str(hours) + " h " + strmin + " min"

    def refreshAct(self):
#        self.apml.label_set( os.popen("apm").read().replace("\n","") )
        vol = "1234"
        temp = "1234"
        cur = "1234"
        cap = "1234"
        time = "1234"
        rate = ""

        try:
            vol =  float(os.popen("cat /sys/class/power_sup*ly/bat*/voltage_now").readline())/(1000*1000)
            temp = float(os.popen("cat /sys/class/power_sup*ly/bat*/temp").readline())/10
            cur =  int(os.popen("cat /sys/class/power_su*ply/bat*/current_now").readline())/1000
            sta = os.popen("cat /sys/class/power_su*ply/bat*/status").readline().strip()
            cap = os.popen("cat /sys/class/power_su*ply/bat*/capacity").readline().strip()
            if sta=="Charging":
                time = int(os.popen("cat /sys/class/power_su*ply/bat*/time_to_full_now").readline())
                try:
                    rate = int(os.popen("cat /sys/class/i2c-adapter/i2c-0/0-0073/pcf50633-mbc/chg_curlim").readline())
                    rate = " (%s mA)" % rate
                except:
                    pass
            else:
                time = int(os.popen("cat /sys/class/power_su*ply/bat*/time_to_empty_now").readline())

            self.voll.label_set("{0}{1:.3f} V".format(_("Voltage: "),vol))
            self.templ.label_set("{0}{1:.1f} 'C".format(_("Temperature: "),temp))
            self.curl.label_set("{0}{1} mA".format(_("Current: "),str(cur)))
            self.stal.label_set("{0}{1}".format(_("Status: "),sta+rate))
            self.capl.label_set("{0}{1} %".format(_("Capacity: "),cap))
            self.timel.label_set("{0}{1}".format(_("Remaining time: "),self.sectotime(int(time))))


            #FIXME: if it does not work.. we should try again?
            if self.guiUpdate:
                return 1
            else:
                return 0

        except:
            #FIXME: if it does not work.. should we try again?
            return 1
            print ":("

    def createView(self):

        self.guiUpdate = 1

        # create the box
        self.box = elementary.Box(self.window)
        self.box.size_hint_weight_set(1.0, 1.0)
        self.box.size_hint_align_set(-1.0, 0.0)

        # create labels
        self.stal   = BatteryLabel(self.window)
        self.voll   = BatteryLabel(self.window)
        self.templ  = BatteryLabel(self.window)
        self.curl   = BatteryLabel(self.window)
        self.capl   = BatteryLabel(self.window)
        self.timel  = BatteryLabel(self.window)

        # pack labels into the box
        self.box.pack_start(self.stal)
        self.box.pack_start(self.voll)
        self.box.pack_start(self.templ)
        self.box.pack_start(self.curl)
        self.box.pack_start(self.capl)
        self.box.pack_start(self.timel)

        self.box.show()

        self.refreshAct()
            #   Is there no way to use dbus?
            #   Timers seem to lock up the GUI
            #               - Cameron
        ecore.timer_add( 10, self.refreshAct)

        return self.box

    def stopUpdate(self):
        print "Bat desktructor"
        self.guiUpdate = 0

