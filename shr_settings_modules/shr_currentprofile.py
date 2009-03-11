import elementary
import ecore
import module
import dbus
import os

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

class FileButton(elementary.Button):
    def set_filename( self, filename ):
        self.filename = filename
        self.label_set(filename)

    def get_filename( self ):
        return self.filename

class CurrentProfile(module.AbstractModule):
    name = _("Current profile")    

    def setringtone(self, obj, event, *args, **kargs):
        self.dbusobj.SetValue('ring-tone',obj.get_filename())
        self.destroy(obj, event)
        self.update()

    def destroy(self, obj, event, *args, **kargs):
        self.win.hide()

    def tonegui(self, obj, event, *args, **kargs):
        self.win = elementary.Window("change-ringtone",elementary.ELM_WIN_BASIC)
        bg = elementary.Background(self.win)
        self.win.resize_object_add(bg)
        self.win.title_set(_("Change ringtone"))
        bg.show()
        self.win.autodel_set(1)
        box = elementary.Box(self.win)
        fr = elementary.Frame(self.win)
        fr.label_set(_("Select ringtone"))
        lab = elementary.Label(self.win)
        lab.label_set(_("Ringtones are placed in /usr/share/sounds/"))
        fr.content_set(lab)
        lab.show()
        fr.show()
        fr.size_hint_align_set(-1.0, 0.0)
        box.pack_start(fr)
        scr = elementary.Scroller(self.win)
        scr.size_hint_weight_set(1.0, 1.0)
        scr.size_hint_align_set(-1.0, -1.0)
        box.pack_end(scr)
        exitbtn = elementary.Button(self.win)
        exitbtn.label_set(_("Quit"))
        exitbtn.size_hint_weight_set(1.0, 0.0)
        exitbtn.size_hint_align_set(-1.0, -1.0)
        exitbtn.clicked = self.destroy
        box.pack_end(exitbtn)
        self.win.resize_object_add(box)
        box.show()
        scr.show()
        exitbtn.show()
        self.win.show()

        box1 = elementary.Box(self.win)
        scr.content_set(box1)
        box1.size_hint_weight_set(1.0, 0.0)
        box1.show()

        for filename in os.listdir("/usr/share/sounds"):
            filebtn = FileButton(self.win)
            filebtn.set_filename(filename)
            filebtn.clicked = self.setringtone
            filebtn.size_hint_align_set(-1.0, 0.0)
            box1.pack_end(filebtn)
            filebtn.show()

    def update(self):
        keys = self.dbusobj.GetKeys()
        for i in keys:
            wyn = self.dbusobj.GetValue(i)
            try:
                self.labels[i].label_set(str(wyn))
            except:
                frame = elementary.Frame(self.window)
                frame.label_set(i)
                label = elementary.Label(self.window)
                label.label_set(str(wyn))
                self.labels[i] = label

#                if i in ['ring-tone','message-tone']:
                if i=='ring-tone':
                    table = elementary.Box(self.window)
                    table.pack_start(label)
                    table.size_hint_align_set(-1.0, 0.0)
                    table.size_hint_weight_set(1.0, 1.0)
                    label.size_hint_align_set(-1.0, 0.0)
                    tonebtn = elementary.Button(self.window)
                    tonebtn.label_set(_("change"))
                    tonebtn.clicked = self.tonegui
                    tonebtn.size_hint_align_set(-1.0, 0.0)
                    tonebtn.show()
                    table.pack_end(tonebtn)
                    frame.content_set(table)
                    table.show()
                else:   
                    frame.content_set(label)

                frame.size_hint_align_set(-1.0, 0.0)
                frame.size_hint_weight_set(1.0, 1.0)
                label.show()
                frame.show()
                self.main.pack_start(frame)
        return 1
                
    def createView(self):
        self.dbusobj = getDbusObject(self.dbus,"org.freesmartphone.opreferencesd","/org/freesmartphone/Preferences/phone","org.freesmartphone.Preferences.Service")
    	self.main = elementary.Box(self.window)
        self.labels = {}
        self.update()
        #self.dbus.add_signal_receiver(self.update, "
        ecore.timer_add( 5, self.update)
        return self.main
