
import module, os, re, sys, elementary, ecore
import threading
import dbus
from dbus.mainloop.glib import DBusGMainLoop


class Button2( elementary.Button ):
    def set_extData( self, i, name, labelObj, value ):
        self.i = i
        self.name = name
        self.labelObj = labelObj
        self.value = value

    def get_i( self ):
        return self.i

    def get_name(self):
        return self.name

    def get_labelObj(self):
        return self.labelObj

    def get_value(self):
        return self.value

    def set_value(self, i):
        self.value = i

class Timeouts(module.AbstractModule):
    name = "Timeouts"


    #----------------------------------------------------------------------------#
    def getObject( self, busname, objectpath ):
    #----------------------------------------------------------------------------#
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        return bus.get_object( busname, objectpath, follow_name_owner_changes=True )

    #----------------------------------------------------------------------------#
    def getInterface( self, busname, objectpath, interface ):
    #----------------------------------------------------------------------------#
        proxy = self.getObject( busname, objectpath )
        return dbus.Interface( proxy, interface)

    #----------------------------------------------------------------------------#
    def getObjectsForInterface( self, interface ):
    #----------------------------------------------------------------------------#
        framework = getObject( "org.freesmartphone.frameworkd", "/org/freesmartphone/Framework" )

        paths = framework.ListObjectsByInterface( interface, dbus_interface="org.freesmartphone.Framework" )
        result = {}
        for path in paths:
            result[str(path)] = self.getInterface( "org.freesmartphone.frameworkd", path, interface )
        return result

    
    def addbtClick(self, obj, event):
        self.timeouts = self.devidle.GetTimeouts()
        label = obj.get_labelObj()
        addFor = int(obj.get_i())
        name = obj.get_name()
        stat = int(self.timeouts[str(name)])

        if self.dbus_state == 1 and (stat >= 0 or addFor>0):
            self.devidle.SetTimeout( name, int(stat+addFor) )
            obj.set_value(int(stat+addFor))
            label.label_set( str( stat+addFor ) )




    

    def createView(self):
        
        self.box1 = elementary.Box(self.window)


        boxOp = elementary.Box(self.window)
        boxOp.size_hint_weight_set(1.0, 1.0)
        boxOp.size_hint_align_set(-1.0, 0.0)


        self.dbus_state = 0
        try:
            self.devidle = self.getInterface( \
                "org.freesmartphone.odeviced",
                "/org/freesmartphone/Device/IdleNotifier/0",
                "org.freesmartphone.Device.IdleNotifier" \
                )
            self.timeouts = self.devidle.GetTimeouts()
            self.dbus_state = 1
        except:
            self.dbus_state = 0

        if self.dbus_state == 0:
            stal = elementary.Label(self.window)
            stal.size_hint_align_set(-1.0, 0.0)
            stal.label_set("can't connect to dbus")
            stal.show()
            self.box1.pack_start(stal)
        else:

            for i in self.timeouts:
                if i != "avake" :
                    boxS = elementary.Box(self.window)
                    boxS.horizontal_set(True)
                    boxS.size_hint_align_set(-1.0, 0.5)
                    boxS.size_hint_weight_set(1.0, 1.0)


                    namel = elementary.Label(self.window)
                    namel.size_hint_align_set(-1.0, -1.0)
                    namel.size_hint_weight_set(1.0, 1.0)
                    namel.label_set(str(i).replace("_"," ")+": ")
                    namel.show()
                    boxS.pack_start(namel)


                    value = self.timeouts[i]

                    add = ""
                    for s in range(len(str(value)), 5, 1):
                        add = add + " "

                    valuel = elementary.Label(self.window)
                    valuel.size_hint_align_set(0.5, 0.0)
                    valuel.label_set(add+str(self.timeouts[i]))
                    valuel.show()

                    minbt = Button2(self.window)
                    minbt.set_extData( -1, str(i), valuel, value )
                    minbt.clicked = self.addbtClick
                    minbt.label_set("[ - ]")
                    minbt.size_hint_align_set(-1.0, 0.0)
                    minbt.show()

                    addbt = Button2(self.window)
                    addbt.set_extData( 1, str(i), valuel, value )
                    addbt.clicked = self.addbtClick
                    addbt.label_set("[ + ]")
                    addbt.size_hint_align_set(-1.0, 0.0)
                    addbt.show()


                    boxS.pack_end(minbt)
                    boxS.pack_end(valuel)
                    boxS.pack_end(addbt)



                boxS.show()
                self.box1.pack_start(boxS)
            
        
        return self.box1



