__author__="hiciu"
__date__ ="$2008-12-27 21:53:00$"

"""
    This class should be parent for all shr-settings modules.

    There are avilable objects:
    * self.window - elementary window, used for adding new objects like buttons, menus, etc.
    * self.dbus   - object for communicating with dbus (System Bus).
    * self.wizard - boolean, says if module is runned by wizard

    mini template for new module:
#=================
    import module
    class MyModule(module.AbstractModule):
        self.name = "MyModule";
        self.section = "main";
        
        def init(self):
            self.gsm_enabled = self.dbus_system.(...)
            self.toggle0.state_set(self.gsm_enabled)
            
            return True

        def createView(self):
            self.box1 = elementary.Box(self.window)
            self.toggle0 = elementary.Toggle(self.window)
            self.toggle0.label_set("GSM antenna:")
            self.toggle0.size_hint_align_set(-1.0, 0.0)
            self.toggle0.states_labels_set("On","Off")
            self.box1.pack_start(toggle0)
            return self.box1

        def stopUpdate(self):
            #called when we hide the window, stop GUI updates here etc
            pass
#=================
"""

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class AbstractModule(object):
    name = _("OhMy! I have no name!")
    """name displayed to user"""

    section = _("main")
    """a toolbar section. If it is new section it will be created"""

    wizard_name = _("Some wizard page")
    wizard_description = _("Some description")
    """name and description displayed when module is used in wizard"""

    def __init__(self, window, dbus, wizard = False):
        """constructor. param: elementary window object, edbus object, return: nothing"""
        self.window = window
        self.dbus = dbus
        self.wizard = wizard

    def getName(self):
        """this one returns displayed name."""
        return self.name

    def getSection(self):
        """on which tab this module should be?"""
        #FIXME: make tab's, use elm_toolbar.. but first: make / check python bindings
        #for elm_toolbar :)
        return self.section

    def getIcon(self):
        """
            In future, this should return an object (bitmap?) that will act as
            an icon. But for now it's return 0.
        """
        #FIXME: insert proper code here :)
        return 0

    def isEnabled(self):
        """
            If module isn't enabled it shouldn't be displayed. Use it to
            check if we have wifi hardware or bluetooth dongle or something.
            Default: module is enabled
        """
        return True
        
    def init(self):
        """
            Module init. This is done after createView, but before 
            createView.show(), if it return "false" then module is
            skipped (will not be shown).
            Here should be things like timer's start, setting default
            values of toggles, labels, etc.
            
            dec init(self):
                self.gsm_enabled = self.dbus_system.(...)
                self.toggle0.state_set(self.gsm_enabled);
                
                return True
        """
        return True
        
    def destroy(self):
        """This one should close timers, free memory (python?) etc.."""
        pass

    def wizardClose(self):
        """This one is called when going into next wizard page"""
        return True

    def createView(self):
        """
            This should return elementary object (for example Box) with will
            be displayed to user.
            Code here should do only a gui.
            Here is example code:

            def createView(self):
                self.box1 = elementary.Box(self.window)
                self.toggle0 = elementary.Toggle(self.window)
                self.toggle0.label_set("GSM antenna:")
                self.toggle0.size_hint_align_set(-1.0, 0.0)
                self.toggle0.states_labels_set("On","Off")
                self.box1.pack_start(toggle0)
                return self.box1
        """
        pass


    def stopUpdate(self):
        """ called when we hide the window, stop GUI updates here """
        pass

    def bool_question_dialog(self, action, text, *args, **kargs):
        dia = elementary.InnerWindow(self.window)
        self.window.resize_object_add(dia)
        frame = elementary.Frame(self.window)
        dia.style_set('minimal_vertical')
        dia.scale_set(1.0)
        frame.label_set(_('Warning'))
        dia.content_set(frame)
        frame.show()
        box = elementary.Box(self.window)
        frame.content_set(box)
        box.show()
        label = elementary.AnchorBlock(self.window)
        label.size_hint_align_set(-1.0, -1.0)
        label.size_hint_weight_set(1.0, 0.0)
        label.text_set(text)
        label.show()
        box.pack_start(label)
        hbox = elementary.Box(self.window)
        hbox.horizontal_set(True)
        box.pack_end(hbox)
        hbox.show()

        yes = elementary.Button(self.window)
        yes.label_set(_('Yes'))
        yes.show()
        yes._callback_add('clicked', partial(action, 1))
        hbox.pack_start(yes)

        no = elementary.Button(self.win)
        no.label_set(_('No'))
        no.show()
        no._callback_add('clicked', partial(action, 0))
        hbox.pack_end(no)

        dia.show()
        dia.activate()
