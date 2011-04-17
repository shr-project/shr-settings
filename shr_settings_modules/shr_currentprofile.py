import elementary
import module
import dbus
import os, re

from helper import getDbusObject

# Locale support
import gettext

"""
Notes

 *.size_hint_align_set( horiz_align , vert_align )
    horiz_align:
        -1.0    = default (?)
        -0.5    = right-justified with end at 0.0 position
         0.0    = left-justified
         0.5    = center
         1.0    = right-justified
    vert_align:
        -1.0    =
        -0.5    =
         0.0    =
         0.5    = middle
         1.0    =

 SID Files:
    Magic numbers: +00  = 0x50534944 (PSID)
                        = 0x52534944 (RSID)
    Track Count Location = +0E-0F (1-256)

"""

SND_DIR = "/usr/share/sounds/"

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x

def dbus_ok(*args, **kargs):
    pass

def dbus_err(x, *args, **kargs):
    print str(x)

class FileButton(elementary.Button):
    def set_filename( self, filename ):
        self.filename = filename
        self.label_set(filename)

    def get_filename( self ):
        return self.filename


class ValueLabel(elementary.Label):
    """ Label that displays current timeout """
    def __init__(self, win):
        self._value = None
        super(ValueLabel, self).__init__(win)

    def get_value(self):
        return self._value

    def set_value(self, val):
         self.label_set(str(val))
         self._value = val


class IncDecButton(elementary.Button):
    """
    Button that add/substracts from the value label
    """

    def set_Delta(self, delta):
        self._delta = delta
        self.label_set("{0:+d}".format(delta))


    def get_Delta( self ):
        return self._delta


class PreferenceBox(elementary.Box):
    """
    Parent class for preference item display boxes
    """

    def update(self, value = None):
        """
        This is where each decendant class provides it's own updating code

        Defaults to updating default setup label
        """
        if value == None:
            value = self.dbusObj.GetValue(self.item_name, reply_handler=self.update, error_handler=dbus_err)
        else:
            self.label.label_set(str(value))

    def setup(self):
        """
        This is where each decendant class provides its own look

        Defaults to displaying a label of the current value
        """
#        cur_value = self.dbusObj.GetValue(self.item_name)

        self.label = elementary.Label(self.window)
#        self.label.label_set(str(cur_value))
        self.update()

        self.pack_start(self.label)
        self.label.show()

    def stopUpdate(self):
        self.signal.remove()

    def notify(self, name, value):
        if name == self.item_name:
            self.update(value)

    def __init__(self, win, dbusObj, item_name):
        """
        initialize the box and load objects
        """

        super(PreferenceBox, self).__init__(win)
        self.window = win
        self.item_name = item_name
        self.dbusObj = dbusObj

        ifa = dbusObj
        if isinstance(ifa, tuple):
            ifa = ifa[0]
        self.signal = ifa.connect_to_signal('Notify', self.notify)

        self.setup()


class IncDecButtonBox(PreferenceBox):
    """
    Object which shows an increment/decrement button set to alter int
    Preferences values

    Layout derived taken from shr_device_timeouts.py
    """

    def IncDecButtonClick(self, obj, *args, **kargs):
        """
        Callback function when +-[1,10] timeout buttons have been pressed
        """
        cur_val = self.cur_value
        delta  = obj.get_Delta()
        new_val = max(-1, cur_val + delta)

        self.dbusObj.SetValue(self.item_name,int(new_val), reply_handler=dbus_ok, error_handler=dbus_err)
        self.update(new_val)

    def update(self, value = None):
        """
        Updates the displayed value to the current profile
        """
        if value == None:
            self.cur_value = self.dbusObj.GetValue(self.item_name, reply_handler = self.update, error_handler = dbus_err)
        else:
            self.cur_value = value
            self.value.set_value(self.cur_value) #implicitely sets label too

    def setup(self):
        """
        Function to show a increment/decrement button set to alter int
        Preferences values

        Layout developed from shr_device_timeouts.py
        """

        self.horizontal_set(True)

#        self.cur_value = self.dbusObj.GetValue(self.item_name)

        self.value  = ValueLabel(self.window)
        self.value.size_hint_align_set(0.5, 0.5)
#        self.value.set_value(self.cur_value) #implicitely sets label too
        self.update()
        self.value.show()

        boxbox = elementary.Box(self.window)
        boxbox.pack_start(self.value)
        boxbox.size_hint_weight_set(1.0, 1.0)
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


class RadioOnOffBox(PreferenceBox):
    """
    Object which shows an On/Off Radio Button
    object for Boolean Preferences items

    """

    togglegroup = {}

    def OnOffClick(self, obj, *args, **kargs):
        """
        Callback function either radio button has been selected
        """
        self.dbusObj.SetValue(self.item_name,bool(obj.value_get()), reply_handler=dbus_ok, error_handler=dbus_err)
        self.update(bool(obj.value_get()))

    def update(self, value = None):
        """
        Updates the displayed value to the current profile
        """
        if value == None:
            self.dbusObj.GetValue(self.item_name, reply_handler=self.update, error_handler=dbus_err)
        else:
            state = value
            self.togglegroup[self.item_name].value_set(state)

    def setup(self):
        """
        Function to show a radio button set to alter bool
        Preferences values
        """
#        state = self.dbusObj.GetValue(self.item_name)

        self.horizontal_set(True)

        radioOn = elementary.Radio(self.window)
        radioOn.label_set(_("On"))
        radioOn.size_hint_weight_set(1.0, 0.0)
        radioOn.size_hint_align_set(0.5, 0.0)
        radioOn.state_value_set(True)
        radioOn._callback_add("changed", self.OnOffClick)
        radioOn.show()

        radioOff = elementary.Radio(self.window)
        radioOff.label_set(_("Off"))
        radioOff.size_hint_weight_set(1.0, 0.0)
        radioOff.size_hint_align_set(0.5, 0.0)
        radioOff.state_value_set(False)
        radioOff._callback_add("changed", self.OnOffClick)
        radioOff.show()

        self.togglegroup[self.item_name] = radioOn
        radioOff.group_add(self.togglegroup[self.item_name])

        self.update()
#        self.togglegroup[self.item_name].value_set(state)

        self.pack_start(radioOn)
        self.pack_end(radioOff)

        self.show()


class ToneChangeBox(PreferenceBox):
    """
    Object which shows a file selctor object to allow for changing of string
    Preferences items, specifically 'message-tone' and 'ring-tone'
    """

    def destroy(self, obj, *args, **kargs):
        """
        Callback function to destroy the FileListBox window
        """
        self.FLBWin.hide()

    def ChangeTone(self, obj, *args, **kargs):
        """
        Callback function to change the tone file name in the settings
        """
        self.tonefile = str(obj.get_filename())
        self.dbusObj.SetValue(self.item_name, self.tonefile, reply_handler=dbus_ok, error_handler=dbus_err)
        self.destroy(obj, event)

        self.update(self.tonefile)

    def FileListBox(self, obj, *args, **kargs):
        """
        Callback function to display the file selection window
        """
        self.FLBWin = elementary.Window(_("Change ringtone"),elementary.ELM_WIN_BASIC)
        bg = elementary.Background(self.FLBWin)
        self.FLBWin.resize_object_add(bg)
        self.FLBWin.title_set(_("Change ringtone"))
        bg.show()
        self.FLBWin.autodel_set(1)

        box = elementary.Box(self.FLBWin)

        fr = elementary.Frame(self.FLBWin)
        fr.label_set(_("Select ringtone"))
        lab = elementary.Label(self.FLBWin)
        lab.label_set(_("Ringtones are placed in /usr/share/sounds/"))
        fr.content_set(lab)
        lab.show()
        fr.show()
        fr.size_hint_align_set(-1.0, 0.0)
        box.pack_start(fr)

        scr = elementary.Scroller(self.FLBWin)
        scr.size_hint_weight_set(1.0, 1.0)
        scr.size_hint_align_set(-1.0, -1.0)
        scr.bounce_set(0, 0)
        box.pack_end(scr)
        exitbtn = elementary.Button(self.FLBWin)
        exitbtn.label_set(_("Quit"))
        exitbtn.size_hint_weight_set(1.0, 0.0)
        exitbtn.size_hint_align_set(-1.0, -1.0)
        exitbtn._callback_add('clicked', self.destroy)
        box.pack_end(exitbtn)
        self.FLBWin.resize_object_add(box)
        box.show()
        scr.show()
        exitbtn.show()
        self.FLBWin.show()

        box1 = elementary.Box(self.FLBWin)
        scr.content_set(box1)
        box1.size_hint_weight_set(1.0, 0.0)
        box1.show()

        sndFiles = [f for f in os.listdir("/usr/share/sounds") if os.path.isfile("/usr/share/sounds/"+f)]

        for filename in sndFiles:
            filebtn = FileButton(self.FLBWin)
            filebtn.set_filename(filename)
            filebtn._callback_add('clicked', self.ChangeTone)
            filebtn.size_hint_align_set(-1.0, 0.0)
            box1.pack_end(filebtn)
            filebtn.show()

    def SidButtonClick(self, obj, *args, **kargs):
        """
        Callback function when +-1 SID track buttons have been pressed
        """
        cur_val = self.sidValue
        delta  = obj.get_Delta()
        new_val = max(-1, cur_val + delta)
        if self.sidTracks:
            if new_val > self.sidTracks:
                self.sidValue = 1
            elif new_val < 1:
                self.sidValue = self.sidTracks
            else:
                self.sidValue = new_val

        new_tone = self.tonefile + ";tune=" + str(self.sidValue)
        print "setting:", new_tone

        self.dbusObj.SetValue(self.item_name, new_tone, reply_handler=dbus_ok, error_handler=dbus_err)
        self.update(new_tone)

    def PlayTone(self, obj, *args, **kargs):
        # prep play parameters
        if self.sidValue:
            # Need to specificy the sid track
            play_tone = self.tonepath + ";tune=" + str(self.sidValue)
            # Need to specificy the sid length (Maybe infer from the file?)
            duration = 60 # As we have Stop button, we can let it playing long
        else:
            play_tone = self.tonepath
            duration = 0

        # Stop the tone if playing
        if self.playStatus:
            print self.item_name,"- Stopping:", self.tonefile
            self.AudioDbusObj.StopAllSounds(reply_handler=dbus_ok, error_handler=dbus_err )

        # Play the tone
        print self.item_name,"- Playing:", self.tonefile
        self.AudioDbusObj.PlaySound(play_tone, 0, duration, reply_handler=dbus_ok, error_handler=dbus_err)

    def StopTone(self, obj, *args, **kargs):
        """
        Stop a playing tone
        """
        # Stop the tone if playing
        if self.playStatus:
            print self.item_name,"- Stopping:", self.tonefile
            self.AudioDbusObj.StopAllSounds(reply_handler=dbus_ok, error_handler=dbus_err )

    def StartStopSound(self, id, status, properties):
        """
        Signal handler for SoundStatus signals

        Only a status of 'stopped' is considered
        """
        # Debug output
        print self.item_name,"- Status 'id','status:", id, status

        tone = self.tonepath + ";tune=" + str(self.sidValue) if self.sidValue else self.tonepath

        if id == tone:
            if status == 'stopped': # tone has stopped
                # Reset Play button
##                print "Stopped: Resetting to 'Play'"
                self.testBtn.label_set(_("Play"))
                self.testBtn._callback_add('clicked', self.PlayTone)
                self.playStatus = False
            elif status == 'playing': # tone is playing
                # Reset Play button
##                print "Playing: Resetting to 'Stop'"
                self.testBtn.label_set(_("Stop"))
                self.testBtn._callback_add('clicked', self.StopTone)
                self.playStatus = True

    def updateButtons( self, sid = False ):

        try:
            self.sidDnBtn.delete()
            self.sidUpBtn.delete()
            del self.sidDnBtn
            del self.sidUpBtn
        except:
            pass

        try:
            self.testBtn.delete()
            self.changeBtn.delete()
            del self.testBtn
            del self.changeBtn
        except:
            pass

        # Tone Test button
        self.testBtn = elementary.Button(self.window)
        self.testBtn.label_set(_("Play"))
        self.testBtn.size_hint_align_set(-1.0, 0.0)
        self.testBtn.size_hint_weight_set(1.0, 0.0)
        self.testBtn._callback_add('clicked', self.PlayTone)
        self.testBtn.show()

        # Tone change button
        self.changeBtn = elementary.Button(self.window)
        self.changeBtn.label_set(_("Change"))
        self.changeBtn.size_hint_align_set(-1.0, 0.0)
        self.changeBtn.size_hint_weight_set(1.0, 0.0)
        self.changeBtn._callback_add('clicked', self.FileListBox)
        self.changeBtn.show()

        if sid:
            # Controls for sid files
            self.sidDnBtn = IncDecButton(self.window)
            self.sidDnBtn.set_Delta( -1 )
            self.sidDnBtn._callback_add('clicked', self.SidButtonClick)
            self.sidDnBtn.size_hint_align_set(-1.0, 0.0)
            self.sidDnBtn.show()

            self.sidUpBtn = IncDecButton(self.window)
            self.sidUpBtn.set_Delta( 1 )
            self.sidUpBtn._callback_add('clicked', self.SidButtonClick)
            self.sidUpBtn.size_hint_align_set(-1.0, 0.0)
            self.sidUpBtn.show()

        # pack the button box
        self.buttonBox.pack_start(self.testBtn)
        if sid:
            self.buttonBox.pack_end(self.sidDnBtn)
            self.buttonBox.pack_end(self.sidUpBtn)
        self.buttonBox.pack_end(self.changeBtn)

    def update(self, value = None):
        """
        Updates the displayed value to the current profile
        """
        if value == None:
            self.dbusObj.GetValue(self.item_name, reply_handler=self.update, error_handler=dbus_err)
            return False
        else:
            self.tonefile = str(value)
        self.tonepath = SND_DIR + self.tonefile
        self.label.label_set(self.tonefile)

        isSid = re.match(r'(.*sid)(;tune=(.+))?',self.tonefile)

        if isSid:
            self.tonefile = str(isSid.group(1))
            self.tonepath = SND_DIR + self.tonefile

            try:
                sidFile = open(self.tonepath, "rb")
                sidFile.seek(0x0E)
                self.sidTracks = int("0x"+repr(sidFile.read(2)).replace("'","").replace('\\x',''),16)
                sidFile.close()

                if isSid.group(3):
                    self.sidValue = int(isSid.group(3))
                else:
                    self.sidValue = 1

                self.label.label_set("{0}  {1}/{2}".format(self.tonefile,self.sidValue, self.sidTracks))

                self.updateButtons( True )
            except:
                self.sidValue = 0
                self.sidTracks = 0
                self.updateButtons( False )
        else:
            self.sidValue = 0
            self.sidTracks = 0
            self.updateButtons( False )

    def stopUpdate(self):
        self.asignal.remove()
        PreferenceBox.stopUpdate(self)

    def setup(self):
        """
        Function to show the current profile tone and a button to trigger
        FileListBox to set the tone Preferences values
        """

        self.playStatus = False
        self.dbusObj, self.AudioDbusObj = self.dbusObj
        self.asignal = self.AudioDbusObj.connect_to_signal("SoundStatus",
            self.StartStopSound)

        # Tone name label
        self.label = elementary.Label(self.window)
        self.label.size_hint_weight_set(1.0, 0.0)
        self.label.size_hint_align_set(0.5, 0.5)
        self.label.show()

        # Button container
        self.buttonBox = elementary.Box(self.window)
        self.buttonBox.horizontal_set(True)
        self.buttonBox.size_hint_align_set(-1.0, 0.0)
        self.buttonBox.size_hint_weight_set(1.0, 0.0)
        self.buttonBox.show()

        # pack the main box
        self.pack_start(self.label)
        self.pack_end(self.buttonBox)

        self.show()
        self.update()

class CurrentProfile(module.AbstractModule):
    name = _("Current profile settings")

    def error(self):
        label = elementary.Label(self.window)
        label.label_set(_("Couldn't connect to FSO"))
        label.show()
        self.main.pack_start(label)

    def profileChanged(self, profile):
        """
        Signal Handler for profile updates
        """
        self.update()

    def stopUpdate(self):
#        self.signal.remove()
        for i in self.contents:
            self.contents[i].stopUpdate()

    def update(self):
        keys = self.dbusObj.GetKeys()
        keys.sort()
        for i in keys:
            typ = self.dbusObj.GetType(i)
            profilable = self.dbusObj.IsProfilable(i)

            if profilable:
                try:
                    # If self.contents[i] exists, then run the update()
                    # for that object
                    self.contents[i].update()
                except KeyError:
                    # If self.contents[i] fails, assume the object doesn't
                    # exist and create it
                    frame = elementary.Frame(self.window)
                    frameTitle = str(i).replace("-"," ").title()
                    frame.label_set(frameTitle)

                    if i=='ring-tone' or i == 'message-tone':
                        box = ToneChangeBox(self.window, (self.dbusObj, self.AudioDbusObj), i)
                    elif typ == 'bool':
                        box = RadioOnOffBox(self.window, self.dbusObj, i)
                    elif typ == 'int':
                        box = IncDecButtonBox(self.window, self.dbusObj, i)
                    else:
                        box = PreferenceBox(self.window, self.dbusObj, i)

                    self.contents[i] = box
                    frame.content_set(box)
                    frame.size_hint_align_set(-1.0, 0.0)
                    frame.size_hint_weight_set(1.0, 1.0)
                    frame.show()

                    self.main.pack_start(frame)
        return 1

    def createView(self):
        self.main = elementary.Box(self.window)
        self.main.size_hint_weight_set(1.0, 1.0)

        try:
            # Preferences.Service DBus interface
            self.dbusObj = getDbusObject(self.dbus,
                "org.freesmartphone.opreferencesd",
                "/org/freesmartphone/Preferences/phone",
                "org.freesmartphone.Preferences.Service")

            # Preferences DBus interface (For Signals)
#            self.SignalsDbusObj = getDbusObject(self.dbus,
#                "org.freesmartphone.opreferencesd",
#                "/org/freesmartphone/Preferences",
#                "org.freesmartphone.Preferences" )
#            self.signal = self.SignalsDbusObj.connect_to_signal("Notify",
#                self.profileChanged)

            # Audio DBus interface (For Ringtone testing)
            self.AudioDbusObj = getDbusObject(self.dbus,
                "org.freesmartphone.odeviced",
                "/org/freesmartphone/Device/Audio",
                "org.freesmartphone.Device.Audio" )

            self.contents = {} # named array of contents, for updating
            self.update()
        except:
            self.error()

        return self.main
