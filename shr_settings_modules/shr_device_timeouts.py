import module, os, re, sys, elementary, ecore
import threading
import dbus
from dbus.mainloop.glib import DBusGMainLoop


class ValueLabel( elementary.Label ):
    """ Label that displays current timeout """
    def __init__(self, win):
        self._value = None
        super(ValueLabel, self).__init__(win)

    def get_value(self):
        return self._value

    def set_value(self, val):
         self.label_set(str(val))
         self._value = val


class AddButton( elementary.Button ):
    """ Button that add/substracts from the value label """
    def set_extData( self, addStep, name, labelObj):
        self._addStep = addStep
        self.name = name
        self._labelObj = labelObj

    def get_addStep( self ):
        return self._addStep

    def get_name(self):
        return self.name

    def get_labelObj(self):
        return self._labelObj


class Timeouts(module.AbstractModule):
    name = "Timeouts"


    #----------------------------------------------------------------------------#
    def getObject( self, busname, objectpath ):
    #----------------------------------------------------------------------------#
        #DBusGMainLoop(set_as_default=True)
        #bus = dbus.SystemBus()
        return self.dbus.get_object( busname, objectpath, follow_name_owner_changes=True )

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


    #----------------------------------------------------------------------------#   
    def addbtClick(self, obj, event):
    #----------------------------------------------------------------------------#
        """ Callback function when +-[1,10] timeout buttons have been pressed """
        label   = obj.get_labelObj()
        cur_val = label.get_value()
        addFor  = obj.get_addStep()
        name    = obj.get_name()
        new_val = max(-1, cur_val + addFor)

        if self.dbus_state == 1:
            self.devidle.SetTimeout( name, new_val )
            label.set_value(new_val)


    
    #----------------------------------------------------------------------------#   
    def createView(self):
    #----------------------------------------------------------------------------#   
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
                if not str(i) in ("awake","busy","none"):
                    boxS = elementary.Box(self.window)
                    boxS.horizontal_set(True)
                    boxS.size_hint_align_set(-1.0, 0.5)
                    boxS.size_hint_weight_set(1.0, 1.0)


                    namel = elementary.Label(self.window)
                    namel.size_hint_align_set(-1.0, -1.0)
                    namel.size_hint_weight_set(1.0, 1.0)
                    namel.label_set(str(i).replace("_"," "))
                    namel.show()
                    boxS.pack_start(namel)

                    cur_val = int(self.timeouts[i])
                    valuel  = ValueLabel(self.window)
                    valuel.size_hint_align_set(0.5, 0.0)
                    valuel.label_set(str(cur_val))
                    valuel.set_value(cur_val) #implicitely sets label too
                    valuel.show()

                    # the -10 button
                    mintenbt = AddButton(self.window)
                    mintenbt.set_extData( -10, str(i), valuel)
                    mintenbt.clicked = self.addbtClick
                    mintenbt.label_set("-10")
                    mintenbt.size_hint_align_set(-1.0, 0.0)
                    mintenbt.show()

                    # the -1 button
                    minonebt = AddButton(self.window)
                    minonebt.set_extData( -1, str(i), valuel) 
                    minonebt.clicked = self.addbtClick
                    minonebt.label_set("-1")
                    minonebt.size_hint_align_set(-1.0, 0.0)
                    minonebt.show()

                    # the +1 button
                    addonebt = AddButton(self.window)
                    addonebt.set_extData( 1, str(i), valuel)
                    addonebt.clicked = self.addbtClick
                    addonebt.label_set("+1")
                    addonebt.size_hint_align_set(-1.0, 0.0)
                    addonebt.show()


                    # the +10 button
                    addtenbt = AddButton(self.window)
                    addtenbt.set_extData( 10, str(i), valuel) 
                    addtenbt.clicked = self.addbtClick
                    addtenbt.label_set("+10")
                    addtenbt.size_hint_align_set(-1.0, 0.0)
                    addtenbt.show()


                    boxS.pack_end(mintenbt)
                    boxS.pack_end(minonebt)
                    boxS.pack_end(valuel)
                    boxS.pack_end(addonebt)
                    boxS.pack_end(addtenbt)

                    # add the "<name> [-]val[+]" box
                    boxS.show()
                    self.box1.pack_start(boxS)
            
        
        return self.box1
