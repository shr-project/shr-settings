import module, elementary
import dbus

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x

"""
source
- freesmartphone framework
http://www.freesmartphone.org/index.php/Main_Page
- dbus
http://74.125.77.132/search?q=cache:lrCoc3DSa0gJ:www.freesmartphone.org/index.php/Tutorials/GSM_python+python+dbus+%22org.freesmartphone.ogsmd%22&hl=pl&ct=clnk&cd=3&gl=pl&client=firefox-a
- target :)
http://shr-project.org/trac/wiki/Draft:SHRSettingsApp
"""

class Button2( elementary.Button ):
    def set_opeNr( self, mOpeNr ):
        self.mOpeNr = mOpeNr

    def get_opeNr( self ):
        return self.mOpeNr

class GSMstateContener:
    def __init__(self, bus):
        self.dbus_state = 0
        try:
            gsm_device_obj = bus.get_object( 'org.freesmartphone.ogsmd', '/org/freesmartphone/GSM/Device' )
            self.gsm_network_iface = dbus.Interface(gsm_device_obj, 'org.freesmartphone.GSM.Network')
            self.gsm_device_iface = dbus.Interface(gsm_device_obj, 'org.freesmartphone.GSM.Device')

            opkd_device_obj = bus.get_object( 'org.shr.ophonekitd.Usage', '/org/shr/ophonekitd/Usage' )
            self.opkd_device_iface = dbus.Interface(opkd_device_obj, 'org.shr.ophonekitd.Usage')
            #test
            #self.gsm_device_iface.GetAntennaPower()
            #test end
            self.dbus_state = 1
        except:
            self.dbus_state = 0
            print "GSM GSMstateContener [error] can't connect to dbus"

    def dbus_getState(self):
        return self.dbus_state

    def gsmdevice_getAntennaPower(self):
        if self.dbus_state==0:
            return 0
        else:
            try:
                tr = self.opkd_device_iface.GetResourceState('GSM')
            except:
                tr = 0
            return tr

    def gsmdevice_setAntennaPower(self, b):
        if self.dbus_state==1:
            if b:
                self.opkd_device_iface.RequestResource('GSM')
                try:
                    self.gsm_device_iface.SetAntennaPower(True)
                except:
                    pass
            else:
                self.opkd_device_iface.ReleaseResource('GSM')

    def gsmdevice_GetInfo(self):
        if self.dbus_state==1:
            return self.gsm_device_iface.GetInfo()

    def gsmnetwork_ListProviders(self, handler, error):
        if self.dbus_state==1:
            return self.gsm_network_iface.ListProviders(reply_handler=handler, error_handler=error)

    def gsmnetwork_Register(self):
        if self.dbus_state==1:
            self.gsm_network_iface.Register()

    def gsmnetwork_RegisterWithProvider(self, b, error):
        if self.dbus_state==1:
            try:
                self.gsm_network_iface.RegisterWithProvider(b)
                return 1
            except dbus.exceptions.DBusException, e:
                error(e)
                return 0

    def gsmnetwork_GetStatus(self):
        if self.dbus_state==1:
            return self.gsm_network_iface.GetStatus()

    def gsmnetwork_GetStatus_providerName(self):
        if self.dbus_state==1:
            struct = self.gsmnetwork_GetStatus()
            return str( struct[u'provider'])

    def gsmnetwork_GetStatusOperatorName(self):
        if self.dbus_state==1:
            stat = self.gsmnetwork_GetStatus()
            try:
                return str(stat[u'provider'])
            except:
                return ""
        else:
            return ""


class Gsm(module.AbstractModule):
    name = _("GSM settings")

    def goto_settingsbtClick(self, obj, event, *args, **kargs):
        try:
            self.wininfo.hide()
            self.wininfo.delete()
        except:
            pass
        try:
            self.winope.hide()
            self.winope.delete()
        except:
            pass


    def operatorSelectError(self, e):
        print "Error happened: " + str(e)
        self.status = elementary.Label(self.winope)
        self.opefr.content_set(self.status)
        self.status.label_set(_("Could not connect to network"))
        self.status.show()

    def operatorAutomatic(self, obj, event, *args, **kwargs):
        self.gsmsc.gsmnetwork_Register()
        self.winope.hide()
        self.winope.delete()

    def operatorSelect(self, obj, event, *args, **kargs):
        #os.popen("echo \"gsmnetwork.RegisterWithProvider( "+obj.get_opeNr()+" )\" | cli-framework", "r");
        print "GSM operatorSelect [info] ["+str(obj.get_opeNr())+"]"
        if self.gsmsc.gsmnetwork_RegisterWithProvider( obj.get_opeNr(), self.operatorSelectError ):
            self.winope.hide()
            self.winope.delete()
            print "clik"

    def nothing(self,obj,event, *args, **kargs):
        print "nothing called"

    def operatorsList(self, obj, event, *args, **kargs):
        obj.label_set(_("Please wait..."))
        obj.clicked=self.nothing
        self.gsmsc.gsmnetwork_ListProviders(self.operatorsList2, self.operatorsListError)        

    def operatorsListError(self, why):
        print "operatorsListError! " + str(why)
        self.opebt.label_set(_("Operators"))
        self.opebt.clicked=self.operatorsList
        return 0

    def operatorsList2(self,l):
        print "GSM operatorsList [inf]"
        self.opebt.label_set(_("Operators"))
        self.opebt.clicked=self.operatorsList

        self.winope = elementary.Window("listProviders", elementary.ELM_WIN_BASIC)
        self.winope.title_set(_("List Providers"))
        self.winope.autodel_set(True)

        self.bg = elementary.Background(self.winope)
        self.winope.resize_object_add(self.bg)
        self.bg.size_hint_weight_set(1.0, 1.0)
        self.bg.show()

        box0 = elementary.Box(self.winope)
        box0.size_hint_weight_set(1.0, 1.0)
        self.winope.resize_object_add(box0)
        box0.show()

        self.opefr = elementary.Frame(self.winope)
        self.opefr.label_set(_("List Providers"))
        self.opefr.size_hint_align_set(-1.0, 0.0)
        box0.pack_end(self.opefr)
        self.opefr.show()

        sc = elementary.Scroller(self.winope)
        sc.size_hint_weight_set(1.0, 1.0)
        sc.size_hint_align_set(-1.0, -1.0)
        sc.bounce_set(0,1)
        box0.pack_end(sc)
        sc.show()

        cancelbt = elementary.Button(self.winope)
        cancelbt.clicked = self.goto_settingsbtClick
        cancelbt.label_set(_("Cancel"))
        cancelbt.size_hint_align_set(-1.0, 0.0)
        cancelbt.show()
        box0.pack_end(cancelbt)

        box1 = elementary.Box(self.winope)
        box1.size_hint_weight_set(1.0, -1.0)
        sc.content_set(box1)
        box1.show()

        opeautobt = elementary.Button(self.winope)
        opeautobt.label_set(_("Automatic"))
        opeautobt.clicked = self.operatorAutomatic
        opeautobt.size_hint_align_set(-1.0, 0.0)
        opeautobt.show()
        box1.pack_end(opeautobt)

        print "GSM operatorsList [inf] get list"
        #l = self.gsmsc.gsmnetwork_ListProviders()
        for i in l:
            print "GSM operatorsList [inf] add operator to list - "+str(i[2])+" - "+str(i[1])+" - "+str(i[0])
            opeAvbt = Button2(self.winope)
            if str(i[1])=="current":
                add = _(" [current]")
            elif str(i[1])=="forbidden":
                add = _(" [forbidden]")
            else:
                add = "";
            opeAvbt.label_set( str(i[2])+add )
            opeAvbt.set_opeNr( i[0] )
            opeAvbt.clicked = self.operatorSelect
            opeAvbt.size_hint_align_set(-1.0, 0.0)
            opeAvbt.show()
            box1.pack_end(opeAvbt)

        self.winope.show()

    def GSMmodGUIupdate(self):
        self.ap = self.gsmsc.gsmdevice_getAntennaPower()

        self.toggle0.state_set( self.ap )
        if self.ap:
            self.opebt.show()
            self.toggle0.state_set( self.ap )
        else:
            self.opebt.hide()
            self.toggle0.state_set( self.ap )

#        self.opela.label_set( self.gsmsc.gsmnetwork_GetStatusOperatorName() )

    def toggle0bt(self, obj, event, *args, **kargs):
        if self.gsmsc.gsmdevice_getAntennaPower()==obj.state_get():
		return 0
	if obj.state_get()==0:
            print "GSM set off"
            self.gsmsc.gsmdevice_setAntennaPower(0)
            self.opebt.hide()
            self.infobt.hide()
#            obj.state_set( 0 )
        else:
            print "GSM set on"
            self.gsmsc.gsmdevice_setAntennaPower(1)
            self.opebt.show()
            self.infobt.show()
#            obj.state_set( 1 )

        try:
            del self.thread
            print "GSM GSMmodGUIupdate [inf] kill operator search thread"
        except:
            print "GSM GSMmodGUIupdate [inf] search thread not present"

        self.GSMmodGUIupdate()

    def informationbt(self, obj, event, *args, **kargs):
        print "GSM infobt [inf]"
        self.wininfo = elementary.Window("deviceInfo", elementary.ELM_WIN_BASIC)
        self.wininfo.title_set(_("GSM modem information"))
        self.wininfo.autodel_set(True)

        self.bginfo = elementary.Background(self.wininfo)
        self.wininfo.resize_object_add(self.bginfo)
        self.bginfo.size_hint_weight_set(1.0, 1.0)
        self.bginfo.show()

        box0 = elementary.Box(self.wininfo)
        box0.size_hint_weight_set(1.0, 1.0)
        self.wininfo.resize_object_add(box0)
        box0.show()

        fr = elementary.Frame(self.wininfo)
        fr.label_set(_("GSM modem information"))
        fr.size_hint_align_set(-1.0, 0.0)
        box0.pack_end(fr)
        fr.show()

        sc = elementary.Scroller(self.wininfo)
        sc.size_hint_weight_set(1.0, 1.0)
        sc.size_hint_align_set(-1.0, -1.0)
        sc.bounce_set(0,1)
        box0.pack_end(sc)
        sc.show()

        cancelbt = elementary.Button(self.wininfo)
        cancelbt.clicked = self.goto_settingsbtClick
        cancelbt.label_set(_("Cancel"))
        cancelbt.size_hint_align_set(-1.0, 0.0)
        cancelbt.show()
        box0.pack_end(cancelbt)

        box1 = elementary.Box(self.wininfo)
        box1.size_hint_weight_set(1.0, -1.0)
        sc.content_set(box1)
        box1.show()

        i = self.gsmsc.gsmnetwork_GetStatus()
        for b in i:
            fo = elementary.Frame(self.wininfo)
            fo.label_set( str(b) )
            fo.size_hint_align_set(-1.0, 0.0)
            fo.show()
            box1.pack_end(fo)

            lab = elementary.Label(self.wininfo)
            lab.label_set( str(i[b]) )
            lab.size_hint_align_set(-1.0, 0.0)
            lab.show()
            fo.content_set( lab )

        i = self.gsmsc.gsmdevice_GetInfo()
        for b in i:
            fo = elementary.Frame(self.wininfo)
            fo.label_set( str(b) )
            fo.size_hint_align_set(-1.0, 0.0)
            fo.show()
            box1.pack_end(fo)

            lab = elementary.Label(self.wininfo)
            lab.label_set( str(i[b]) )
            lab.size_hint_align_set(-1.0, 0.0)
            lab.show()
            fo.content_set( lab )



        self.wininfo.show()


    def createView(self):
        
        self.gsmsc = GSMstateContener(self.dbus)
        
        self.box1 = elementary.Box(self.window)

        try:
            self.toggle0 = elementary.Toggle(self.window)
            self.toggle0.label_set(_("GSM antenna:"))
            self.toggle0.size_hint_align_set(-1.0, 0.0)
            self.toggle0.states_labels_set("On","Off")
            self.toggle0.show()
            self.box1.pack_start(self.toggle0)

            self.opebt = elementary.Button(self.window)
            self.opebt.clicked = self.operatorsList
            self.opebt.label_set(_("Operators"))
            self.opebt.size_hint_align_set(-1.0, 0.0)
            self.box1.pack_end(self.opebt)

            self.infobt = elementary.Button(self.window)
            self.infobt.clicked = self.informationbt
            self.infobt.label_set(_("Modem information"))
            self.infobt.size_hint_align_set(-1.0, 0.0)
            self.infobt.show()
            self.box1.pack_end(self.infobt)

            self.toggle0.changed = self.toggle0bt

            self.GSMmodGUIupdate()
        except:
            print "GSM view [info] can't connect to dbus"
            errlab = elementary.Label(self.window)
            errlab.label_set(_("can't connect to dbus"))
            errlab.size_hint_align_set(-1.0, 0.0)
            errlab.show()
            self.box1.pack_end( errlab )


        return self.box1



