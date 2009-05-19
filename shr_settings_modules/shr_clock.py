import elementary
import module
import os
import datetime, time
import dbus

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


#changelog:
# 1.01.2009 - hiciu - cleaning code

#kurde, raz spacja, raz tabulator.. wtf?
#tak to jest, jak sie pisze kod na freerunnrze ;) - dos

def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)

class Clock(module.AbstractModule):
    name = _("Time settings")
    section = _("Other")

    def clockset(self, obj, event, *args, **kargs):
	    if self.editable:
                d = datetime.date.today()
                t = datetime.time(self.cl.time_get()[0], self.cl.time_get()[1], self.cl.time_get()[2])
                dt = datetime.datetime.combine(d,t)
                
                clock = getDbusObject( self.dbus, "org.freesmartphone.odeviced", "/org/freesmartphone/Device/RealTimeClock/rtc0", "org.freesmartphone.Device.RealTimeClock" )
                clock.SetCurrentTime(int(dt.strftime("%s")))
                
                self.cl.edit_set(False)
                obj.label_set(_("Set time"))
                self.editable = False
            else:
                self.cl.edit_set(True)
                obj.label_set(_("OK"))
                self.editable = True

    def createView(self):
        self.editable = False
        box0 = elementary.Box(self.window)
        self.cl = elementary.Clock(self.window)
        #self.cl.show_seconds_set(True)
        box0.pack_end(self.cl)
        self.cl.show()
        self.but = elementary.Button(self.window)
        self.but.label_set(_("Set time"))
        self.but.size_hint_align_set(-1.0, 0.0)
        box0.pack_end(self.but)
        self.but.clicked = self.clockset
        self.but.show()

        return box0
