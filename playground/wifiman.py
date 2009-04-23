#!/usr/bin/env python
import elementary
import dbus
import e_dbus

#def dialog(content):
#  global win
#  dia = elementary.Inwin(win)
#  dia.content_set(content)
#  win.resize_object_add(dia)
#  return dia

def shutdown(obj, event, *args, **kargs):
  elementary.exit()

def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)

def error_callback(err):
  print str(err)

def disconnect(obj, event, networkbus, *args, **kargs):
  print "disconnect"
  networkbus.Disconnect(reply_handler=connect_callback,error_handler=error_callback)
  disconnecting = elementary.Label(pager)
  disconnecting.label_set("Disconnecting...")
  disconnecting.show()
  box = elementary.Box(pager)
  box.pack_end(disconnecting)
  box.show()
  pager.content_push(box)
  #update_networks(dev.GetProperties()['Networks'])
  #dev.ProposeScan()

def connect_callback():
  print "connect_callback()"
  #pager.content_pop()
  #update_networks(dev.GetProperties()['Networks'])
  #dev.ProposeScan()  

def get_passphrase(obj, event, array, *args, **kargs):
  pager.content_pop()
  entry=array[1]
  networkbus=array[0]
  networkbus.SetProperty('WiFi.Passphrase','YOUR-PASSPHRASE') # hardcode your passphrase here
  networkbus.Connect(reply_handler=connect_callback,error_handler=error_callback)

def request_for_passphrase(networkbus):
  box=elementary.Box(pager)
  label = elementary.Label(pager)
  label.label_set("Please enter passphrase (unimplemented :P)")
  label.show()
  box.pack_end(label)
  button = elementary.Button(pager)
  button.label_set("Connect")
  box.pack_end(button)
  button.show()
  entry = elementary.Entry(pager)
  button._callback_add("clicked", (get_passphrase, [networkbus, entry]))
  pager.content_push(box)

def connect(obj, event, networkbus, *args, **kargs):
  network = networkbus.GetProperties()
  print "connecting to " + network['Name'] + "..."
  connecting = elementary.Label(pager)
  try:
    connecting.label_set("Connecting with "+ network['Name'] +"...")
  except:
    connecting.label_set("Connecting with hidden network...")

  encryption = elementary.Label(pager)
  encryption.label_set("Encryption type: " + network['WiFi.Security'])

  macaddress = elementary.Label(pager)
  macaddress.label_set("Access point address: " + network['Address'])

  strength = elementary.Label(pager)
  strength.label_set("Signal strength: " + str(int(network['Strength'])) + "%")

  btn_disconnect = elementary.Button(pager)
  btn_disconnect.label_set("Disconnect")
  btn_disconnect._callback_add("clicked", (disconnect, networkbus))

  box = elementary.Box(pager)
  box.show()                  
  box.pack_end(connecting)
  box.pack_end(encryption)
  box.pack_end(macaddress)
  box.pack_end(strength)
  box.pack_end(btn_disconnect)
  connecting.show()
  encryption.show()
  macaddress.show()
  strength.show()
  btn_disconnect.show()
  scanpage = pager.content_push(box)

  #networkbus.SetProperty('WiFi.Passphrase','YOUR-PASSPHRASE')
  if network['WiFi.Security']=='None':
    networkbus.Connect(reply_handler=connect_callback,error_handler=error_callback)
  else:
    try:
      print network['WiFi.Passphrase']
      networkbus.Connect(reply_handler=connect_callback,error_handler=error_callback)
    except:
      request_for_passphrase(networkbus)

def update_networks(networks):
  global items
  #print "updating network list with: " + str(networks)
  for x in items:
    x.delete()
  items=[]
  for x in networks:
    network = getDbusObject (bus, "org.moblin.connman", x, "org.moblin.connman.Network")
    netprops = network.GetProperties()
    but = elementary.Button(win)
    if netprops['Connected']:
      but.label_set("Disconnect")
      but._callback_add("clicked", (disconnect, network))
    else:
      but.label_set("Connect")
      but._callback_add("clicked", (connect, network))
    encryption = netprops['WiFi.Security']
    try:
      name=netprops['Name']
    except:
      name="*hidden SSID*"
    try:
      strength=", "+str(int(netprops['Strength']))+"%"
    except:
      strength=''
    item = li.item_append(name + " (" + encryption + strength +")", None, but, None)
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
        #scanning = elementary.Label(pager)
        #scanning.label_set("Scanning now...")

        #box = elementary.Box(pager)
        #box.show()
        #box.pack_end(scanning)
        #scanning.show()
        #scanpage = pager.content_push(box)
      else:
        print "Scan ended"
        #pager.content_pop()
    elif args[0]=='Networks':
      print "Available networks: " + str(args[1])
      update_networks(args[1])
    elif args[0]=='Connected':
      pager.content_pop()
      update_networks(dev.GetProperties()['Networks'])
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

#scanning = dialog(scanningl)

box = elementary.Box(win)
box.show()

li = elementary.List(win)
li.show()

pager = elementary.Pager(win)
pager.show()
win.resize_object_add(pager)
pager.content_push(li)


box.pack_end(scanning)
#win.resize_object_add(box)
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
  try:
    dev.ProposeScan()
  except:
    print "scan failed"

elementary.run()
elementary.shutdown()
