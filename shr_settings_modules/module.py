__author__="hiciu"
__date__ ="$2008-12-27 21:53:00$"

"""
    This class should be parent for all shr-settings modules.

    There are avilable objects:
    * self.window - elementary window, used for adding new objects like buttons, menus, etc.
    * self.dbus   - object for communicating with dbus (System Bus).

    mini template for new module:
#=================
    import module
    class MyModule(module.AbstractModule):
        self.name = "MyModule";
        self.section = "main";

        def createView(self):
            box1 = elementary.Box(self.window)
            toggle0 = elementary.Toggle(self.window)
            toggle0.label_set("GSM antenna:")
            toggle0.size_hint_align_set(-1.0, 0.0)
            toggle0.states_labels_set("On","Off")
            box1.pack_start(toggle0)
            return box1
#=================
"""

class AbstractModule(object):
    name = "OhMy! I have no name!"
    """name displayed to user"""

    section = "main"
    """a toolbar section. If it is new section it will be created"""

    def __init__(self, window, dbus):
        """constructor. param: elementary window object, edbus object, return: nothing"""
        self.window = window
        self.dbus = dbus

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

    def createView(self):
        """
            This should return elementary object (for example Box) with will
            be displayed to user.
            Here is example code:

            def createView(self):
                box1 = elementary.Box(self.window)
                toggle0 = elementary.Toggle(self.window)
                toggle0.label_set("GSM antenna:")
                toggle0.size_hint_align_set(-1.0, 0.0)
                toggle0.states_labels_set("On","Off")
                box1.pack_start(toggle0)
                return box1
        """
        pass
