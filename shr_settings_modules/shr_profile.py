import elementary, module, ecore
import dbus
import array
from dbus.mainloop.glib import DBusGMainLoop


class Toggle2( elementary.Toggle ):
    def setProfile_name( self, i ):
        self.profile_name = i

    def getProfile_name( self ):
        return self.profile_name




class Profile(module.AbstractModule):
    name = "Profile"


    def defbt_click(self, obj, event):
        if self.stan!="":
            self.pr_iface.SetProfile('default')
            self.cur.label_set('default')

    def silbt_click(self, obj, event):
        if self.stan!="":
            self.pr_iface.SetProfile('silent')
            self.cur.label_set('silent')


    def guiUpdate(self):
        if self.stan!="":
            print "guiUpdate"
            self.stan = self.pr_iface.GetProfile()
            for obj in self.toggleArray:
                toggle_name = obj.getProfile_name()
                if toggle_name==self.stan:
                    set = 1
                else:
                    set = 0
                obj.state_set(set)
        if self.guiUpdates:
            ecore.timer_add( 1.3, self.guiUpdate)


    def toggle0bt_Click(self, obj, event):
        print "1"
        profile = obj.getProfile_name()
        print "2"
        s = obj.state_get()
        print "3"
        #print "action on:"+str(profile)+" state:"+str(state)

        print "act 0"
        if s == 1:
            print "act 1"
            self.pr_iface.SetProfile(profile)
            print "act 2"
            

    def createView(self):
        self.guiUpdates = 1
        self.stan = ""
        
        try:
            #DBusGMainLoop(set_as_default=True)
            #bus = dbus.SystemBus()
            pr_device_obj = self.dbus.get_object( "org.freesmartphone.opreferencesd", "/org/freesmartphone/Preferences" )
            self.pr_iface = dbus.Interface(pr_device_obj, "org.freesmartphone.Preferences" )
            self.stan = self.pr_iface.GetProfile()
            self.dbus_status = 1
        except:
            self.dbus_status = 0
            print "can't connect to dbus :/"


        boxh = elementary.Box(self.window)
        boxh.size_hint_weight_set(1.0, -1.0)

        """la = elementary.Label(self.window)
        la.label_set("Current profile:")
        la.show()
        boxh.pack_start(la)"""
        self.cur = elementary.Label(self.window)
        if self.stan=="":
            self.cur.label_set("dbus error")
            self.cur.show()
            boxh.pack_end(self.cur)

        if self.dbus_status == 1:
            self.toggleArray = []
            profiles = self.pr_iface.GetProfiles()
            for i in profiles:
                toggle0 = Toggle2(self.window)
                toggle0.label_set(i)
                toggle0.setProfile_name(i)
                toggle0.size_hint_align_set(-1.0, 0.0)
                toggle0.states_labels_set("On","Off")
                toggle0.changed = self.toggle0bt_Click
                if i==self.stan:
                    stanTog = 1
                else:
                    stanTog = 0
                toggle0.state_set( stanTog )
                toggle0.show()
                boxh.pack_start(toggle0)
                self.toggleArray.append(toggle0)
            self.guiUpdate()
                
        """
        defbt = elementary.Button(self.window)
        defbt.clicked = self.defbt_click
        defbt.label_set("default" )
        defbt.size_hint_align_set(-1.0, 0.0)
        defbt.show()
        boxh.pack_end(defbt)

        silbt = elementary.Button(self.window)
        silbt.clicked = self.silbt_click
        silbt.label_set("silent" )
        silbt.size_hint_align_set(-1.0, 0.0)
        silbt.show()
        boxh.pack_end(silbt)
        """

       

        return boxh


    def stopUpdate(self):
        print "Profile desktructor"
        self.guiUpdates = 0


