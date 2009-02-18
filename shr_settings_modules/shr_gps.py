import elementary, module, os, dbus

def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)

class Gps(module.AbstractModule):
    name = "GPS"

    def isEnabled(self):
        return True
    
    def power_handle(self, obj, event):
       if self.gps.GetResourceState("GPS")==obj.state_get():
            return 0
       if obj.state_get(): 
           self.gps.SetResourcePolicy("GPS","enabled")
           obj.state_set(1)
       else:
           self.gps.SetResourcePolicy("GPS","disabled")
           obj.state_set(0)


    def res_handle(self, obj, event):
        if obj.state_get():
            self.gps.SetResourcePolicy("GPS","auto")
            self.toggle1.hide()
        else:
            if self.gps.GetResourceState("GPS"):
                self.gps.SetResourcePolicy("GPS","enabled")
                self.toggle1.state_set(1)
            else:
                self.gps.SetResourcePolicy("GPS","disabled")
                self.toggle1.state_set(0)
            self.toggle1.show()

    def createView(self):
        try:
            self.gps = getDbusObject (self.dbus, "org.freesmartphone.ousaged", "/org/freesmartphone/Usage", "org.freesmartphone.Usage") 
        except:
            label = elementary.Label(self.window)
            label.label_set("can't connect to dbus")
            return label

        box1 = elementary.Box(self.window)

        toggle0 = elementary.Toggle(self.window)
        toggle0.label_set("GPS radio policy:")
        toggle0.size_hint_align_set(-1.0, 0.0)
        toggle0.states_labels_set("Auto","Manual")
        toggle0.changed = self.res_handle
        box1.pack_start(toggle0)
        toggle0.show()

        self.toggle1 = elementary.Toggle(self.window)
        self.toggle1.label_set("Radio:")
        self.toggle1.size_hint_align_set(-1.0, 0.0)
        self.toggle1.states_labels_set("On","Off")
        self.toggle1.changed = self.power_handle
        box1.pack_end(self.toggle1)


        if self.gps.GetResourcePolicy("GPS")=="auto":
            toggle0.state_set(1)
            self.toggle1.hide()
        else:
            toggle0.state_set(0)
            self.toggle1.show()
        self.toggle1.state_set(self.gps.GetResourceState("GPS"))
        
        return box1