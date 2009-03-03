import elementary
import module

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
    
    #enter your apn, login && password here:
    apn, login, password = "INTERNET", "INTERNET", "INTERNET"
    
    #a little helper..
    def newLabel(self, labelText):
    	obj = elementary.Label(self.window)
    	obj.label_set(labelText)
    	obj.show()
    	self.main.pack_end(obj)
    	return obj
    
    def createView(self):
    	#gui
    	self.main = elementary.Box(self.window)
    	
        #connection status..
        self.laConnection = self.newLabel(_("Connection status: UNKNOWN"))
        self.laTransferred = self.newLabel(_("Transferred bytes (RX/TX): UNKNOWN"))
                
        #there is no elementary.Entry so far..
        #here is: LOGIN, PASSWORD, APN
        self.laLogin = self.newLabel(_("Your login: '%s'" % self.login))
        #should this one be hidden? "Your password: '********'"?
        self.laPassword = self.newLabel(_("Your password: '%s'") % self.password)
        self.laApn = self.newLabel(_("Your APN: '%s'") % self.apn)
        
        #CONNECT / DISCONNECT button
        self.btConnectDisconnect = elementary.Button(self.window)
        self.btConnectDisconnect.label_set(_("UNKNOWN"))
        self.btConnectDisconnect.show()
        self.main.pack_end(self.btConnectDisconnect)

        return self.main
