import elementary
import module
import os
import shutil

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
    iface = 'usb0'
    updating = False #lock for tmp file

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', self.iface[:15])
            )[20:24])
        except:
            print "Error fetching %s ip address" % self.iface
            return "unkown"
        return ip


    def get_mac_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', self.iface[:15]))
            return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
        except:
            print "Error fetching %s MAC address" % self.iface
            return "unkown"

    def save_ip_address(self, ip):
        etcfile = "/etc/network/interfaces"
        tmpfile = "/tmp/shr-settings-network-interfaces"
        f = open(etcfile, "r+")
        fout = open(tmpfile, "w+")
        while True:
            line = f.readline()
            if line=="": #TODO: close+remove tmp file
                f.close()
                fout.close()
                os.remove(tmpfile)
                return False
            fout.write(line)
            li = line.strip('\t\n').split(' ')
            if len(li)>1 and li[0]== "iface" and li[1]==self.iface:
                break

        #if we arrive here, it's because we are in the wanted iface block:
        while True:
            line = f.readline()
            li = line.strip('\t\n').split(' ')
            if line=="" or li[0]=="iface": #(EOF) or (we got to next iface block, exit)
                f.close()
                fout.close()
                os.remove(tmpfile)
                return False
            if li[0]=="address": #hey, we got the interesting line!
                line = line.replace(li[1],ip)
                fout.write(line)
                break
            fout.write(line)

        #if we arrive here,we've changed the ip. finish copying the file, save it and return true.
        while True:
            line = f.readline()
            if line=="":
                break
            fout.write(line)

        f.close()
        fout.close()
        shutil.move(tmpfile, etcfile)
        return True


    def setIP(self, obj, *args, **kwargs):

       if self.updating == True:
           print "Please, wait for the last ip update to complete before trying another time\n"
           return #don't update if there's a callback still running

       self.updating = True

       ip = self.entryUSB0.ifaceEntry.entry_get()
       print "Setting ip on interface "+ self.iface + " to "+ ip +"\n"
       if self.save_ip_address(ip)==True:
           print "IP saved successfully to /etc/network/interfaces\n"
       else:
           print "Error saving new ip to /etc/network/interfaces !\n"
       print "Running ifconfig... "
       ret = os.system("ifconfig "+self.iface+" "+ip)
       if ret:
           print "Error executing: ifconfig "+self.iface+" "+ip+"\n"
       else:
           print "Done\n"

       self.updating = False


    def createView(self):
        self.main = elementary.Box(self.window)

        self.entryUSB0 = InterfaceEntryBox(self.window, _(self.iface+" IP: "), self.get_ip_address())
        self.main.pack_end(self.entryUSB0)

        self.macUSB0 = InterfaceEntryBox(self.window, _(self.iface+" MAC Address: "), self.get_mac_address())
        self.main.pack_end(self.macUSB0)

        bt = elementary.Button(self.window)
        bt.label_set(_('Save IP'))
        bt.size_hint_weight_set(1.0, 0.0)
        bt.size_hint_align_set(-1.0, 0.0)
        bt._callback_add('clicked', self.setIP)
        self.main.pack_end(bt)
        bt.show()

        return self.main
