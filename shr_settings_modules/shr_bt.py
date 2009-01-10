import time
import module
import elementary, ecore
import os

"""
- gta01
/sys/devices/platform/s3c2410-i2c/i2c-adapter/i2c-0/0-0008/neo1973-pm-bt.0/
- gta02
/sys/devices/platform/s3c2440-i2c/i2c-adapter/i2c-0/0-0073/neo1973-pm-bt.0/

"""
btModels = [ \
"/sys/devices/platform/s3c2410-i2c/i2c-adapter/i2c-0/0-0008/neo1973-pm-bt.0",
"/sys/devices/platform/s3c2440-i2c/i2c-adapter/i2c-0/0-0073/neo1973-pm-bt.0",
"/sys/bus/platform/devices/neo1973-pm-bt.0"]

class BtMstateContener:
    def __init__(self):
        self.model = ""
        self.state = 0
        self.getModel()

    def getModel(self):
        return self.model

    def getModel(self):
        try:
            open(btModels[0]+"/power_on", "r")
            self.model = "gta01"
        except:
            print "BT BtMstateContener getModel [inf] not gta01"

        try:
            open(btModels[1]+"/power_on", "r")
            self.model = "gta02"
        except:
            print "BT BtMstateContener getModel [inf] not gta02"

        try:
            open(btModels[1]+"/power_on", "r")
            self.model = "gta02"
        except:
            print "BT BtMstateContener getModel [inf] not gta02"

        print "BT BtMstateContener getModel [inf] device is ? "+self.model

    def getService(self):
        ser = os.popen("ps -A | grep [h]ci").read().replace("\n","")
        if ser != "":
            return 1
        else:
            return 0

    def getServiceObex(self):
        ser = os.popen("ps -A | grep [o]bexftpd").read().replace("\n","")
        if ser != "":
            return 1
        else:
            return 0
        

    def setPower(self, b ):
        print "BT BtMstateContener setPower [inf] "+self.model
        if b==0:
            print "BT BtMstateContener setPower [inf] turn off bt by sysfs"
            #print "stop /etc/init.d/bluetooth"
            #os.system("/etc/init.d/bluetooth stop")
            #time.sleep(1)

            print "power_on"
            os.system("echo "+str(b)+" > "+btModels[2]+"/power_on")

            print "sleep"
            time.sleep(1)
        
            print "reset"
            os.system("echo 1 > "+btModels[2]+"/reset")
            

        else:
            print "BT BtMstateContener setPower [inf] turn on bt by sysfs"
            print "power_on"
            os.system("echo "+str(b)+" > "+btModels[2]+"/power_on")

            if self.model == "gta02":
                print "sleep"
                time.sleep(1)

                print "reset"
                os.system("echo 0 > "+btModels[2]+"/reset")

            #time.sleep(1)
            #print "start /etc/init.d/bluetooth"
            #os.system("/etc/init.d/bluetooth start")

        

    def getPower(self):
        if self.model=="gta01":
            f0 = open(btModels[2]+"/power_on", "r")
        elif self.model=="gta02":
            f0 = open(btModels[2]+"/power_on", "r")
        elif self.model=="":
            return self.state

        while f0:
            line = f0.readline()
            if not line:
                f0.close()
                break
            else:
                self.state = int(line)
        return self.state

    def setVisibility(self, b):
        if b:
            print "hciconfig hci0 piscan"
            os.system("hciconfig hci0 up")
            os.system("hciconfig hci0 piscan")
        else:
            print "hciconfig hci0 pscan"
            os.system("hciconfig hci0 up")
            os.system("hciconfig hci0 pscan")

    def getVisibility(self):
        piscan = os.popen("hciconfig dev")
        self.visible = -1
        self.iscan = 0
        self.pscan = 0

        s = 1
        while s:
            line = piscan.readline()
            if not line:
                break
            else:
                s = line.split(" ")
                self.visible = 0
                for i in s:
                    if i=="ISCAN":
                        self.iscan = 1
                    elif i=="PSCAN":
                        self.pscan = 1

        if self.iscan==1:
            return 1
        return 0
        


class Bt(module.AbstractModule):
    name = "Bluetooth"
    section = "Connectivity"

    def BtmodGUIupdate(self):
        s = self.btmc.getPower()
        v = self.btmc.getVisibility()
        ser = self.btmc.getService()
        obex = self.btmc.getServiceObex()
        print "BT BtmodGUIupdate [info] power:"+str(s)+"; visibility:"+str(v)+" services:"+str(ser)+" obxeftpd:"+str(obex)
        if s == 1:
            self.toggle1.show()
            if v:
                self.toggle1.state_set(1)
            else:
                self.toggle1.state_set(0)

            if ser:
                self.toggle2.state_set(1)
            else:
                self.toggle2.state_set(0)

            self.toggle0.state_set( 1 )

            self.toggle2.show()
        else:
            self.toggle1.hide()
            self.toggle2.hide()
            self.toggle0.state_set( 0 )

        self.toggle3.state_set( obex )

        if self.guiUpdate:
            ecore.timer_add( 5.4, self.BtmodGUIupdate)

    def toggle0Click(self, obj, event, *args, **kargs):
#        if self.btmc.getPower():
	if self.btmc.getPower()==obj.state_get():
		return 0
	if obj.state_get()==0:
            print "Bt toggle0Click BT set OFF"
            self.btmc.setPower( 0 )
            self.toggle1.hide()
        else:
            print "Bt toggle0Click BT set ON"
            self.btmc.setPower( 1 )
            self.toggle1.show()

        
        

    def toggle1Click(self, obj, event, *args, **kargs):
        print "BT toggle1Cleck set Visibility"
        if self.btmc.getVisibility()==obj.state_get():
            return 0
    #        s = self.btmc.getVisibility()
    #        print str(s)
    #        if s:
        if obj.state_get()==0:
            print "Turn off"
            self.btmc.setVisibility(0)
        else:
            print "Turn on"
            self.btmc.setVisibility(1)

    def toggle2Click(self, obj, event, *args, **kargs):
        print "BT toggle2Cleck set on off spi hci servis"
        if self.btmc.getService()==obj.state_get():
            return 0
    #        s = self.btmc.getVisibility()
    #        print str(s)
    #        if s:
        if obj.state_get()==0:
            print "Turn off"
            os.system("/etc/init.d/bluetooth stop")
        else:
            print "Turn on"
            os.system("/etc/init.d/bluetooth start")


    def toggle3Click(self, obj, event, *args, **kargs):
        print "BT toggle3Cleck set on off obexftpd servis"
        if self.btmc.getServiceObex()==obj.state_get():
            return 0
    #        s = self.btmc.getVisibility()
    #        print str(s)
    #        if s:
        if obj.state_get()==0:
            print "Turn off"
            os.system("killall -9 obexftpd")
        else:
            print "Turn on"
            os.system("cd /tmp && obexftpd -b -c /tmp &")


    def createView(self):
        self.guiUpdate = 1
        self.btmc = BtMstateContener()
        vi = self.btmc.getVisibility()

        box1 = elementary.Box(self.window)

        if self.btmc.getModel=="":
            label =elementary.Label(self.window)
            label.label_set("can't find file in sysfs")
            label.size_hint_align_set(-1.0, 0.0)
            label.show()
            box1.pack_start(label)
        else:
            self.toggle0 = elementary.Toggle(self.window)
            self.toggle0.label_set("Bluetooth radio:")
            self.toggle0.size_hint_align_set(-1.0, 0.0)
            self.toggle0.states_labels_set("On","Off")
            box1.pack_start(self.toggle0)
            self.toggle0.show()
            self.toggle0.changed = self.toggle0Click

            self.toggle1 = elementary.Toggle(self.window)
            self.toggle1.label_set("Visibility")
            self.toggle1.size_hint_align_set(-1.0, 0.0)
            self.toggle1.states_labels_set("On","Off")
            self.toggle1.state_set(vi)
            box1.pack_end(self.toggle1)
            self.toggle1.changed = self.toggle1Click


            
            self.toggle2 = elementary.Toggle(self.window)
            self.toggle2.label_set("Services (spi, hci):")
            self.toggle2.size_hint_align_set(-1.0, 0.0)
            self.toggle2.states_labels_set("On","Off")
            box1.pack_end(self.toggle2)
            self.toggle2.changed = self.toggle2Click


            self.toggle3 = elementary.Toggle(self.window)
            self.toggle3.label_set("Services (ObexFTPd):")
            self.toggle3.size_hint_align_set(-1.0, 0.0)
            self.toggle3.states_labels_set("On","Off")
            if os.popen("obexftpd --help | grep [O]bexFTPd").read().replace("\n","")!="":
                self.toggle3.show()
                box1.pack_end(self.toggle3)
                self.toggle3.changed = self.toggle3Click
            else:
                print "No obexftpd found :/ toggle disable"




        self.BtmodGUIupdate()

        return box1

    def stopUpdate(self):
        print "BT desktructor"
        self.guiUpdate = 0
