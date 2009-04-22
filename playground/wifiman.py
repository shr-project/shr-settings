#!/usr/bin/env python
import elementary
import dbus
import e_dbus

def shutdown(obj, event, *args, **kargs):
  elementary.exit()

def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)

def update_networks(networks):
  global li
  global items
  #print "updating network list with: " + str(networks)
  for x in items:
    x.delete()
  items=[]
  for x in networks:
    network = getDbusObject (bus, "org.moblin.connman", x, "org.moblin.connman.Network")
    netprops = network.GetProperties()
    item = li.item_append(netprops['Name'] + " (" + netprops['WiFi.Security']+")", None, None, None)
    items.append(item)
    print "i have network " + x + " with name " + netprops['Name']
  li.go()
  return 1

def onsignal (*args, **kargs):
#  print kargs['signal'] + ' ' + str(args[0]) + ' ' + str(args[1])
  if kargs['signal']=='PropertyChanged':
    if args[0]=='Scanning':
      if args[1]:
        print "Now scanning"
        scanning.show()
      else:
        print "Scan ended"
        scanning.hide()
    elif args[0]=='Networks':
      print "Available networks: " + str(args[1])
      update_networks(args[1])
    else:
      print "Property " + str(args[0]) + " changed to: " + str(args[1])
  else:
    print "Unknown signal: " + str(kargs['signal'])
  return True

elementary.init()

items=[]

mainloop = e_dbus.DBusEcoreMainLoop()
bus = dbus.SystemBus(mainloop=mainloop)

win = elementary.Window("wifiman", elementary.ELM_WIN_BASIC)
win.title_set("SHR WiFi manager")
win.destroy = shutdown
win.show()

bg = elementary.Background(win)
win.resize_object_add(bg)
bg.show()

scanning = elementary.Label(win)
scanning.label_set("Scanning now...")

box = elementary.Box(win)
box.pack_end(scanning)
box.show()

li = elementary.List(win)
li.show()
win.resize_object_add(li)
win.resize_object_add(box)
li.go()

connman = getDbusObject (bus, "org.moblin.connman", "/", "org.moblin.connman.Manager")
properties = connman.GetProperties()

device = ''

for x in properties['Devices']:
  print x
  try:
    xdev = getDbusObject(bus, "org.moblin.connman", x, "org.moblin.connman.Device")
    xprop = xdev.GetProperties()
    if xprop['Type']=='wifi':
       print "we have wifi device!"
       device = x
       dev = xdev
       prop = xprop
  except:
    print x + " failed"

if device!='':
  print "Our device: " + x
  #catch all connman signals. they could be usefull.
  bus.add_signal_receiver(onsignal, bus_name='org.moblin.connman', interface_keyword='iface', member_keyword='signal')
  update_networks(prop['Networks'])
  dev.ProposeScan()

elementary.run()
elementary.shutdown()
