import elementary, module, os

# Locale support
import gettext

from math import floor
from functools import partial
from dircache import listdir

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class Elementary(module.AbstractModule):
    name = _("Elementary settings")
    keys = {}
    changed = False

    def setValue(self, field, value, *args, **kargs):
        os.system('sed "s/export '+field+'=.*/export '+field+'='+value+'/" /etc/profile.d/elementary.sh -i')
        if callable(kargs.get('callback')):
            kargs['callback']()
        if not self.changed:
            btn = elementary.Button(self.window)
            btn.label_set(_('Restart X server'))
            btn.size_hint_align_set(-1.0, -1.0)
            btn.size_hint_weight_set(1.0, 0.0)
            btn.show()
            btn.clicked = self.xrestart
            self.main.pack_end(btn)
            self.changed = True

    def keysUpdate(self):
        """
        Updates the displayed value of the current theme
        """
        try:
            file = open('/etc/profile.d/elementary.sh', 'r' )
        except:
            #FIXME! UGLY!
            os.system('echo "export ELM_ENGINE=x11" > /etc/profile.d/elementary.sh')
            os.system('echo "export ELM_THEME=default" >> /etc/profile.d/elementary.sh')
            os.system('echo "export ELM_FINGER_SIZE=70" >> /etc/profile.d/elementary.sh')
            os.system('echo "export ELM_SCALE=2" >> /etc/profile.d/elementary.sh')
            file = open('/etc/profile.d/elementary.sh', 'r' )

        s=1
        while s:
            line = file.readline()
            if not line:
                s = 0
            else:
                s = line.split("=")
                if len(s)==2:
                    name = s[0].replace('export ','')
                    value = s[1].replace('\n', '')
                    self.keys[name]=value

        self.hoverSel.label_set(_("Themes (%s)") % self.keys['ELM_THEME'])
        if self.keys['ELM_ENGINE']=='x11':
            self.engine.value_set(1)
        else:
            self.engine.value_set(0)
        self.slider.value = int(self.keys['ELM_FINGER_SIZE'])

    def closex(self, dia, obj, *args, **kwargs):
        os.system('. /etc/profile.d/elementary.sh; /etc/init.d/xserver-nodm restart &')
        self.closedia(dia)
        obj.delete()

    def closedia(self, dia, *args, **kwargs):
        dia.delete()

    def xrestart(self, obj, *args, **kargs):
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
        label.text_set(_('Restarting X server will close running applications. Do you really want to proceed?'))
        label.show()
        box.pack_start(label)
        hbox = elementary.Box(self.window)
        hbox.horizontal_set(True)
        box.pack_end(hbox)
        hbox.show()

        yes = elementary.Button(self.window)
        yes.label_set(_('Yes'))
        yes.show()
        yes.clicked = partial(self.closex, dia, obj)
        hbox.pack_start(yes)

        no = elementary.Button(self.window)
        no.label_set(_('No'))
        no.show()
        no.clicked = partial(self.closedia, dia)
        hbox.pack_end(no)

        dia.show()
        dia.activate()

    def OnOffClick(self, obj, *args, **kargs):
        if obj.value_get():
            self.setValue('ELM_ENGINE', 'x11')
        else:
            self.setValue('ELM_ENGINE', 'x11-16')

    def setFingerSize(self, obj, *args, **kargs):
        integer = int(floor(obj.value))
        if obj.value-integer>=0.5:
          integer = integer + 1
        self.setValue('ELM_FINGER_SIZE', str(integer))

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

        themeList = listdir("/usr/share/elementary/themes/")
        themeList.sort()
        for theme in themeList:
            if theme.endswith('.edj'):
                theme = theme.split('.edj')[0]
                self.hoverSel.item_add(theme,
                "arrow_down",
                elementary.ELM_ICON_STANDARD,
                partial( self.setValue, 'ELM_THEME', theme, callback = self.keysUpdate))

        radiobox = elementary.Box(self.window)
        radiobox.horizontal_set(True)

        radiobox.show()

        engine = elementary.Frame(self.window)
        engine.label_set(_("Engine:"))
        engine.show()
        engine.content_set(radiobox)

        engine.size_hint_align_set(-1.0, -1.0)
        engine.size_hint_weight_set(1.0, 0.0)

        radioOn = elementary.Radio(self.window)
        radioOn.label_set(_("x11"))
        radioOn.size_hint_weight_set(1.0, 0.0)
        radioOn.size_hint_align_set(0.5, 0.0)
        radioOn.state_value_set(1)
        radioOn._callback_add("changed", self.OnOffClick)
        radioOn.show()

        radioOff = elementary.Radio(self.window)
        radioOff.label_set(_("x11-16"))
        radioOff.size_hint_weight_set(1.0, 0.0)
        radioOff.size_hint_align_set(0.5, 0.0)
        radioOff.state_value_set(0)
        radioOff._callback_add("changed", self.OnOffClick)
        radioOff.show()

        radioOff.group_add(radioOn)

        radiobox.pack_start(radioOn)
        radiobox.pack_end(radioOff)

        self.engine = radioOff

        self.slider = elementary.Slider(self.window)
        self.slider.label_set(_('Finger size '))
        self.slider.size_hint_align_set(-1.0, -1.0)
        self.slider.size_hint_weight_set(1.0, 0.0)
        self.slider.unit_format_set(" %0.f ")
        self.slider.min_max_set(35, 150)
        self.slider._callback_add("delay,changed", self.setFingerSize)
        self.slider.show()

        self.main.pack_end(self.slider)
        self.main.pack_end(engine)

        self.keysUpdate()


    def createView(self):

        self.main = elementary.Box(self.window)
        
        self.listThemes()
            
        return self.main
