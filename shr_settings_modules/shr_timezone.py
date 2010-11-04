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
    
class LabelBox(elementary.Box):
    """
    Class for HW ADDRESS info
    """
    def label_get(self):
        return self.Status.label_get()

    def label_set(self, value):
        return self.Status.label_set(value.title())

    def __init__(self, win, label, value):
        """
        """

        super(LabelBox, self).__init__(win)
        self.horizontal_set(True)
        
        self.size_hint_weight_set(1.0, 0.0)
        self.size_hint_align_set(-1.0, 0.0)

        self.window = win
        self.label  = label
        self.value  = value

        self.Label = elementary.Label(self.window)
        self.Label.label_set(self.label)
        self.Label.size_hint_align_set(-1.0, 0.0)
        self.Label.show()

        self.Status = elementary.Label(self.window)
        self.Status.size_hint_align_set(-1.0, 0.0)
        self.Status.size_hint_weight_set(1.0, 0.0)
        self.Status.label_set(self.value)
        self.Status.show()


        self.StatusFrame = elementary.Frame(self.window)
        self.StatusFrame.size_hint_align_set(-1.0, 0.0)
        self.StatusFrame.size_hint_weight_set(1.0, 0.0)
        self.StatusFrame.style_set("outdent_top")
        self.StatusFrame.content_set(self.Status)
        self.StatusFrame.show()

        self.pack_start(self.Label)
        self.pack_end(self.StatusFrame)
        self.show()

    
class Timezone(module.AbstractModule):
    name = _("Timezone settings")
    tzdir = "/usr/share/zoneinfo"
    tzf = "/etc/timezone"
    
    
    def GetCurrentTimezone(self):
        try:
            tzfile = open(self.tzf, "r+")
            line = tzfile.readline()
            tzfile.close()
            return line
        except:
            print "could not open "+self.tzf+" for reading"
            return "unknown"
    
    def setNewTimezone(self, timezone):
        try:
            tzfile = open(self.tzf, "w+")
        except:
            print "Error opening /etc/timezone"
            return
        tzfile.writelines(timezone)
        tzfile.close()
        if os.path.isfile("/etc/localtime"):
            print "removing old /etc/localtime"
            os.system("rm /etc/localtime")
        ret = os.system("ln  -s %s /etc/localtime" % os.path.join(self.tzdir,timezone))
        if ret:
            print "error linking timezone to /etc/localtime"
            
            
    def receivedTimezone(self, timezone, obj, *args, **kargs):
        self.setNewTimezone(timezone)
        self.closeTzList()
    
    def generateTimezones(self, prefix):
        
        tzs = [ os.path.join(prefix,f) for f in os.listdir(os.path.join(self.tzdir,prefix)) if os.path.isfile(os.path.join(self.tzdir,prefix,f)) ]
        for i in os.listdir(os.path.join(self.tzdir,prefix)):
            if os.path.isdir(os.path.join(self.tzdir,prefix,i)):
                subtzs = self.generateTimezones(os.path.join(prefix, i))
                for f in subtzs:
                    tzs.append(f)
        return tzs
    
    def populateTzList(self):
        self.timezones = self.generateTimezones("")
        self.timezones = sorted(self.timezones)
        for tz in self.timezones:
            btz = elementary.Button(self.inwin)
            btz.label_set(tz)
            btz.size_hint_weight_set(-1.0, 0.0)
            btz.size_hint_align_set(-1.0, 0.0)
            self.inbox.pack_end(btz)
            btz.show()
            btz._callback_add('clicked', partial(self.receivedTimezone, tz))
        
    
    def createTzList(self, *args):
        
        self.inwin = elementary.InnerWindow(self.window)
        self.inwin.style_set('default')
        self.window.resize_object_add(self.inwin)
        self.inwin.show()
        self.inwin.activate()
        
        self.scr = elementary.Scroller(self.inwin)
        self.scr.bounce_set(0,0)
        self.scr.size_hint_weight_set(1.0, 1.0)
        self.scr.size_hint_align_set(-1.0, -1.0)
        self.inwin.content_set(self.scr)
        self.scr.show()
        
        self.inbox = elementary.Box(self.inwin)
        self.scr.content_set(self.inbox)
        
        self.populateTzList()
 
        
    def closeTzList(self, *args):
        self.inwin.delete()
  

    def createButton(self):
        self.bt = elementary.Button(self.window)
        self.bt.label_set(_("Set Timezone"))
        self.bt.size_hint_weight_set(-1.0, 0.0)
        self.bt.size_hint_align_set(-1.0, 0.0)
        self.main.pack_end(self.bt)
        self.bt.show()
        self.bt._callback_add('clicked', self.createTzList)
        
    def createView(self):
        self.main = elementary.Box(self.window)
        self.CurrentTZ = LabelBox(self.window, _("Current Timezone: "), self.GetCurrentTimezone())
        self.main.pack_end(self.CurrentTZ)
        self.createButton()
        return self.main
