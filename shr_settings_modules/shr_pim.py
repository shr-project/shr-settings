import elementary, module, ecore
import dbus
import array

# Locale support
import gettext

## Testing
from functools import partial


try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)


class Pim(module.AbstractModule):
    name = _("PIM settings")

    def error(self):
        """
        Report the DBus is fsck'd
        """
        label = elementary.Label(self.window)
        label.label_set(_("DBus is borked"))
        self.main.pack_start(label)
        label.show()

    def pagerPop(self, obj, event, pager, *args, **kargs):
        pager.content_pop()

    def setAsDefault(self, obj, event, arguments, *args, **kargs):
        backend = arguments[0]
        domain = arguments[1]
        pager = arguments[2]

        backend.SetAsDefault(domain)
        pager.content_pop()
        #TODO: refresh backends list

    def enableOrDisable(self, obj, event, backend, *args, **kargs):
        if obj.state_get():
            backend.Enable()
        else:
            backend.Disable()
        

    def backendOptions(self, obj, event, arguments, *args, **kargs):
        backend = arguments[0]
        domain = arguments[1]
        pager = arguments[2]
        defaultbackend = arguments[3]

        backendname = backend.GetName()

        box = elementary.Box(pager)
        box.show()

        label = elementary.Label(pager)
        #label.label_set(backendname + "<br>(domain: "+domain+")")
        label.label_set(_("%(backend)s<br>(domain: %(domain)s)") % {'backend':backendname, 'domain':domain})
        label.show()
        box.pack_start(label)
 
        check = elementary.Check(pager)
        check.label_set(_("enabled"))
        check._callback_add("changed", (self.enableOrDisable, backend))

        check.state_set(backend.GetEnabled())
        check.show()

        box.pack_end(check)

        if defaultbackend.lower() != backendname.lower():
            default = elementary.Button(pager)
            default.label_set(_("Set as default"))
            default._callback_add("clicked", (self.setAsDefault, [backend, domain, pager]))
            default.show()

            box.pack_end(default)

        back = elementary.Button(pager)
        back.label_set(_("Quit"))
        back._callback_add("clicked", (self.pagerPop, pager))
        back.show()

        box.pack_end(back)

        pager.content_push(box)

    def domainWindow(self, obj, event, domain, *args, **kargs):
        win = elementary.Window("domain", elementary.ELM_WIN_BASIC)
        win.show()
        win.autodel_set(1)
        bg = elementary.Background(win)
        win.resize_object_add(bg)
        bg.show()
        
        box = elementary.Box(win)
        #win.resize_object_add(box)
        box.show()

        list = elementary.List(win)
        #box.pack_start(list)
        list.show()

        pager = elementary.Pager(win)

        pager.content_push(list)

        pager.show()

        win.resize_object_add(pager)

        backendscount = self.dbusObj.GetEntryCount()
        
        try:
            defaultbackend = self.dbusObj.GetDefaultBackend(domain)
        except:
            defaultbackend = ""

        for i in range(0,backendscount):
            backend = getDbusObject(self.dbus, "org.freesmartphone.opimd", "/org/freesmartphone/PIM/Sources/"+str(i), "org.freesmartphone.PIM.Source")
            if domain in backend.GetSupportedPIMDomains():
                checkbox = elementary.Check(win)
                button = elementary.Button(win)
                button.label_set(_("Options"))
                button._callback_add("clicked", (self.backendOptions, [backend, domain, pager, defaultbackend]))
                default = ""
                name = backend.GetName()
                if defaultbackend.lower()==name.lower():
                    default = _(" (default)")
                list.item_append(name + default, None, button, None)

        list.go()

    def createView(self):

        self.main = elementary.Box(self.window)
        
        try:
            # create dbus object
            self.dbusObj = getDbusObject(self.dbus, 
                "org.freesmartphone.opimd", 
                "/org/freesmartphone/PIM/Sources", 
                "org.freesmartphone.PIM.Sources" )

            self.main = elementary.Box(self.window)

            self.domains = self.dbusObj.GetDomains()

            label = elementary.Label(self.main)
            label.label_set(_("Domains:"))
            self.main.pack_start(label)
            label.size_hint_align_set(-1.0, 0.0)
            label.show()

            for domain in self.domains:
                dombutton = elementary.Button(self.main)
                dombutton.label_set(domain)
                dombutton.size_hint_align_set(-1.0, -1.0)
                dombutton.size_hint_weight_set(1.0, 1.0)
                dombutton._callback_add("clicked", (self.domainWindow, domain))
                self.main.pack_end(dombutton)
                dombutton.show()

        except:
            self.error()

        return self.main