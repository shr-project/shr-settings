import elementary, module, ecore
import dbus
import array
#from dbus.mainloop.glib import DBusGMainLoop

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x



class Toggle2( elementary.Toggle ):
    def setProfile_name( self, i ):
        self.profile_name = i

    def getProfile_name( self ):
        return self.profile_name




class Profile(module.AbstractModule):
    name = _("Profile")

    def error(self, result):
        print "async dbus error"

    def callback(self, result):
        if self.stan!="":
            print "guiUpdate"
            nr=0
            for i in self.profiles:
                if i==result:
                    self.togglegroup.value_set(nr)
                nr=nr+1

        if self.guiUpdates:
            ecore.timer_add( 1.3, self.guiUpdate)



    def guiUpdate(self):
        if self.stan!="":
            print "guiUpdate"
            self.stan = self.pr_iface.GetProfile(reply_handler=self.callback,error_handler=self.error)
        #TODO - change to dbus event listener


    def toggle0bt_Click(self, obj, event, *args, **kargs):
#        print "1"
#        profile = obj.getProfile_name()
#        print "2"
#        s = obj.state_get()
#        print "3"
        #print "action on:"+str(profile)+" state:"+str(state)

#        print "act 0"
#        if s == 1:
#            print "act 1"
        self.pr_iface.SetProfile(self.profiles[self.togglegroup.value_get()],reply_handler=self.nothing,error_handler=self.error)
#            print "act 2"
            
    def nothing(self):
        print "nothing called"

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
        la.label_set(_("Current profile:"))
        la.show()
        boxh.pack_start(la)"""
        self.cur = elementary.Label(self.window)
        if self.stan=="":
            self.cur.label_set("dbus error")
            self.cur.show()
            boxh.pack_end(self.cur)

        if self.dbus_status == 1:
            self.toggleArray = []
            self.profiles = self.pr_iface.GetProfiles()
            profilenr = 0
            for i in self.profiles:
                toggle0 = elementary.Radio(self.window)
                toggle0.label_set(i)
                toggle0.size_hint_align_set(-1.0, 0.0)
                toggle0._callback_add("changed", self.toggle0bt_Click)
                if i==self.stan:
                    stanTog = 1
                else:
                    stanTog = 0
                #toggle0.state_set( stanTog )
                toggle0.state_value_set(profilenr)
                profilenr=profilenr+1
                if profilenr==1:
                    self.togglegroup=toggle0
                else:
                    toggle0.group_add(self.togglegroup)
                toggle0.show()
                boxh.pack_start(toggle0)
                self.toggleArray.append(toggle0)
            self.guiUpdate()
                
        return boxh


    def stopUpdate(self):
        print "Profile desktructor"
        self.guiUpdates = 0


