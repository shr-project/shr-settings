# -*- coding: utf-8 -*-
import elementary, module, os

# Locale support
import gettext

from functools import partial
from dircache import listdir

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class PhoneuiTheme(module.AbstractModule):
    name = _("Phoneui themes")
    config_file = "/usr/share/libphone-ui-shr/config"


    def getValue(self,field):
        try:
            file = open(self.config_file, 'r' )
        except:
            print "Error opening "+self.config_file
            return "unknown"

        value="unkown"
        s=1
        while s:
            line = file.readline()
            if not line:
                s = 0
            else:
                s = line.split(" = ")
                if len(s)==2 and s[0]==field:
                    value = s[1].replace('\n', '')
                    s = 0
        file.close()
        return value

    def setValue(self, field, value, *args, **kargs):
        if self.current_theme!=value:
            self.current_theme=value
            os.system('sed "s/'+field+' = .*/'+field+' = '+value+'/" '+self.config_file+' -i')
            btn = elementary.Button(self.window)
            btn.label_set(_('Restart phoneui'))
            btn.size_hint_align_set(-1.0, -1.0)
            btn.size_hint_weight_set(1.0, 0.0)
            btn.show()
            btn._callback_add('clicked', self.phoneui_restart)
            self.main.pack_end(btn)
            self.hselCurrentTheme()

    def hselCurrentTheme(self):
        self.hoverSel.label_set(_("Themes (%s)") % self.current_theme)


    def close_phoneui(self, dia, obj, *args, **kwargs):
        os.system('killall phoneuid; /usr/bin/phoneui-wrapper.sh &')
        self.closedia(dia)
        obj.delete()

    def closedia(self, dia, *args, **kwargs):
        dia.delete()

    def phoneui_restart(self, obj, *args, **kargs):
        dia = elementary.InnerWindow(self.window)
        self.window.resize_object_add(dia)
        frame = elementary.Frame(self.window)
        dia.style_set('minimal_vertical')
        dia.scale_set(1.0)
        frame.label_set(_('Are you sure?'))
        dia.content_set(frame)
        frame.show()
        box = elementary.Box(self.window)
        frame.content_set(box)
        box.show()
        label = elementary.AnchorBlock(self.window)
        label.size_hint_align_set(-1.0, -1.0)
        label.size_hint_weight_set(1.0, 0.0)
        label.text_set(_('Stopping phoneuid will stop all phone user interface related functions. Do you really want to proceed?'))
        label.show()
        box.pack_start(label)
        hbox = elementary.Box(self.window)
        hbox.horizontal_set(True)
        box.pack_end(hbox)
        hbox.show()

        yes = elementary.Button(self.window)
        yes.label_set(_('Yes'))
        yes.show()
        yes._callback_add('clicked', partial(self.close_phoneui, dia, obj))
        hbox.pack_start(yes)

        no = elementary.Button(self.window)
        no.label_set(_('No'))
        no.show()
        no._callback_add('clicked', partial(self.closedia, dia))
        hbox.pack_end(no)

        dia.show()
        dia.activate()

    def listThemes(self):
        """
        Displays the themes Hoversel
        """
        self.main.size_hint_weight_set(1.0, -1.0)

        hozBox = elementary.Box(self.window)
        hozBox.horizontal_set(True)
        hozBox.size_hint_weight_set(1.0, 0.0)
        hozBox.size_hint_align_set(-1.0, 0.0)
        hozBox.show()
        self.main.pack_end(hozBox)

        # Listing HoverSelect
        self.hoverSel = elementary.Hoversel(self.window)
        self.hoverSel.scale_set(1.0)
        self.hoverSel.hover_parent_set(self.window)
        self.hoverSel.size_hint_weight_set(1.0, 0.0)
        self.hoverSel.size_hint_align_set(-1.0, 0.0)
        hozBox.pack_end(self.hoverSel)
        self.hoverSel.show()

        themeList = listdir("/usr/share/libphone-ui-shr")
        themeList.sort()
        for theme in themeList:
            if theme.endswith('.edj') and theme!='idle_screen.edj' and theme!='widgets.edj':
                theme = theme.split('.edj')[0]
                self.hoverSel.item_add(theme,
                "arrow_down",
                elementary.ELM_ICON_STANDARD,
                partial( self.setValue, 'theme', theme))
        self.hselCurrentTheme()


    def createView(self):

        self.main = elementary.Box(self.window)

        self.current_theme = self.getValue('theme')
        print "Current theme = "+self.current_theme

        self.listThemes()

        return self.main

