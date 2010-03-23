# -*- coding: utf-8 -*-
import elementary, module
import dbus

# Locale support
import gettext


try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)


class SimManager(module.AbstractModule):
    name = _("SIM Manager")

    def startSimManager(self, obj, *args, **kargs):
        self.dbusObj = getDbusObject(self.dbus, 
                "org.shr.phoneui",
                "/org/shr/phoneui/Settings",
                "org.shr.phoneui.Settings" )
        self.dbusObj.DisplaySimManager()

    def createView(self):
        bt = elementary.Button(self.window)
        bt._callback_add('clicked', self.startSimManager)
        bt.label_set(_("SIM Manager"))

        return bt
