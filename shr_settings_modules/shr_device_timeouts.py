import module, elementary
import dbus

from helper import getDbusObject

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x

def dbus_ok(*args, **kargs):
    pass

def dbus_err(x, *args, **kargs):
    print str(x)

class ValueLabel( elementary.Label ):
    """ Label that displays current timeout """
    def __init__(self, win):
        self._value = None
        super(ValueLabel, self).__init__(win)

    def get_value(self):
        return self._value

    def set_value(self, val):
         self.text_set(str(val) + _(" sec."))
         self._value = val

class IncDecButton(elementary.Button):
    """
    Button that add/substracts from the value label
    """

    def set_Delta(self, delta):
        self._delta = delta
        self.text_set("{0:+d}".format(delta))

    def get_Delta( self ):
        return self._delta


class IncDecButtonBox(elementary.Box):
    """
    Object which shows an increment/decrement button set to alter int
    Preferences values
    """

    def IncDecButtonClick(self, obj, *args, **kargs):
        """
        Callback function when +-[1,10] timeout buttons have been pressed
        """
        cur_val = self.cur_value
        delta  = obj.get_Delta()
        new_val = max(-1, cur_val + delta)

        self.dbusObj.SetTimeout(self.item_name,int(new_val), reply_handler=dbus_ok, error_handler=dbus_err)
        self.cur_value = new_val
        self.itemValue.set_value(self.cur_value)

    def update(self):
        """
        Updates the displayed value to the current profile
        """
        timeouts = self.dbusObj.GetTimeouts()
        self.cur_value = timeouts[self.item_name]
        self.itemValue.set_value(self.cur_value) #implicitely sets label too

    def setup(self):
        """
        Function to show a increment/decrement button set to alter int
        Preferences values

        Layout developed from shr_device_timeouts.py
        """

        self.horizontal_set(True)
        self.size_hint_align_set(-1.0, 0.0)
        self.size_hint_weight_set(1.0, 0.0)

        itemLabel = elementary.Label(self.window)
        itemLabel.size_hint_weight_set(1.0, 0.0)
        itemLabel.text_set(self.item_name.replace("_"," ").title())
        itemLabel.show()

        itemFrame = elementary.Frame(self.window)
        itemFrame.style_set("outdent_top")
        itemFrame.content_set(itemLabel)
        itemFrame.show()

        self.itemValue = ValueLabel(self.window)
        self.itemValue.size_hint_weight_set(1.0, 0.0)
        self.itemValue.set_value(self.cur_value) #implicitely sets label too
        self.itemValue.show()

        boxbox = elementary.Box(self.window)
        boxbox.pack_start(itemFrame)
        boxbox.pack_end(self.itemValue)
        boxbox.size_hint_weight_set(1.0, 0.0)
        boxbox.show()

        buttons = []

        for step in [-10, -1, 1, 10]:
            btn = IncDecButton(self.window)
            btn.set_Delta( step )
            btn._callback_add('clicked', self.IncDecButtonClick)
            btn.size_hint_align_set(-1.0, 0.0)
            btn.show()

            buttons.append(btn)

        self.pack_end(buttons[0])
        self.pack_end(buttons[1])
        self.pack_end(boxbox)
        self.pack_end(buttons[2])
        self.pack_end(buttons[3])

        self.show()

    def __init__(self, win, dbusObj, item_name, initial_value):
        """
        initialize the box and load objects
        """
        super(IncDecButtonBox, self).__init__(win)
        self.window = win
        self.dbusObj = dbusObj
        self.item_name = item_name
        self.cur_value = initial_value

        self.setup()

class Timeouts(module.AbstractModule):
    name = _("Timeouts settings")

    def error(self):
        label = elementary.Label(self.window)
        label.text_set(_("Couldn't connect to FSO"))
        label.show()
        self.main.pack_start(label)

    def createView(self):
        self.main = elementary.Box(self.window)

        self.dbus_state = 0
        try:
            self.dbusObj = getDbusObject( self.dbus,
                "org.freesmartphone.odeviced",
                "/org/freesmartphone/Device/IdleNotifier/0",
                "org.freesmartphone.Device.IdleNotifier")
            self.timeouts = self.dbusObj.GetTimeouts()
            self.dbus_state = 1
        except:
            self.dbus_state = 0
            self.error()

        tmptimeouts = sorted(self.timeouts.iteritems(), key=lambda (k,v): (v,k))

        if self.dbus_state:
            for i in tmptimeouts:
                if not str(i[0]) in ("awake","busy","none"):
                    box = IncDecButtonBox(self.window, self.dbusObj, i[0], i[1])
                    self.main.pack_end(box)
            self.main.show()

        return self.main
