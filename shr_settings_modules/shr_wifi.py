import elementary, module, os, dbus
try:
    from pythonwifi.iwlibs import Wireless, getNICnames
    iwlibs_present = 1
except:
    print "from pythonwifi.iwlibs import Wireless, getNICnames import error - not present"
    iwlibs_present = 0

def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)

class Wifi(module.AbstractModule):
    name = "WiFi"

    def isEnabled(self):
        if os.popen("cat /proc/cpuinfo | grep Hardware |  awk '{ print $3 }'").read()=="GTA01\n":
            return False
        else:
            return True
    
    def scan_wifi(self):

        found_aps = {}

        # search for accesspoints the interfaces can access..
        # and show list of connections to user..
        for ifname in getNICnames():

            wifi = Wireless(ifname)
            essid = wifi.getEssid()

            wifi.scan()
            for results in wifi.scan():
                enc_type = "unknown"
                # seems encryption [0x0,0x0,0x0,0x8] is WPA, [0x0,0x0,0x0,0x80] is open
                #TODO - detect WEP encryption
                enc = map(lambda x: hex(ord(x)), results.encode)

                if enc[3] == '0x80':
                    enc_type = "open"
                elif  enc[3] == '0x8':
                    enc_type = "WPA"

                found_aps[results.essid] = {'essid':results.essid, 'enc':enc_type, 'connected': (essid == results.essid)}
        return found_aps

    def power_handle(self, obj, event):
	if self.wifi.GetPower()==obj.state_get():
		return 0
	self.wifi.SetPower(obj.state_get())

    def createView(self):
        try:
                self.wifi = getDbusObject (self.dbus, "org.freesmartphone.odeviced", "/org/freesmartphone/Device/PowerControl/WiFi", "org.freesmartphone.Device.PowerControl")
        except:
            label = elementary.Label(self.window)
            label.label_set("can't connect to dbus")
            return label

        box1 = elementary.Box(self.window)
        global iwlibs_present
        if iwlibs_present == 0:
            return box1


        toggle0 = elementary.Toggle(self.window)
        toggle0.label_set("WiFi radio:")
        toggle0.size_hint_align_set(-1.0, 0.0)
        toggle0.states_labels_set("On","Off")
        toggle0.changed = self.power_handle
        box1.pack_start(toggle0)
        toggle0.state_set(self.wifi.GetPower())
        toggle0.show()
        
        try:
            networks = self.scan_wifi()
#            print networks
            for net in networks:
                btn1 = elementary.Button(self.window)
                btn1.label_set(net)
                box1.pack_end(btn1)
                btn1.show()
        except:
            label1 = elementary.Label(self.window)
            label1.label_set("unable to scan")
            box1.pack_end(label1)
            label1.show()

        return box1
