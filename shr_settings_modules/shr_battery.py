
import module, os, re, sys, elementary, ecore
import threading

class Battery(module.AbstractModule):
    name = "Battery"

    def refreshAct(self):
#        self.apml.label_set( os.popen("apm").read().replace("\n","") )
        vol = "1234"
        temp = "1234"
        cur = "1234"
        cap = "1234"
        time = "1234"

        try:
            vol =  os.popen("cat /sys/class/power_sup*ly/bat*/voltage_now").readline().replace("\n","")
            temp = os.popen("cat /sys/class/power_sup*ly/bat*/temp").readline().replace("\n","")
            cur =  int(os.popen("cat /sys/class/power_su*ply/bat*/current_now").readline().replace("\n",""))/1000
            sta = os.popen("cat /sys/class/power_su*ply/bat*/status").readline().replace("\n","")
            cap = os.popen("cat /sys/class/power_su*ply/bat*/capacity").readline().replace("\n","")

            self.voll.label_set("Voltage: "+str(vol)[0]+"."+str(vol)[1]+str(vol)[2]+str(vol)[3]+" V")
            self.templ.label_set("Temperature: "+str(temp)[0]+str(temp)[1]+"."+str(temp)[2]+" 'C")
            self.curl.label_set("Current: "+str(cur)+" mA")
            self.stal.label_set("Status: "+sta)
            self.capl.label_set("Capacity: "+cap+" %")

            #FIXME: if it does not work.. we should try again?
            if self.guiUpdate:
                ecore.timer_add( 2.3, self.refreshAct)

        except:
            print ":("

    def createView(self):
        self.guiUpdate = 1
        self.box1 = elementary.Box(self.window)


        box1p = elementary.Box(self.window)
        box1p.size_hint_weight_set(1.0, 1.0)
        box1p.size_hint_align_set(-1.0, 0.0)

        self.stal = elementary.Label(self.window)
    	self.stal.size_hint_align_set(-1.0, 0.0)
    	self.stal.show()
    	box1p.pack_start(self.stal)

        self.voll = elementary.Label(self.window)
    	self.voll.size_hint_align_set(-1.0, 0.0)
    	self.voll.show()
    	box1p.pack_start(self.voll)

        self.templ = elementary.Label(self.window)
    	self.templ.size_hint_align_set(-1.0, 0.0)
    	self.templ.show()
    	box1p.pack_start(self.templ)

        self.curl = elementary.Label(self.window)
    	self.curl.size_hint_align_set(-1.0, 0.0)
    	self.curl.show()
    	box1p.pack_start(self.curl)

        self.capl = elementary.Label(self.window)
    	self.capl.size_hint_align_set(-1.0, 0.0)
    	self.capl.show()
    	box1p.pack_start(self.capl)

        box1p.show()
        self.box1.pack_end(box1p)


        self.refreshAct()

        return self.box1

    def stopUpdate(self):
        print "Bat desktructor"
        self.guiUpdate = 0

