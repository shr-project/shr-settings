import elementary, module, os, dbus
from datetime import datetime
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


def getDbusObject (bus, busname , objectpath , interface):
        dbusObject = bus.get_object(busname, objectpath)
        return dbus.Interface(dbusObject, dbus_interface=interface)


#-------------------------------------------------------------------
class SatDetails():
    """ Displays a window with GPS details """
    def __init__(self, parent):
       self.satlab = [] #contains the satellite labels
       self.win = elementary.Window("sat-details", elementary.ELM_WIN_BASIC)
       self.win.title_set(_("Satellite details"))
       self.win.show()
       self.win.destroy = self.destroy

       bg = elementary.Background(self.win)
       bg.show()
       self.win.resize_object_add(bg)

       self.box = elementary.Box(self.win)

       self.tab = elementary.Table(self.win)
       self.tab.size_hint_weight_set(1.0, 1.0)
       self.tab.size_hint_align_set (-1.0, -1.0)
       self.tab.show()
       
       self.box.pack_start(self.tab)

       self.quit_button = elementary.Button(self.win)
       self.quit_button.label_set(_("Quit"))
       self.quit_button.size_hint_weight_set(1.0, 0.0)
       self.quit_button.size_hint_align_set(-1.0, -1.0)
       self.quit_button.clicked = self.quit
       self.quit_button.show()
       ic = elementary.Icon(self.quit_button)
       ic.file_set( "/usr/share/pixmaps/icon_quit.png" )
       ic.smooth_set(1)
       ic.scale_set(0, 0)
       self.quit_button.icon_set(ic)



       self.box.pack_end(self.quit_button)
    
       self.box.show()
       self.win.resize_object_add(self.box)

    def update(self, sats):
       print "update satellites"
       sats.sort()
       for row in range(0,12):
         if len(self.satlab) <= row:
             self.satlab.append(elementary.Label(self.tab))
             self.satlab[row].size_hint_align_set (-1.0, -1.0)
             self.satlab[row].show()
             self.tab.pack(self.satlab[row], 1, row, 1, 1)

         if row < len(sats):
           (prn, inuse, ele, azi, srn) = sats[row]
           if inuse:
               self.satlab[row].color_set(1,100,1,200)
           else:
               self.satlab[row].color_set(100,1,1,100)
           self.satlab[row].label_set("%d (%d,%d) %d" % (prn, ele, azi, srn))

         else:
           # delete empty rows 
           self.satlab[row].label_set("")

    def destroy(self, win, *args, **kargs):
       win.delete()
       self.win = None
       del self

    def quit(self,win, *args, **kargs):
       self.destroy(self.win)

#-------------------------------------------------------------------
class GpsInfoBox(elementary.Table):
    """ Displays a box with GPS and updates it. Extents elementary.Table """

    sigMatch = None  #Contains instance variable with signal listener
    items =  [{'cap':_('Time'), 'iface':'org.freedesktop.Gypsy.Time', 'method':'GetTime', 'signal':'TimeChanged'},
              {'cap':_('Fix'), 'iface':'org.freedesktop.Device', 'method':'GetFixStatus', 'signal':'FixStatusChanged'},
              {'cap':_('Lat'), 'iface':'org.freedesktop.Gypsy.Position', 'signal': 'PositionChanged', 'method':'GetPosition'},
              {'cap':_('Lon'), 'signal': 'LonChanged'},     # set with Lat
              {'cap':_('Alt'), 'signal': 'AltChanged'},     # set with Lat
              {'cap':_('Accuracy'), 'iface':'org.freedesktop.Gypsy.Accuracy', 'signal': 'AccuracyChanged', 'method':'GetAccuracy'},
              {'cap':_('Satellites'), 'iface':'org.freedesktop.Gypsy.Satellites', 'signal': 'SatellitesChanged', 'method':'GetSatellites'},
              {'cap':_('Heading'), 'iface':'org.freedesktop.Gypsy.Course', 'signal': 'CourseChanged', 'method':'GetCourse'},
              {'cap':_('Speed'), 'signal': 'SpeedChanged'}, # set with Heading
              {'cap':_('Descend'), 'signal': 'ClimbChanged'}, # set with Heading
             ]

    #TODO start/stop updating with updateGUI var
    #TODO on init fill in values once (at least 'fix') and not only when changed
    #use org.freedesktop.Gypsy.Device.GetConnectionStatus == True

    def cb_show_sat_details(self, bt, event, *args):
        self.satdetails = SatDetails(self)
        if self.values.has_key('sats'):
            self.satdetails.update(self.values['sats'])

    def on_gypsy_signal(self, *args, **kwargs):
        signal = kwargs['signal']

        # Timestamp has changed
        if signal == 'TimeChanged':
            self.values['tstamp'] = args[0]
            t = datetime.utcfromtimestamp(self.values['tstamp']).strftime('%H:%M:%S')
            self.value_labels[signal].label_set(t)

        # Course has changed
        elif signal == 'CourseChanged':
            #args: validity bitfield, tstamp, speed, in knots, heading, -climb
            for (i, val) in enumerate([
                                       'SpeedChanged','CourseChanged',
                                       'ClimbChanged'
                                      ]):
                # if the bitfield indicates a valid value
                if args[0] & (1 << i):
                    # then update
                    self.values[val] = args[i+2]
                    self.value_labels[val].label_set(str(round(args[i+2],2)))

        # Position has changed
        elif signal == 'PositionChanged':
            #args: validity bitfield, tstamp, lat, lon, alt
            for (i, val) in enumerate([
                                       'PositionChanged','LonChanged',
                                       'AltChanged'
                                      ]):
                # if the bitfield indicates a valid value
                if args[0] & (1 << i):
                    # then update
                    self.values[val] = args[i+2]
                    self.value_labels[val].label_set(str(round(args[i+2],2)))

        #Accuracy has changed
        elif signal == 'AccuracyChanged':
            #args: validity bitfield, pdop, hdop, vdop
            label_str = []
            for (i,val) in enumerate(['pdop','hdop','vdop']):
                # if the bitfield indicates a valid value
                if args[0] & (1 << i):
                    self.values[val] = args[i+1]
                label_str.append(str(round(self.values[val],1)))

            # update label
            self.value_labels[signal].label_set('/'.join(label_str))

        # FixStatus has changed
        elif signal == 'FixStatusChanged':
            #args: 0: invalid 1:no fix 2:2d fix 3:3d fix
            status = ['invalid','no fix','2D fix', '3D fix']
            # update label
            self.value_labels[signal].label_set(status[args[0]])

        # Satellites have changed
        elif signal == 'SatellitesChanged':
            #args: array(SVID, in_use, Elev, Azim, CNO)
            self.values['sats'] = satellites = args[0]
            inuse = filter(lambda x: x[1] == True, satellites)
            #satnums = map(lambda x: x[0], inuse)
            #satnums.sort()
            #sats = '/' + ','.join(map(lambda x: str(x), satnums))
            total = str(len(satellites))
            self.value_labels[signal].label_set(str(len(inuse)) + '/' + total)
            #update the satellite detail window if necessary
            if self.satdetails and self.satdetails.win: 
                self.satdetails.update(satellites)

        else:
            print "unhandled signal"
            print str(args)
            print str(kwargs)

    def __init__(self, parent, dbus):
	self.values = dict(zip(['pdop','hdop','vdop'],[None]))
        """ contains items['name']=value mapping)"""
        self.value_labels = {}
        """ contains items['signal']=valuelabel mapping """
        self.satdetails = None # widget that displays sat details

        self.gypsy = dbus.get_object('org.freedesktop.Gypsy', '/org/freedesktop/Gypsy')
        super(GpsInfoBox, self).__init__(parent)
    
        # create a 'caption' and a 'value' label for all values in table cells
        for (i, item) in enumerate(GpsInfoBox.items):
            # put caption label in cell
            cap_l = elementary.Label(self)
            cap_l.size_hint_align_set(-1.0, 0.0)
            cap_l.label_set(item['cap'] + ':')
            (row, col) = divmod(i,2)
            self.pack(cap_l, col*2, row, 1, 1)
            cap_l.show()

            # put value label in cell
            val_l = elementary.Label(self)
            val_l.size_hint_align_set(-1.0, 0.0)
            cap_l.size_hint_weight_set(1.0, -1.0)
            val_l.label_set('<i>unknown</i>')
            val_l.show()
            self.pack(val_l, col*2 +1, row, 1, 1)
            self.value_labels[item['signal']] = val_l

        row = len(GpsInfoBox.items) // 2 + 1
        sat_details_bt = elementary.Button(self)
        sat_details_bt.label_set(_("Satellite details"))
        sat_details_bt.show()
        sat_details_bt.clicked = self.cb_show_sat_details
        self.pack(sat_details_bt, 1, row, 2, 1)
        
        # catch all gypsy signals and udate values            
        self.sigMatch = dbus.add_signal_receiver(self.on_gypsy_signal, bus_name='org.freedesktop.Gypsy', interface_keyword='iface', member_keyword='signal')

    def stopUpdate(self):
        # if we listen to all gypsy signals, remove those listeners now
        if self.sigMatch != None:
            self.sigMatch.remove()

#-------------------------------------------------------------------
class Gps(module.AbstractModule):
    """ Main GPS Module """
    name = _("GPS settings")

    def error(self, result):
        print "async dbus error"

    def callback(self):
        print "async dbus callback"

    def rempickle(self, obj, event, *args, **kargs):
        os.system("rm /etc/freesmartphone/persist/ogpsd.pickle")
        obj.hide()

    def isEnabled(self):
        return True
    
    def power_handle(self, obj, event, *args, **kargs):
       # if ResourceState already equals off/on setting do nothing
       if self.gps.GetResourceState("GPS") == obj.state_get():
            return 0
       if obj.state_get(): 
           self.gps.SetResourcePolicy("GPS","enabled",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(1)
       else:
           self.gps.SetResourcePolicy("GPS","disabled",reply_handler=self.callback,error_handler=self.error)
           obj.state_set(0)


    def res_handle(self, obj, event, *args, **kargs):
        if obj.state_get():
            # slider has been moved to 'Auto'
            self.gps.SetResourcePolicy("GPS","auto",reply_handler=self.callback,error_handler=self.error)
            self.toggle1.hide()
        else:
            # slider has been moved to 'Manual'
            if self.gps.GetResourceState("GPS"):
                self.gps.SetResourcePolicy("GPS","enabled",reply_handler=self.callback,error_handler=self.error)
                self.toggle1.state_set(1)
            else:
                self.gps.SetResourcePolicy("GPS","disabled",reply_handler=self.callback,error_handler=self.error)
                self.toggle1.state_set(0)
            self.toggle1.show()

    def createView(self):
        try:
            self.gps = getDbusObject (self.dbus, "org.freesmartphone.ousaged", "/org/freesmartphone/Usage", "org.freesmartphone.Usage") 
        except:
            label = elementary.Label(self.window)
            label.label_set(_("can't connect to dbus"))
            return label

        box1 = elementary.Box(self.window)

        toggle0 = elementary.Toggle(self.window)
        toggle0.label_set(_("GPS radio policy:"))
        toggle0.size_hint_align_set(-1.0, 0.0)
        toggle0.states_labels_set(_("Auto"),_("Manual"))
        toggle0.changed = self.res_handle
        box1.pack_start(toggle0)
        toggle0.show()

        self.toggle1 = elementary.Toggle(self.window)
        self.toggle1.label_set(_("Radio:"))
        self.toggle1.size_hint_align_set(-1.0, 0.0)
        self.toggle1.states_labels_set(_("On"),_("Off"))
        self.toggle1.changed = self.power_handle
        box1.pack_end(self.toggle1)

        gpspolicy =  self.gps.GetResourcePolicy("GPS")
        if gpspolicy == "auto":
            toggle0.state_set(1)
            self.toggle1.hide()
        else:
            toggle0.state_set(0)
            self.toggle1.show()
        gpsstate =  self.gps.GetResourceState("GPS")
        self.toggle1.state_set(gpsstate)

        gpsinfo_f = elementary.Frame(box1)
        gpsinfo_f.label_set('GPS info')
        gpsinfo_f.size_hint_align_set(-1.0, 0.0)
        gpsinfo_f.size_hint_weight_set(1.0, 1.0)
        gpsinfo_f.show()

        self.gpsinfo = GpsInfoBox(gpsinfo_f, self.dbus)
        self.gpsinfo.show()
        gpsinfo_f.content_set(self.gpsinfo)
        box1.pack_end(gpsinfo_f)

        if os.path.exists("/etc/freesmartphone/persist/ogpsd.pickle"):
            picklebtn = elementary.Button(self.window)
            picklebtn.label_set(_("Remove AGPS data"))
            box1.pack_end(picklebtn)
            picklebtn.size_hint_align_set(-1.0, 0.0)
            picklebtn.clicked = self.rempickle
            picklebtn.show()
        
        return box1

    def stopUpdate(self):
        """ stop the GUI update and remove signal handlers and such """
        # remove the gypsy signal listeners
        self.gpsinfo.stopUpdate()
