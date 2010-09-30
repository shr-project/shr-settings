import elementary
import module
import os


import socket
import fcntl
import struct



# Locale support
import gettext

## Testing
from functools import partial

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x





class InterfaceLabelBox(elementary.Box):
    """
    Class for HW ADDRESS info
    """
    def label_get(self):
        return self.ifaceStatus.label_get()

    def label_set(self, value):
        return self.ifaceStatus.label_set(value.title())

    def __init__(self, win, label, value):
        """
        """

        super(InterfaceLabelBox, self).__init__(win)
        self.horizontal_set(True)

        self.size_hint_align_set(0.0, 0.0)

        self.window = win
        self.label  = label
        self.value  = value

        self.ifaceLabel = elementary.Label(self.window)
        self.ifaceLabel.label_set(self.label)
        self.ifaceLabel.show()

        self.ifaceStatus = elementary.Label(self.window)
        self.ifaceStatus.label_set(self.value)
        self.ifaceStatus.show()

        self.pack_start(self.ifaceLabel)
        self.pack_end(self.ifaceStatus)
        self.show()


class InterfaceEntryBox(elementary.Box):
    """
    Class for Interface info entry
    """

    def entry_get(self):
        return self.ifaceEntry.entry_get()

    def entry_set(self, value):
        return self.ifaceEntry.entry_set(value)

    def __init__(self, win, label, value):
        """
        """

        super(InterfaceEntryBox, self).__init__(win)
        self.horizontal_set(True)

        self.size_hint_weight_set(1.0, 0.0)
        self.size_hint_align_set(-1.0, 0.0)

        self.window = win
        self.label  = label
        self.value  = value

        self.ifaceLabel = elementary.Label(self.window)
        self.ifaceLabel.size_hint_align_set(-1.0, 0.0)
        self.ifaceLabel.label_set(self.label)
        self.ifaceLabel.show()

        self.ifaceEntry = elementary.Entry(self.window)
        self.ifaceEntry.size_hint_align_set(-1.0, 0.0)
        self.ifaceEntry.size_hint_weight_set(1.0, 0.0)
        self.ifaceEntry.single_line_set(True)
        self.ifaceEntry.entry_set(self.value)
        self.ifaceEntry.show()

        self.ifaceEntryFrame = elementary.Frame(self.window)
        self.ifaceEntryFrame.size_hint_align_set(-1.0, 0.0)
        self.ifaceEntryFrame.size_hint_weight_set(1.0, 0.0)
        self.ifaceEntryFrame.style_set("outdent_top")
        self.ifaceEntryFrame.content_set(self.ifaceEntry)
        self.ifaceEntryFrame.show()

        self.pack_start(self.ifaceLabel)
        self.pack_end(self.ifaceEntryFrame)
        self.show()





class UsbNetwork(module.AbstractModule):
    name = _("Usb Network Settings")

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24])
        except:
            print "Error fetching %s ip address" % ifname
            return "unkown"
        return ip


    def get_mac_address(self, ifname):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
            return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
        except:
            print "Error fetching %s MAC address" % ifname
            return "unkown"


    def createView(self):
        self.main = elementary.Box(self.window)

        self.entryUSB0 = InterfaceEntryBox(self.window, _("usb0 IP: "), self.get_ip_address('usb0'))
        self.main.pack_end(self.entryUSB0)

        self.macUSB0 = InterfaceEntryBox(self.window, _("usb0 MAC Address: "), self.get_mac_address('usb0'))
        self.main.pack_end(self.macUSB0)

        return self.main
