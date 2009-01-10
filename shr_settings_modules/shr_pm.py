
import module, os, re, sys, elementary, ecore
import threading
import dbus

class Pm(module.AbstractModule):
    name = "Power"

    def poweroffbtClick(self, obj, event):
        iface = self.get_usage_iface()
        if iface:
            iface.Shutdown()
        else:
            print "Shutdown by dbus cmd error"

    def restartbtClick(self, obj, event):
        iface = self.get_usage_iface()
        if iface:
            iface.Reboot()
        else:
            print "Reboot by dbus cmd error"

    def get_usage_iface(self):
        try:
            usage_obj = self.dbus.get_object( 'org.freesmartphone.ousaged', '/org/freesmartphone/Usage' )
            return dbus.Interface(usage_obj, 'org.freesmartphone.Usage')
            
            #self.usage_iface.Suspend()
            
        except:
            print "suspend by dbus cmd error"
            return 0


        

    def suspendbtClick(self, obj, event):
        iface = self.get_usage_iface()

        if os.popen("cat /proc/cpuinfo | grep [G]TA01").read() == "GTA01\n":
            print "suspend for GTA01"
            os.system("/etc/init.d/fso-gsmd stop")
            time.sleep(0)


            if iface:
                iface.Suspend()
            else:
                print "suspend by dbus cmd error2"

            time.sleep(0)
            os.system("/etc/init.d/fso-gsmd start")
        else:
            if iface:
                iface.Suspend()
            else:
                print "suspend by dbus cmd error2"
            
    def refreshAct(self):
        self.apml.label_set( os.popen("apm").read().replace("\n","") )
        vol = "1234"
        temp = "1234"
        cur = "1234"
        cap = "100"

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


        boxOp = elementary.Box(self.window)
        boxOp.size_hint_weight_set(1.0, 1.0)
        boxOp.size_hint_align_set(-1.0, 0.0)

        self.apml = elementary.Label(self.window)
    	self.apml.size_hint_align_set(-1.0, 0.0)
    	self.apml.show()
    	boxOp.pack_start(self.apml)

        fo = elementary.Frame(self.window)
        fo.label_set( "apm:" )
        fo.size_hint_align_set(-1.0, 0.0)
        fo.show()
        fo.content_set( boxOp )

        boxOp.show()
        self.box1.pack_end(fo)



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

        fo = elementary.Frame(self.window)
        fo.label_set( "battery:" )
        fo.size_hint_align_set(-1.0, 0.0)
        fo.show()
        fo.content_set( box1p )

        box1p.show()
        self.box1.pack_end(fo)


        self.refreshAct()



        box2p = elementary.Box(self.window)
        box2p.size_hint_weight_set(1.0, 1.0)
        box2p.size_hint_align_set(-1.0, 0.0)

        poweroffbt = elementary.Button(self.window)
        poweroffbt.clicked = self.suspendbtClick
        poweroffbt.label_set("power off")
        poweroffbt.size_hint_align_set(-1.0, 0.0)
        poweroffbt.show()
        box2p.pack_end(poweroffbt)

        restartbt = elementary.Button(self.window)
        restartbt.clicked = self.restartbtClick
        restartbt.label_set("restart")
        restartbt.size_hint_align_set(-1.0, 0.0)
        restartbt.show()
        box2p.pack_end(restartbt)

        suspendbt = elementary.Button(self.window)
        suspendbt.clicked = self.suspendbtClick
        suspendbt.label_set("suspend")
        suspendbt.size_hint_align_set(-1.0, 0.0)
        suspendbt.show()
        box2p.pack_end(suspendbt)


        fo = elementary.Frame(self.window)
        fo.label_set( "actions:" )
        fo.size_hint_align_set(-1.0, 0.0)
        fo.show()
        fo.content_set( box2p )

        box2p.show()
        self.box1.pack_end(fo)


        
        return self.box1

    def stopUpdate(self):
        print "PM desktructor"
        self.guiUpdate = 0

