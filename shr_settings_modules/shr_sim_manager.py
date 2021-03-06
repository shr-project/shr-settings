# -*- coding: utf-8 -*-
import elementary, module
import dbus

from helper import getDbusObject

# Locale support
import gettext


try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x

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
        bt.text_set(_("SIM Manager"))

        return bt
