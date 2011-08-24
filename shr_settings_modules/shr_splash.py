import elementary, module, os, ecore

# Locale support
import gettext

## Testing
from functools import partial


try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class Splash(module.AbstractModule):
    name = _("Splash settings")

    def setTheme(self, path, obj, *args, **kargs):
        """
        Set the current theme to `path`
        """
        os.system('rm /usr/share/shr-splash/theme') # do we really need THAT?
        os.system('update-alternatives --install /usr/share/shr-splash/theme shr-splash-theme '+path+' '+str(self.max_prio+1))
        self.ThemeNameUpdate()

    def ThemeNameUpdate(self):
        """
        Updates the displayed value of the current theme
        """
        file = open('/var/lib/opkg/alternatives/shr-splash-theme', 'r' )

        self.themes = {} # items: 'path' : ('name', priority)
        self.priority_idx = {} # items: priority : [theme paths]

        s=1
        while s:
            line = file.readline()
            if not line:
                s = 0
            else:
                s = line.split(" ")
                if len(s)==2:
                     try:
                         namefile = open(s[0]+'/name')
                         name = namefile.readline().replace('\n','')
                     except:
                         name = s[0].replace('/usr/share/shr-splash/themes/','')
                     self.themes[s[0]] = (name,int(s[1]))
                     try:
                         self.priority_idx[int(s[1])].append(s[0])
                     except:
                         self.priority_idx[int(s[1])]=[s[0]]

        max_prio = -1
        for prio in self.priority_idx:
            if prio>max_prio:
                max_prio=prio

        self.priority_idx[max_prio].sort()

        self.currentProfile = self.themes[self.priority_idx[max_prio][len(self.priority_idx[max_prio])-1]][0]

        self.hoverSel.text_set(_("Themes (%s)") % self.currentProfile)

        self.max_prio = max_prio
        self.currentTheme = self.priority_idx[max_prio][len(self.priority_idx[max_prio])-1]

    def preview_close(self):
        self.prevwin.hide()
        self.prevwin.delete()
        del self.prevwin
        return False

    def preview(self, obj, *args, **kwargs):
#        print self.currentTheme
        self.prevwin = elementary.Window('preview', 0)
        bg = elementary.Background(self.prevwin)
        bg.file_set(self.currentTheme + '/preview.png')
        bg.show()
        self.prevwin.resize_object_add(bg)
        self.prevwin.autodel_set(True)
        self.prevwin.fullscreen_set(True)
        self.prevwin.show()
        ecore.timer_add(5, self.preview_close)

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

        # Preview button
        previewbtn = elementary.Button(self.window)
        previewbtn.text_set(_("Preview"))
        previewbtn._callback_add('clicked', self.preview)
        previewbtn.show()
        previewbtn.size_hint_align_set(-1.0, 0.0)
        hozBox.pack_end(previewbtn)        

        # Set current theme name to the hoverSel label
        self.ThemeNameUpdate()

        # Add HoversleItems
        # The callback is a bit of functools.partial magic
        for i in self.themes:
            name = self.themes[i][0]
            self.hoverSel.item_add(name, 
                "arrow_down", 
                elementary.ELM_ICON_STANDARD, 
                partial( self.setTheme, i ))

    def createView(self):

        self.main = elementary.Box(self.window)
        
        self.listThemes()
            
        return self.main
