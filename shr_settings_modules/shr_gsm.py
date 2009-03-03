
import module, os, re, sys, elementary
import threading
import dbus
from dbus.mainloop.glib import DBusGMainLoop

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
                tr = self.gsm_device_iface.GetAntennaPower()
            except:
                tr = 0
            return tr
    def gsmdevice_setAntennaPower(self, b):
        if self.dbus_state==1:
            self.gsm_device_iface.SetAntennaPower(b)

    def gsmdevice_GetInfo(self):
        if self.dbus_state==1:
            return self.gsm_device_iface.GetInfo()

    def gsmnetwork_ListProviders(self, handler, error):
        if self.dbus_state==1:
            return self.gsm_network_iface.ListProviders(reply_handler=handler, error_handler=error)

    def gsmnetwork_RegisterWithProvider(self, b):
        if self.dbus_state==1:
            self.gsm_network_iface.RegisterWithProvider(b)

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
    name = _("GSM")

    def goto_settingsbtClick(self, obj, event, *args, **kargs):
        self.wininfo.hide()
        self.winope.hide()

    def destroyDebug(self, obj, event, *args, **kargs):
        self.windeb.hide()

    def clean_ophonekitd_log(self, obj, event, *args, **kargs):
        os.system("echo \"\" >  /var/log/ophonekitd.log")
        self.destroyDebug(self, obj, event, *args, **kargs) 
       
    def view_ophonekitd_log(self, obj, event, *args, **kargs):        
        print "ophonekitd log"
        self.windeb = elementary.Window("ophonekitdLog", elementary.ELM_WIN_BASIC )
        self.windeb.title_set(_("ophonekitd log"))
        self.windeb.autodel_set(True)
        self.bgdeb = elementary.Background(self.windeb)
        self.windeb.resize_object_add(self.bgdeb)
        self.bgdeb.size_hint_weight_set(1.0, 1.0)
        self.bgdeb.show()

        box0 = elementary.Box(self.windeb)
        box0.size_hint_weight_set(1.0, 1.0)
        self.windeb.resize_object_add(box0)
        box0.show()

        fr = elementary.Frame(self.windeb)
        fr.label_set(_("ophonekitd log"))
        fr.size_hint_align_set(-1.0, 0.0)
        box0.pack_end(fr)
        fr.show()

        sc = elementary.Scroller(self.windeb)
        sc.size_hint_weight_set(1.0, 1.0)
        sc.size_hint_align_set(-1.0, -1.0)
        box0.pack_end(sc)
        sc.show()

        cleanbt = elementary.Button(self.windeb)
        cleanbt.clicked = self.clean_ophonekitd_log   
        cleanbt.label_set(_("Clean"))
        cleanbt.size_hint_align_set(-1.0, 0.0)
        cleanbt.show()
        box0.pack_end(cleanbt)

        cancelbt = elementary.Button(self.windeb)
        cancelbt.clicked = self.destroyDebug
        cancelbt.label_set(_("Close"))
        cancelbt.size_hint_align_set(-1.0, 0.0)
        cancelbt.show()
        box0.pack_end(cancelbt)

        box1 = elementary.Box(self.windeb)
        box1.size_hint_weight_set(1.0, -1.0)
        sc.content_set(box1)
        box1.show()

        self.windeb.show()
        

        c = open( "/var/log/ophonekitd.log", "r" )
        while 1:
            line = c.readline().replace("\n","")
            if not line:
                break
            print "line ["+line+"]"
            lb = elementary.Label(self.windeb)
            lb.label_set(line)
            box1.pack_end(lb)
            lb.show()


    def operatorSelect(self, obj, event, *args, **kargs):
        #os.popen("echo \"gsmnetwork.RegisterWithProvider( "+obj.get_opeNr()+" )\" | cli-framework", "r");
        print "GSM operatorSelect [info] ["+str(obj.get_opeNr())+"]"
        self.gsmsc.gsmnetwork_RegisterWithProvider( obj.get_opeNr() )
        self.winope.hide()
        print "clik"

    def operatorsListbt(self, obj, event, *args, **kargs):
        self.thread = threading.Thread(target=self.operatorsList)
        self.thread.start()

    def nothing(self,obj,event, *args, **kargs):
        print "nothing called"

    def operatorsList(self, obj, event, *args, **kargs):
        obj.label_set(_("Please wait..."))
        obj.clicked=self.nothing
        self.gsmsc.gsmnetwork_ListProviders(self.operatorsList2, self.operatorsListError)        

    def operatorsListError(self, why):
        print "operatorsListError!"
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

        fr = elementary.Frame(self.winope)
        fr.label_set(_("List Providers"))
        fr.size_hint_align_set(-1.0, 0.0)
        box0.pack_end(fr)
        fr.show()

        sc = elementary.Scroller(self.winope)
        sc.size_hint_weight_set(1.0, 1.0)
        sc.size_hint_align_set(-1.0, -1.0)
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

        print "GSM operatorsList [inf] get list"
        #l = self.gsmsc.gsmnetwork_ListProviders()
        for i in l:
            print "GSM operatorsList [inf] add operator to list - "+str(i[2])+" - "+str(i[1])+" - "+str(i[0])
            opeAvbt = Button2(self.winope)
            if str(i[1])=="current":
                add = " [current]"
            else :
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
#            obj.state_set( 0 )
        else:
            print "GSM set on"
            self.gsmsc.gsmdevice_setAntennaPower(1)
            self.opebt.show()
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

    def start_ophonekitd_btClick(self, obj, event, *args, **kargs):
        obj.hide()
        os.system( "DISPLAY=:0 ophonekitd >> /var/log/ophonekitd.log 2>&1 &" )




    def createView(self):
        
        self.gsmsc = GSMstateContener(self.dbus)
        
        self.box1 = elementary.Box(self.window)

        try:
            print self.gsmsc.gsmnetwork_GetStatus()

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


            if os.popen("ps -A | grep [o]phonekitd").read() == "":
                boxOp = elementary.Box(self.window)
                boxOp.size_hint_weight_set(1.0, 1.0)
                boxOp.size_hint_align_set(-1.0, 0.0)

                label = elementary.Label(self.window)
                label.label_set(_("It's not running! Start it?"))
                label.size_hint_align_set(-1.0, 0.0)
                label.show()
                boxOp.pack_start( label )

                startbt = elementary.Button(self.window)
                startbt.clicked = self.start_ophonekitd_btClick
                startbt.label_set(_("Yes"))
                startbt.size_hint_align_set(-1.0, 0.0)
                startbt.show()
                boxOp.pack_end(startbt)

                logbt = elementary.Button(self.window)
                logbt.clicked = self.view_ophonekitd_log
                logbt.label_set(_("View log"))
                logbt.size_hint_align_set(-1.0, 0.0)
                logbt.show()
                boxOp.pack_end(logbt)


                fo = elementary.Frame(self.window)
                fo.label_set( _("ophonekitd") )
                fo.size_hint_align_set(-1.0, 0.0)
                fo.show()
                fo.content_set( boxOp )

                boxOp.show()
                self.box1.pack_end(fo)

        return self.box1



