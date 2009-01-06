import elementary, module, os, dbus

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
    
    def power_handle(self, obj, event):
        #if obj.state_get():
#        wifipower = self.wifi.GetPower()
#        self.wifi.SetPower(not(wifipower))
	if self.wifi.GetPower()==obj.state_get():
		return 0
	self.wifi.SetPower(obj.state_get())
#        obj.state_set(not(wifipower))


    def createView(self):
        try:
                self.wifi = getDbusObject (self.dbus, "org.freesmartphone.odeviced", "/org/freesmartphone/Device/PowerControl/WiFi", "org.freesmartphone.Device.PowerControl")
        except:
            label = elementary.Label(self.window)
            label.label_set("can't connect to dbus")
            return label

        box1 = elementary.Box(self.window)
        toggle0 = elementary.Toggle(self.window)
        toggle0.label_set("WiFi radio:")
        toggle0.size_hint_align_set(-1.0, 0.0)
        toggle0.states_labels_set("On","Off")
        toggle0.changed = self.power_handle
        box1.pack_start(toggle0)
        toggle0.state_set(self.wifi.GetPower())
        toggle0.show()
        
        return box1
