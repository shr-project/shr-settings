import elementary
import module
import os


# Locale support
import gettext

## Testing
from functools import partial

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x
    
    
class Timezone(module.AbstractModule):
    name = _("Timezone settings")
    tzdir = "/usr/share/zoneinfo"
    try:
        tzfile = open("/etc/timezone", "w+")
    except:
        print "Error opening /etc/timezone"
     
    def setNewTimezone(self, prefix, timezone):
        try:
            tzfile = open("/etc/timezone", "w+")
        except:
            print "Error opening /etc/timezone"
            return
        tzfile.writelines(os.path.join(prefix, timezone))
        tzfile.close()
        if os.path.isfile("/etc/localtime"):
            print "removing old /etc/localtime"
            os.system("rm /etc/localtime")
        ret = os.system("ln  -s %s /etc/localtime" % os.path.join(self.tzdir,prefix,timezone))
        if ret:
            print "error linking timezone to /etc/localtime"
                
    def receivedTimezone0(self, timezone, obj, *args, **kargs):
        print timezone
        if self.hs1exists==1:
            self.hoverSel1.delete()
        self.hoverSel0.label_set(timezone)
        if os.path.isdir(os.path.join(self.tzdir, timezone)):
            self.createhoverSel1(timezone)
        else:
            self.setNewTimezone("", timezone)
            
    def receivedTimezone1(self, prefix, timezone, obj, *args, **kargs):
        print os.path.join(prefix, timezone)
        self.hoverSel1.label_set(timezone)
        if os.path.isfile(os.path.join(self.tzdir, prefix, timezone)):
            self.setNewTimezone(prefix, timezone)
        
    def createhoverSel0(self):
        self.hs1exists=0
        self.hoverSel0 = elementary.Hoversel(self.window)
        self.hoverSel0.hover_parent_set(self.window)
        self.hoverSel0.size_hint_weight_set(-1.0, 0.0)
        self.hoverSel0.size_hint_align_set(-1.0, 0.0)
        self.main.pack_end(self.hoverSel0)
        self.hoverSel0.show()
        for i in os.listdir(self.tzdir):
            self.hoverSel0.item_add(i, "arrow_down", elementary.ELM_ICON_STANDARD, partial( self.receivedTimezone0, i))
        return self.hoverSel0
        
    def createhoverSel1(self, subdir):
        self.hs1exists = 1
        self.hoverSel1 = elementary.Hoversel(self.window)
        self.hoverSel1.hover_parent_set(self.window)
        self.hoverSel1.size_hint_weight_set(-1.0, 0.0)
        self.hoverSel1.size_hint_align_set(-1.0, 0.0)
        self.main.pack_end(self.hoverSel1)
        self.hoverSel1.show()
        for i in os.listdir(os.path.join(self.tzdir,subdir)):
            self.hoverSel1.item_add(i, "arrow_down", elementary.ELM_ICON_STANDARD, partial ( self.receivedTimezone1, subdir, i))
        return self.hoverSel1
    
    def createView(self):
        self.main = elementary.Box(self.window)
        
        self.createhoverSel0()
        return self.main
