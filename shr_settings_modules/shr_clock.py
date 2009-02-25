import elementary
import module
import os
import datetime, time
import dbus

#changelog:
# 1.01.2009 - hiciu - cleaning code

#kurde, raz spacja, raz tabulator.. wtf?
#tak to jest, jak sie pisze kod na freerunnrze ;) - dos

def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)

class Clock(module.AbstractModule):
    name = "Time"
    section = "Other"

    def clockset(self, obj, event):
	    if self.editable:
                now = datetime.datetime.now()
                #TODO - set time by fso dbus request
                os.system("date "+str(now.month).zfill(2)+str(now.day).zfill(2)+str(self.cl.time_get()[0]).zfill(2)+str(self.cl.time_get()[1]).zfill(2)+str(now.year)+"."+str(self.cl.time_get()[2]).zfill(2))
                self.cl.edit_set(False)
                obj.label_set("Set time")
                self.editable = False
            else:
                self.cl.edit_set(True)
                obj.label_set("OK")
                self.editable = True

    def createView(self):
        self.editable = False
        box0 = elementary.Box(self.window)
        self.cl = elementary.Clock(self.window)
        self.cl.show_seconds_set(True)
        box0.pack_end(self.cl)
        self.cl.show()
        self.but = elementary.Button(self.window)
        self.but.label_set("Set time")
        self.but.size_hint_align_set(-1.0, 0.0)
        box0.pack_end(self.but)
        self.but.clicked = self.clockset
        self.but.show()

        return box0
