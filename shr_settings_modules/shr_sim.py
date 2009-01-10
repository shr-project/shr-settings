import time, dbus
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

class SimMstateContener:
    def __init__(self, bus):
        self.state = 0
        try:
            gsm_sim_obj = bus.get_object( 'org.freesmartphone.ogsmd', '/org/freesmartphone/GSM/Device' )
            self.gsm_sim_iface = dbus.Interface(gsm_sim_obj, 'org.freesmartphone.GSM.SIM')
            #self.gsm_sim_iface.getSimInfo()
            self.state = 1
            print "SimMstateContener can connect to dbus"
        except:
            self.state = 0
            print "SimMstateContener can't connect to dbus"

    def getDbusState(self):
        return self.state

    def getSimInfo(self):
        if self.state == 0:
            return 0
        else:
            return self.gsm_sim_iface.GetSimInfo()

    def ListPhonebooks(self):
        if self.state == 0:
            return 0
        else:
            return self.gsm_sim_iface.ListPhonebooks()

    def GetPhonebookInfo(self, a):
        if self.state == 0:
            return 0
        else:
            return self.gsm_sim_iface.GetPhonebookInfo(a)


    def GetMessagebookInfo(self):
        if self.state == 0:
            return 0
        else:
            return self.gsm_sim_iface.GetMessagebookInfo()


    def MessageBookClean(self):
        messageMax = self.GetMessagebookInfo()['last']
        print "MessageBookClean max: "+str(messageMax)
        for i in range(1, (messageMax+1), 1):
            print "remove id: "+str(i)
            try:
                self.gsm_sim_iface.DeleteMessage(i)
            except:
                pass
        print "DONE"

   

    

class Sim(module.AbstractModule):
    name = "SIM"
    section = "Connectivity"

    

    def cleanMessageBookClick(self, obj, event):
        self.simmc.MessageBookClean()


    def createView(self):
        self.guiUpdate = 1
        
        self.simmc = SimMstateContener( self.dbus )
        print "3"
        print "sim dbus"+str(self.simmc.getDbusState())
        print "4"

        box1 = elementary.Box(self.window)
        print "5"

        if self.simmc.getDbusState==0:
            label =elementary.Label(self.window)
            label.label_set("can't find file in sysfs")
            label.size_hint_align_set(-1.0, 0.0)
            label.show()
            box1.pack_start(label)
        else:
            simInfo = self.simmc.getSimInfo()
            frameInfo = elementary.Frame(self.window)
            frameInfo.label_set("SIM information:")
            box1.pack_end(frameInfo)
            frameInfo.size_hint_align_set(-1.0, 0.0)
            frameInfo.show()
            
            boxInfo = elementary.Box(self.window)
            frameInfo.content_set(boxInfo)
            
            for s in simInfo:
                if s != "subscriber_numbers":
                    boxS = elementary.Box(self.window)
                    boxS.horizontal_set(True)
                    boxS.size_hint_align_set(-1.0, 0.0)
                    boxS.show()

                    labelN =elementary.Label(self.window)
                    labelN.label_set(str(s)+":")
                    labelN.size_hint_align_set(-1.0, -1.0)
                    labelN.size_hint_weight_set(1.0, 1.0)
                    labelN.show()
                    boxS.pack_start(labelN)

                    labelV =elementary.Label(self.window)
                    labelV.size_hint_align_set(-1.0, 0.0)
                    labelV.label_set( str( simInfo[s] ) )
                    labelV.show()
                    boxS.pack_end(labelV)

                    boxInfo.pack_start( boxS )

            phoneBooks = self.simmc.ListPhonebooks()
            for b in phoneBooks:
                #frame
                frameBook = elementary.Frame(self.window)
                frameBook.label_set("Book "+b+":")
                box1.pack_end(frameBook)
                frameBook.size_hint_align_set(-1.0, 0.0)
                frameBook.show()

                boxBook = elementary.Box(self.window)
                boxBook.show()
                frameBook.content_set(boxBook)


                print "phoneBookInfo: "+b
                phoneBookInfo = self.simmc.GetPhonebookInfo( b )
                for i in phoneBookInfo:
                    print "phoneBookInfo: "+b+"; "+i
                    #info state
                    boxS = elementary.Box(self.window)
                    boxS.horizontal_set(True)
                    boxS.size_hint_align_set(-1.0, 0.0)
                    boxS.show()

                    labelN =elementary.Label(self.window)
                    try:
                        labelN.label_set(str(i)+":")
                    except:
                        pass
                    labelN.size_hint_align_set(-1.0, -1.0)
                    labelN.size_hint_weight_set(1.0, 1.0)
                    labelN.show()
                    boxS.pack_start(labelN)

                    labelV =elementary.Label(self.window)
                    labelV.size_hint_align_set(-1.0, 0.0)
                    try:
                        labelV.label_set( str( phoneBookInfo[i] ) )
                    except:
                        pass
                    labelV.show()
                    boxS.pack_end(labelV)

                    boxBook.pack_start( boxS )

            print "phoneBookInfo --------- DONE"

            """
            # actions
            boxS = elementary.Box(self.window)
            boxS.horizontal_set(True)
            boxS.size_hint_align_set(-1.0, 0.0)
            boxS.show()

            # backup TODO
            backupbt = elementary.Button(self.window)
            #backupbt.clicked = self.destroy2
            backupbt.label_set("backup")
            backupbt.size_hint_align_set(-1.0, 0.0)
            backupbt.show()
            boxS.pack_end(backupbt)

            # clear TODO
            cleanbt = elementary.Button(self.window)
            #backupbt.clicked = self.destroy2
            cleanbt.label_set("clean")
            cleanbt.size_hint_align_set(-1.0, 0.0)
            cleanbt.show()
            boxS.pack_end(cleanbt)

            boxBook.pack_end( boxS )
            """
            print "1"
            # message book info

            messBookInfo = self.simmc.GetMessagebookInfo()
            print "2"
            frameBook = elementary.Frame(self.window)
            print "3"
            frameBook.label_set("Message book:")
            box1.pack_end(frameBook)
            frameBook.size_hint_align_set(-1.0, 0.0)
            frameBook.show()

            boxBook = elementary.Box(self.window)
            boxBook.show()
            frameBook.content_set(boxBook)
            
            for m in messBookInfo:
                boxS = elementary.Box(self.window)
                boxS.horizontal_set(True)
                boxS.size_hint_align_set(-1.0, 0.0)
                boxS.show()

                labelN =elementary.Label(self.window)
                labelN.label_set(str(m)+":")
                labelN.size_hint_align_set(-1.0, -1.0)
                labelN.size_hint_weight_set(1.0, 1.0)
                labelN.show()
                boxS.pack_start(labelN)

                labelV =elementary.Label(self.window)
                labelV.size_hint_align_set(-1.0, 0.0)
                labelV.label_set( str( messBookInfo[m] ) )
                labelV.show()
                boxS.pack_end(labelV)

                boxBook.pack_start( boxS )


            # actions
            boxS = elementary.Box(self.window)
            boxS.horizontal_set(True)
            boxS.size_hint_align_set(-1.0, 0.0)
            boxS.show()
            """
            # backup TODO
            backupbt = elementary.Button(self.window)
            #backupbt.clicked = self.destroy2
            backupbt.label_set("backup")
            backupbt.size_hint_align_set(-1.0, 0.0)
            backupbt.show()
            boxS.pack_end(backupbt)
            """
            # clear TODO
            cleanbt = elementary.Button(self.window)
            cleanbt.clicked = self.cleanMessageBookClick
            cleanbt.label_set("clean")
            cleanbt.size_hint_align_set(-1.0, 0.0)
            cleanbt.show()
            boxS.pack_end(cleanbt)

            boxBook.pack_end( boxS )
            

            



        return box1

    def stopUpdate(self):
        print "SIM desktructor"
        self.guiUpdate = 0
