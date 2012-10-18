import elementary, module

from helper import getDbusObject

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


class Pim(module.AbstractModule):
    name = _("PIM settings")

    def error(self):
        """
        Report the DBus is fsck'd
        """
        label = elementary.Label(self.window)
        label.text_set(_("Couldn't connect to FSO"))
        self.main.pack_start(label)
        label.show()

    def pagerPop(self, pager, obj, *args, **kargs):
        pager.item_pop()

    def setAsDefault(self, arguments, obj, *args, **kargs):
        backend = arguments[0]
        domain = arguments[1]
        pager = arguments[2]
        win = arguments[3]

        backend.SetAsDefault(domain)
        self.domainWindow(domain, obj)
        win.delete()

    def pleasewait(self, win):
        dia = elementary.InnerWindow(win)
        label = elementary.Label(dia)
        label.text_set(_('Please wait...'))
        dia.style_set('minimal')
        label.show()
        dia.content_set(label)
        win.resize_object_add(dia)
        dia.activate()
        return dia

    def dbus_finished(self, win, *args, **kwargs):
        win.delete()

    def enableOrDisable(self, backend, win, obj, *args, **kargs):
        dia = self.pleasewait(win)
        if obj.state_get():
            backend.Enable(reply_handler = partial(self.dbus_finished, dia), error_handler = partial(self.dbus_finished, dia))
        else:
            backend.Disable(reply_handler = partial(self.dbus_finished, dia), error_handler = partial(self.dbus_finished, dia))
        

    def backendOptions(self, arguments, obj, *args, **kargs):

        backend = arguments[0]
        domain = arguments[1]
        pager = arguments[2]
        defaultbackend = arguments[3]
        win = arguments[4]

        backendname = backend.GetName()

        initialized = backend.GetInitialized()

        box = elementary.Box(pager)
        box.show()

        label = elementary.Label(pager)
        #label.text_set(backendname + "<br>(domain: "+domain+")")
        label.text_set(_("%(backend)s<br>(domain: %(domain)s)") % {'backend':backendname, 'domain':domain})
        label.show()
        box.pack_start(label)
 
        check = elementary.Check(pager)
        check.text_set(_("enabled"))
        check._callback_add("changed", partial(self.enableOrDisable, backend, win))

        check.state_set(backend.GetEnabled())
        check.show()

        props = backend.GetProperties()

        prop_texts = {'add_entry':_('adding entries'), 'upd_entry':_('updating entries'),'del_entry':_('deleting entries'),'upd_entry_with_new_field':_('adding new fields to entries'),'needs_login':_('needs logging in'),'needs_sync':_('needs syncing'),'is_handler':_("it's handler")}

        prop_text = '<b>' + _('Properties') + ': </b><br>';

        for prop in props:
            prop_text += '* ' + prop_texts[prop] + '<br>'

        if len(props):
            propan = elementary.Entry(pager)
            propfr = elementary.Frame(pager)
#            propfr.text_set(_('Properties'))
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

        inited = elementary.Label(pager)
        if initialized:
            inited.text_set(_('Initialized'))
        else:
            inited.text_set(_('Not initialized'))
        inited.show()
        box.pack_end(inited)


        box.pack_end(check)

        if defaultbackend.lower() != backendname.lower() and 'add_entry' in props:
            default = elementary.Button(pager)
            default.text_set(_("Set as default"))
            default._callback_add("clicked", partial(self.setAsDefault, [backend, domain, pager, win]))
            default.show()

            box.pack_end(default)

        back = elementary.Button(pager)
        back.text_set(_("Quit"))
        back._callback_add("clicked", partial(self.pagerPop, pager))
        back.show()

        box.pack_end(back)

        pager.item_simple_push(box)

    def destroywin(self, win, *args, **kargs):
        win.delete()

    def domainWindow(self, domain, obj, *args, **kargs):
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
        quitbt._callback_add('clicked', partial(self.destroywin, win))
        quitbt.text_set(_("Quit"))
        quitbt.size_hint_align_set(-1.0, 0.0)
        ic = elementary.Icon(quitbt)
        ic.file_set( "/usr/share/pixmaps/shr-settings/icon_quit.png" )
        ic.resizable_set(1,1)
        ic.smooth_set(1)
        quitbt.content_set(ic)
        quitbt.show()
        box.pack_end(quitbt)


        pager = elementary.Naviframe(win)

        pager.item_simple_push(box)

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
            self.hoverSel.text_set(_("Domains"))
            self.hoverSel.size_hint_weight_set(-1.0, 0.0)
            self.hoverSel.size_hint_align_set(-1.0, 0.0)
            self.main.pack_end(self.hoverSel)
            self.hoverSel.show()

            for domain in self.domains:
#                dombutton = elementary.Button(self.main)
#                dombutton.text_set(domain)
#                dombutton.size_hint_align_set(-1.0, -1.0)
#                dombutton.size_hint_weight_set(1.0, 1.0)
#                dombutton._callback_add("clicked", partial(self.domainWindow, domain))
#                self.main.pack_end(dombutton)
#                dombutton.show()

                self.hoverSel.item_add(domain,
                "arrow_right",
                elementary.ELM_ICON_STANDARD,
                partial( self.domainWindow, domain ))


        except:
            self.error()

        return self.main
