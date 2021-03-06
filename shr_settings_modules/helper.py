import elementary
import dbus

def getDbusObject (bus, busname , objectpath , interface):
    dbusObject = bus.get_object(busname, objectpath)
    return dbus.Interface(dbusObject, dbus_interface=interface)


class ElmLabelBox(elementary.Box):
    """
    Implements read only title+option box 
    """
    def text_get(self):
        return self.Status.text_get()

    def text_set(self, value):
        return self.Status.text_set(value.title())

    def __init__(self, win, label, value):
        """
        """

        super(ElmLabelBox, self).__init__(win)
        self.horizontal_set(True)

        self.size_hint_align_set(0.0, 0.0)

        self.window = win
        self.label  = label
        self.value  = value

        self.Label = elementary.Label(self.window)
        self.Label.text_set(self.label)
        self.Label.show()

        self.Status = elementary.Label(self.window)
        self.Status.text_set(self.value)
        self.Status.show()

        self.pack_start(self.Label)
        self.pack_end(self.Status)
        self.show()


class ElmEntryBox(elementary.Box):
    """
    Class for title + modificable option 
    """

    def entry_get(self):
        return self.Entry.entry_get()

    def entry_set(self, value):
        return self.Entry.entry_set(value)

    def __init__(self, win, label, value):
        """
        """

        super(ElmEntryBox, self).__init__(win)
        self.horizontal_set(True)

        self.size_hint_weight_set(1.0, 0.0)
        self.size_hint_align_set(-1.0, 0.0)

        self.window = win
        self.label  = label
        self.value  = value

        self.Label = elementary.Label(self.window)
        self.Label.size_hint_align_set(-1.0, 0.0)
        self.Label.text_set(self.label)
        self.Label.show()

        self.Entry = elementary.Entry(self.window)
        self.Entry.size_hint_align_set(-1.0, 0.0)
        self.Entry.size_hint_weight_set(1.0, 0.0)
        self.Entry.single_line_set(True)
        self.Entry.entry_set(self.value)
        self.Entry.show()

        self.EntryFrame = elementary.Frame(self.window)
        self.EntryFrame.size_hint_align_set(-1.0, 0.0)
        self.EntryFrame.size_hint_weight_set(1.0, 0.0)
        self.EntryFrame.style_set("outdent_top")
        self.EntryFrame.content_set(self.Entry)
        self.EntryFrame.show()

        self.pack_start(self.Label)
        self.pack_end(self.EntryFrame)
        self.show()
