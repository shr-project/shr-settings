import elementary, module, os

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


class Splash(module.AbstractModule):
    name = _("Splash settings")

    def setTheme(self, obj, event, path, *args, **kargs):
        """
        Set the current profile to `name`
        """
        #self.dbusObj.SetProfile(name)
        os.system('rm /usr/share/shr-splash/theme') # do we really need THAT?
        os.system('update-alternatives --install /usr/share/shr-splash/theme shr-splash-theme '+path+' '+str(self.max_prio+1))
        self.ThemeNameUpdate()

    def ThemeNameUpdate(self):
        """
        Updates the displayed value of the current profile
        """
        #self.currentProfile = self.dbusObj.GetProfile().title()
#        file = os.popen('cat /usr/lib/opkg/alternatives/shr-splash-theme | grep 11')
        file = open('/usr/lib/opkg/alternatives/shr-splash-theme', 'r' )

        self.themes = {} # items: 'name' : ('path', priority)
        self.priority_idx = {} # items: priority : [theme names]

        s=1
        while s:
            line = file.readline()
            if not line:
                self.currentProfile = '[nothing ;p]'
                s = 0
            else:
                s = line.split(" ")
                if len(s)==2:
#                    self.currentProfile = s[0]
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

        self.hoverSel.label_set(_("Themes (%s)" % self.currentProfile))

        self.max_prio = max_prio

    def listThemes(self):
        """
        Displays the profiles Hoversel
        """
        self.main.size_hint_weight_set(1.0, -1.0)

        # Listing HoverSelect
        self.hoverSel = elementary.Hoversel(self.window)
        self.hoverSel.hover_parent_set(self.window)
        self.hoverSel.size_hint_weight_set(-1.0, 0.0)
        self.hoverSel.size_hint_align_set(-1.0, 0.0)
        self.main.pack_end(self.hoverSel)
        self.hoverSel.show()
        
        # Set current profile name to the hoverSel label
        self.ThemeNameUpdate()

        # Add HoversleItems
        # The callback is a bit of functools.partial magic
        for i in self.themes:
            name = self.themes[i][0]
            self.hoverSel.item_add(name, 
                "arrow_down", 
                elementary.ELM_ICON_STANDARD, 
                partial( self.setTheme, path = i ))

    def createView(self):

        self.main = elementary.Box(self.window)
        
        self.listThemes()
            
        return self.main
