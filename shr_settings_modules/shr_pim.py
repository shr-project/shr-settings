import elementary, module
import dbus

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
        label.label_set(_("Couldn't connect to FSO"))
        self.main.pack_start(label)
        label.show()

    def pagerPop(self, obj, event, pager, *args, **kargs):
        pager.content_pop()

    def setAsDefault(self, obj, event, arguments, *args, **kargs):
        backend = arguments[0]
        domain = arguments[1]
        pager = arguments[2]
        win = arguments[3]

        backend.SetAsDefault(domain)
        self.domainWindow(obj, event, domain)
        win.delete()

    def enableOrDisable(self, obj, event, backend, *args, **kargs):
        if obj.state_get():
            backend.Enable()
        else:
            backend.Disable()
        

    def backendOptions(self, arguments, obj, event, *args, **kargs):

        backend = arguments[0]
        domain = arguments[1]
        pager = arguments[2]
        defaultbackend = arguments[3]
        win = arguments[4]

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

        props = backend.GetProperties()

        prop_texts = {'add_entry':_('adding entries'), 'upd_entry':_('updating entries'),'del_entry':_('deleting entries'),'upd_entry_with_new_field':_('adding new fields to entries'),'needs_login':_('needs loging in'),'needs_sync':_('needs syncing'),'is_handler':_("it's handler")}

        prop_text = '<b>' + _('Properties') + ': </b><br>';

        for prop in props:
            prop_text += '* ' + prop_texts[prop] + '<br>'

        if len(props):
            propan = elementary.AnchorBlock(pager)
            propfr = elementary.Frame(pager)
#            propfr.label_set(_('Properties'))
            propfr.style_set('outdent_top')
            propfr.content_set(propan)
            propfr.show()
            box.pack_end(propfr)
            propan.text_set(prop_text)
            propan.show()
            propan.size_hint_weight_set(-1.0, 0.0)
            propan.size_hint_align_set(-1.0, 0.0)
            propfr.size_hint_weight_set(1.0, 0.0)
            propfr.size_hint_align_set(-1.0, 0.0)

        box.pack_end(check)

        if defaultbackend.lower() != backendname.lower() and 'add_entry' in props:
            default = elementary.Button(pager)
            default.label_set(_("Set as default"))
            default._callback_add("clicked", (self.setAsDefault, [backend, domain, pager, win]))
            default.show()

            box.pack_end(default)

        back = elementary.Button(pager)
        back.label_set(_("Quit"))
        back._callback_add("clicked", (self.pagerPop, pager))
        back.show()

        box.pack_end(back)

        pager.content_push(box)

    def destroywin(self, win, *args, **kargs):
        win.delete()

    def domainWindow(self, obj, event, domain, *args, **kargs):
        win = elementary.Window("domain", elementary.ELM_WIN_BASIC)
        win.show()
        win.autodel_set(1)
        win.title_set(domain)
        bg = elementary.Background(win)
        win.resize_object_add(bg)
        bg.show()
        
        box = elementary.Box(win)
        #win.resize_object_add(box)
        box.show()

        list = elementary.List(win)
        box.pack_start(list)
        list.size_hint_weight_set(1.0, 1.0)
        list.size_hint_align_set(-1.0, -1.0)
        list.show()

        quitbt = elementary.Button(win)
        quitbt.clicked = partial(self.destroywin, win)
        quitbt.label_set(_("Quit"))
        quitbt.size_hint_align_set(-1.0, 0.0)
        ic = elementary.Icon(quitbt)
        ic.file_set( "/usr/share/pixmaps/icon_quit.png" )
        ic.scale_set(1,1)
        ic.smooth_set(1)
        quitbt.icon_set(ic)
        quitbt.show()
        box.pack_end(quitbt)


        pager = elementary.Pager(win)

        pager.content_push(box)

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
                default = ""
                name = backend.GetName()
                if defaultbackend.lower()==name.lower():
                    default = _(" (default)")
                list.item_append(name + default, None, None, partial(self.backendOptions, [backend, domain, pager, defaultbackend, win]))

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

            self.hoverSel = elementary.Hoversel(self.window)
            self.hoverSel.hover_parent_set(self.window)
            self.hoverSel.label_set(_("Domains"))
            self.hoverSel.size_hint_weight_set(-1.0, 0.0)
            self.hoverSel.size_hint_align_set(-1.0, 0.0)
            self.main.pack_end(self.hoverSel)
            self.hoverSel.show()

            for domain in self.domains:
#                dombutton = elementary.Button(self.main)
#                dombutton.label_set(domain)
#                dombutton.size_hint_align_set(-1.0, -1.0)
#                dombutton.size_hint_weight_set(1.0, 1.0)
#                dombutton._callback_add("clicked", (self.domainWindow, domain))
#                self.main.pack_end(dombutton)
#                dombutton.show()

                self.hoverSel.item_add(domain,
                "arrow_right",
                elementary.ELM_ICON_STANDARD,
                partial( self.domainWindow, domain = domain ))


        except:
            self.error()

        return self.main
