import module, elementary, dbus

def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)

class Usb(module.AbstractModule):
    name = "USB"

    def mode_handle(self, obj, event):
	if self.usbhost.GetPower()!=obj.state_get():
		return 0
        usbpower=obj.state_get()
	#usbpower = self.usbhost.GetPower()
        if usbpower:
            self.toggle1.label_set("Device mode:")
            self.toggle1.states_labels_set("Ethernet","Mass storage")
            self.toggle1.state_set(1)
	    self.usbhost.SetPower(False)
        else:
            self.toggle1.label_set("Host powered:")
            self.toggle1.states_labels_set("Yes","No")
            self.toggle1.state_set(1)
	    self.usbhost.SetPower(True)
	#obj.state_set(usbpower)

    def isEnabled(self):
	try:
            self.usbhost = getDbusObject (self.dbus, "org.freesmartphone.odeviced", "/org/freesmartphone/Device/PowerControl/UsbHost","org.freesmartphone.Device.PowerControl")
	    self.usbpower = self.usbhost.GetPower()
	    return 1
	except:
	    return 0

    def createView(self):
        
        box1 = elementary.Box(self.window)
        self.toggle0 = elementary.Toggle(self.window)
        self.toggle0.label_set("USB mode:")
        self.toggle0.size_hint_align_set(-1.0, 0.0)
        self.toggle0.states_labels_set("Device","Host")
	self.toggle0.state_set(1)
        self.toggle0.changed = self.mode_handle
	self.toggle0.state_set(not(self.usbpower))
        box1.pack_start(self.toggle0)
        self.toggle0.show()

	self.toggle1 = elementary.Toggle(self.window)
	self.toggle1.label_set("Device mode:")
	self.toggle1.size_hint_align_set(-1.0, 0.0)
        self.toggle1.states_labels_set("Ethernet","Mass storage")
	self.toggle1.state_set(1)
        box1.pack_end(self.toggle1)
        self.toggle1.show()

	if self.usbpower:
            self.toggle1.label_set("Host powered:")
            self.toggle1.states_labels_set("Yes","No")
            self.toggle1.state_set(1)

        return box1
        
