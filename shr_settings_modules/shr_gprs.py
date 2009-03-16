import elementary
import module

import dbus
import ecore

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


__author__ = "hiciu"

#
# ok:
# 
# ---
#  Status polaczenia: up / down / connecting
#  Ilosc przeslanych danych: 
# ---
#  Login:
#  Haslo:
#  Apn:
# ---
#  Polacz / Rozlacz
#

class Gprs(module.AbstractModule):
    name = _("GPRS")
    section = _("networking")
    
    #enter your apn, login && password here: - TODO - store that somewhere, maybe in opreferencesd
    apn, login, password = "internet", "internet", "internet"
    
    def isEnabled(self):
        try:
            self.gsm = self.dbus.get_object( 'org.freesmartphone.ogsmd', '/org/freesmartphone/GSM/Device' )
            self.gprs = dbus.Interface( self.gsm, dbus_interface = 'org.freesmartphone.GSM.PDP' )
            return 1
        except:
            return 0

    def dbusnothing(self):
        return 0

    def connect(self, obj, event, *args, **kargs):
        self.gprs.ActivateContext(self.entryAPN.entry_get().replace("<br>",""), self.entryLogin.entry_get().replace("<br>",""), self.entryPassword.entry_get().replace("<br>","") , reply_handler = self.dbusnothing, error_handler = self.dbusnothing)
        return 0

    def disconnect(self, obj, event, *args, **kargs):
        self.gprs.DeactivateContext()
        return 0

    def nothing(self, obj, event, *args, **kargs):
        print "nothing called"
        return 0

    #a little helper..
    def newLabel(self, labelText):
    	obj = elementary.Label(self.window)
    	obj.label_set(labelText)
    	obj.show()
    	self.main.pack_end(obj)
    	return obj

    def updateStatus(self):
        gprs_status = self.gprs.GetContextStatus()
        if gprs_status == 'release':
            status=_("disconnected")
            self.btConnectDisconnect.label_set(_("Connect"))
            self.btConnectDisconnect.clicked = self.connect
        elif gprs_status == 'active':
            status=_("connected")
            self.btConnectDisconnect.label_set(_("Disconnect"))
            self.btConnectDisconnect.clicked = self.disconnect
        elif gprs_status == 'outgoing':
            status=_("connecting")
            self.btConnectDisconnect.label_set(_("Disconnect"))
            self.btConnectDisconnect.clicked = self.disconnect
        else:
            status=_("UNKNOWN")+" ("+gprs_status+")"
            self.btConnectDisconnect.label_set(_("UNKNOWN"))
            self.btConnectDisconnect.clicked = self.nothing
        self.laConnection.label_set(_("Connection status: ")+status)
        return True

    def createView(self):
    	#gui
    	self.main = elementary.Box(self.window)
    	
        self.entryAPN = elementary.Entry(self.window)
        self.entryAPN.single_line_set(True)
        self.entryAPN.entry_set(self.apn)
        self.entryAPN.show()
        self.boxAPN = elementary.Box(self.window)
        self.laAPN = elementary.Label(self.window)
        self.laAPN.label_set(_("Your APN: "))
        self.boxAPN.horizontal_set(True)
        self.boxAPN.pack_start(self.laAPN)
        self.laAPN.show()
        self.boxAPN.pack_end(self.entryAPN)
        self.boxAPN.show()
        self.main.pack_end(self.boxAPN)

        self.entryLogin = elementary.Entry(self.window)
        self.entryLogin.single_line_set(True)
        self.entryLogin.entry_set(self.login)
        self.entryLogin.show()
        self.boxLogin = elementary.Box(self.window)
        self.laLogin = elementary.Label(self.window)
        self.laLogin.label_set(_("Your login: "))
        self.boxLogin.horizontal_set(True)
        self.boxLogin.pack_start(self.laLogin)
        self.laLogin.show()
        self.boxLogin.pack_end(self.entryLogin)
        self.boxLogin.show()
        self.main.pack_end(self.boxLogin)

        self.entryPassword = elementary.Entry(self.window)
        self.entryPassword.single_line_set(True)
        self.entryPassword.entry_set(self.password)
        self.entryPassword.show()
        self.boxPassword = elementary.Box(self.window)
        self.laPassword = elementary.Label(self.window)
        self.laPassword.label_set(_("Your password: "))
        self.boxPassword.horizontal_set(True)
        self.boxPassword.pack_start(self.laPassword)
        self.laPassword.show()
        self.boxPassword.pack_end(self.entryPassword)
        self.boxPassword.show()
        self.main.pack_end(self.boxPassword)

        self.laConnection = self.newLabel(_("Connection status: ")+_("UNKNOWN"))
        #self.laTransferred = self.newLabel(_("Transferred bytes (RX/TX): UNKNOWN"))

        #CONNECT / DISCONNECT button
        self.btConnectDisconnect = elementary.Button(self.window)
        self.btConnectDisconnect.label_set(_("UNKNOWN"))
        self.btConnectDisconnect.show()
        self.btConnectDisconnect.size_hint_align_set(-1.0, 0.0)
        self.main.pack_end(self.btConnectDisconnect)
 
        self.updateStatus()

        ecore.timer_add( 1, self.updateStatus)

        return self.main
