import elementary
import module
from helper import ElmEntryBox,ElmLabelBox

import dbus

import os
import pickle

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


__author__ = "hiciu, dos, Toaster`"

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

def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)




class Gprs(module.AbstractModule):
    name = _("GPRS settings")
    section = _("networking")

    wizard_name=_("GPRS connection data")
    wizard_description=_("Please enter your GPRS login and password. You can also skip this step.")

    # persistent data file, until something is available in opreferencesd
    persistData = '/etc/shr-settings/gprs.pickle'

    def error(self):
        label = elementary.Label(self.window)
        label.label_set(_("Couldn't connect to FSO or phonefsod"))
        label.show()
        self.main.pack_start(label)

    def getEntryData(self):
        """
        Returns clean values for the text entries
        """
        apn         = self.entryAPN.entry_get().replace("<br>","")
        login       = self.entryLogin.entry_get().replace("<br>","")
        password    = self.entryPassword.entry_get().replace("<br>","")

        return apn,login,password

    def loadConnectionData(self):
        """
        Read pickled connection data from the persistData file
        """
        # defaults
        apn = login = password = "internet"

        if os.path.exists(self.persistData):
            pickleFile = open(self.persistData, "r")
            apn, login, password = pickle.load(pickleFile)

        return apn, login, password

    def saveConnectionData(self):
        """
        Write pickled connection data to the persistData file.
        `/etc/shr-settings/` is assumed to exist
        """

        # Assume connection was made, therefore is good data, so pickle it
        pickleData = self.getEntryData()
        pickleFile = open(self.persistData, "w")
        pickle.dump(pickleData,pickleFile)
        pickleFile.close()

        apn, login, password = self.getEntryData()
        self.phonefso.SetPdpCredentials(apn, login, password)

    def wizardClose(self):
        self.saveConnectionData()
	return True

    def dbusnothing(self):
        return 0

    def dbuserror(self, error):
        return 0

    def connect(self, obj, *args, **kargs):
        apn, login, password = self.getEntryData()
        self.dbusObj.SetCredentials(apn, login, password)
        self.dbusObj.ActivateContext(
            reply_handler = self.dbusnothing,
            error_handler = self.dbuserror)
        return 0

    def disconnect(self, obj, *args, **kargs):
        self.dbusObj.DeactivateContext(reply_handler = self.dbusnothing, error_handler = self.dbuserror)
        return 0

    def nothing(self, obj, *args, **kargs):
        print "nothing called"
        return 0

    def updateStatus(self, id = None, gprs_status = None, *args, **kargs):
        if id == None:
            self.dbusObj.GetContextStatus(reply_handler = self.updateStatus, error_handler=self.dbuserror)
        else:
            if gprs_status == None or gprs_status == {}:
                gprs_status = id.lower()
            if gprs_status == 'release' or gprs_status == 'released':
                status=_("disconnected")
                self.btConnectDisconnect.label_set(_("Connect"))
                self.btConnectDisconnect._callback_add('clicked',self.connect)
            elif gprs_status == 'active':
                status=_("connected")
                self.btConnectDisconnect.label_set(_("Disconnect"))
                self.btConnectDisconnect._callback_add('clicked', self.disconnect)
                # Since connection was successful, save login data
                self.saveConnectionData()
            elif gprs_status == 'outgoing':
                status=_("connecting")
                self.btConnectDisconnect.label_set(_("Disconnect"))
                self.btConnectDisconnect._callback_add('clicked', self.disconnect)
            elif gprs_status == 'incoming':
                status=_("incoming")
                self.btConnectDisconnect.label_set(_("Connect"))
                self.btConnectDisconnect._callback_add('clicked', self.connect)
            elif gprs_status == 'held':
                status=_("held")
                self.btConnectDisconnect.label_set(_("Disconnect"))
                self.btConnectDisconnect._callback_add('clicked', self.disconnect)
            else:
                status=_("UNKNOWN")+" ("+str(id) + ' ' + str(gprs_status)+")"
                self.btConnectDisconnect.label_set(_("UNKNOWN"))
                self.btConnectDisconnect._callback_add('clicked', self.nothing)
            self.labelStatus.label_set(status)
            return True

    def stopUpdate(self):
        self.signal.remove()

    def createView(self):
        """
        Create main box then try loading dbus, if successful, load the rest,
        on exception load error message
        """

        self.main = elementary.Box(self.window)

        try:
            self.phonefso = getDbusObject(self.dbus,
                    "org.shr.phonefso",
                    "/org/shr/phonefso/Usage",
                    "org.shr.phonefso.Usage")

            if not self.wizard:
                # GSM.PDP DBus interface
                self.dbusObj = getDbusObject(self.dbus,
                    "org.freesmartphone.ogsmd",
                    "/org/freesmartphone/GSM/Device",
                    "org.freesmartphone.GSM.PDP")

                # GSM.PDP.ContextStatus(isa{sv}) DBus Signal
                self.signal = self.dbusObj.connect_to_signal("ContextStatus", self.updateStatus)

            # Check for and load persisted data
            self.apn, self.login, self.password = self.loadConnectionData()

            # connection_name, apn, login, password entries
            self.entryAPN       = ElmEntryBox(self.window, _("Your APN: "), self.apn)
            self.entryLogin     = ElmEntryBox(self.window, _("Your login: "), self.login)
            self.entryPassword  = ElmEntryBox(self.window, _("Your password: "), self.password)
            if not self.wizard:
                self.labelStatus    = ElmLabelBox(self.window, _("Connection status: "),_("UNKNOWN"))
                #self.laTransferred = self.newLabel(_("Transferred bytes (RX/TX): UNKNOWN"))

            self.main.pack_end(self.entryAPN)
            self.main.pack_end(self.entryLogin)
            self.main.pack_end(self.entryPassword)
            if not self.wizard:
                self.main.pack_end(self.labelStatus)

                #CONNECT / DISCONNECT button
                self.btConnectDisconnect = elementary.Button(self.window)
                self.btConnectDisconnect.label_set(_("UNKNOWN"))
                self.btConnectDisconnect.show()
                self.btConnectDisconnect.size_hint_align_set(-1.0, 0.0)
                self.main.pack_end(self.btConnectDisconnect)

                self.updateStatus()

        except:
            # This needs expansion, error reason etc...
            self.error()

        self.main.show()

        return self.main
