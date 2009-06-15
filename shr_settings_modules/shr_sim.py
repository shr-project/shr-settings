import dbus
import module
import elementary

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


"""
- gta01
/sys/devices/platform/s3c2410-i2c/i2c-adapter/i2c-0/0-0008/neo1973-pm-bt.0/
- gta02
/sys/devices/platform/s3c2440-i2c/i2c-adapter/i2c-0/0-0073/neo1973-pm-bt.0/

"""
btModels = [ \
"/sys/devices/platform/s3c2410-i2c/i2c-adapter/i2c-0/0-0008/neo1973-pm-bt.0",
"/sys/devices/platform/s3c2440-i2c/i2c-adapter/i2c-0/0-0073/neo1973-pm-bt.0",
"/sys/bus/platform/devices/neo1973-pm-bt.0"]

class SimMstateContener:
    def __init__(self, bus):
        self.state = 0
        try:
            gsm_sim_obj = bus.get_object( 'org.freesmartphone.ogsmd', '/org/freesmartphone/GSM/Device' )
            self.gsm_sim_iface = dbus.Interface(gsm_sim_obj, 'org.freesmartphone.GSM.SIM')
            self.state = 1
            print "SimMstateContener can connect to dbus"
        except:
            self.state = 0
            print "SimMstateContener can't connect to dbus"

    def getDbusState(self):
        return self.state

    def ListPhonebooks(self):
        if self.state == 0:
            return 0
        else:
            return self.gsm_sim_iface.ListPhonebooks()

    def GetPhonebookInfo(self, a):
        if self.state == 0:
            return 0
        else:
            return self.gsm_sim_iface.GetPhonebookInfo(a)


    def GetMessagebookInfo(self):
        if self.state == 0:
            return 0
        else:
            return self.gsm_sim_iface.GetMessagebookInfo()


    def MessageBookClean(self):
        messageMax = self.GetMessagebookInfo()['last']
        print "MessageBookClean max: "+str(messageMax)
        for i in range(1, (messageMax+1), 1):
            print "remove id: "+str(i)
            try:
                self.gsm_sim_iface.DeleteMessage(i)
            except:
                pass
        print "DONE"


    def PhoneBookClean(self, n ):
        phoneMax = self.GetPhonebookInfo(n)['max_index']
        print "PhoneBookClean max: "+str(phoneMax)
        for i in range(1, (phoneMax+1), 1):
            print "remove id: "+str(i)
            try:
                self.gsm_sim_iface.DeleteEntry(n, i)
            except:
                pass
        print "DONE"
   

class Button2( elementary.Button ):
    def set_name( self, i ):
        self.profile_name = i

    def get_name( self ):
        return self.profile_name

class PhbookInfoFrame(elementary.Frame):
    """ derived from a Frame, this shows phone book statistics.
        It contains a callback function that is called by dbus
        One needs to init the tableobject in which the frames are placed once.
    """
    # class var describing which cell the frame should cover, internally incremented
    table_pos = 1

    #-------------------------------------------------------------------
    def __init__(self, par_tableobj, booktype, par_Simclass):
    #-------------------------------------------------------------------
        """ booktype is a string describing the phone book
            par_Simclass is the instance of the corresp Sim class
        """
        # init class var with table in which frames should go
        self.tableobj = par_tableobj
        self.booktype = booktype
        self.simclass = par_Simclass
        assert self.booktype is not None
        assert self.tableobj == 'elementary.c_elementary.Table'
        # call elementary.Frame.__init__
        super(PhbookInfoFrame, self).__init__(par_tableobj)


    #-------------------------------------------------------------------
    def phonebookinfo_reply_handler(self, phoneBookInfo):
    #-------------------------------------------------------------------
        """ Callback for the 'PhonebookInfo' dbus call.
            Receives info and adds corresponding frame to table.
        """
        print "async book "+ self.booktype +" arrived"
        #frame
        frameBook = elementary.Frame(self.tableobj)
        frameBook.label_set(_("Book ")+ self.booktype)
        (row,col) = divmod(PhbookInfoFrame.table_pos, 2)
        self.tableobj.pack(frameBook, col, row, 1, 1)
        frameBook.size_hint_weight_set(0.5, 0.5)
        frameBook.size_hint_align_set(-1.0, 0.0)
        frameBook.show()

        boxBook = elementary.Box(frameBook)
        boxBook.show()
        frameBook.content_set(boxBook)

        # create a new box for each line and show it
        for (key, val) in phoneBookInfo.iteritems():
           if not key in ('first','min_index'):
                boxS = elementary.Box(boxBook)
                boxS.horizontal_set(True)
                boxS.size_hint_align_set(-1.0, 0.0)
                boxS.show()

                labelN =elementary.Label(boxS)
                labelN.label_set(key)
                labelN.size_hint_align_set(-1.0, -1.0)
                labelN.size_hint_weight_set(1.0, 1.0)
                labelN.show()
                boxS.pack_start(labelN)

                labelV =elementary.Label(boxS)
                labelV.size_hint_align_set(-1.0, 0.0)
                labelV.label_set(str( val ))
                labelV.show()
                boxS.pack_end(labelV)

                boxBook.pack_start( boxS )

        # actions
        boxS = elementary.Box(boxBook)
        boxS.horizontal_set(True)
        boxS.size_hint_align_set(-1.0, 0.0)
        boxS.show()

        # clear TODO
        cleanbt = Button2(boxS)
        cleanbt.set_name( self.booktype )
        cleanbt.clicked = self.simclass.cleanPhoneBookClick
        cleanbt.label_set(_("clean"))
        cleanbt.size_hint_align_set(-1.0, 0.0)
        cleanbt.show()
        boxS.pack_end(cleanbt)

        boxBook.pack_end( boxS )
        # increase table cell for next frame
        PhbookInfoFrame.table_pos += 1


class Sim(module.AbstractModule):
    name = _("SIM settings")
    section = _("Connectivity")
    # no of displayed books, so we can put the next in the right table cell

    def cleanMessageBookClick(self, obj, event, *args, **kargs):
        self.simmc.MessageBookClean()

    def cleanPhoneBookClick(self, obj, event, *args, **kargs):
        name = obj.get_name()
        print "clean phone book: ["+str(name)+"]"
        self.simmc.PhoneBookClean( name )

    #-------------------------------------------------------------------
    def siminfo_reply_handler(self, siminfo):
    #-------------------------------------------------------------------
        """ Callback for the 'SimInfo box' dbus call.
            Receives info and adds corresponding labels.
        """
        print "async SIM info arrived"

        # iterate through all values and display them
        for (key, val) in siminfo.iteritems():
          
            print key+': '+str(val)
            boxS = elementary.Box(self.window)
            boxS.horizontal_set(True)
            boxS.size_hint_align_set(-1.0, 0.0)
            boxS.show()

            labelN =elementary.Label(self.window)
            labelN.label_set(key.replace('_',' ') + ':')
            labelN.size_hint_align_set(-1.0, -1.0)
            labelN.size_hint_weight_set(1.0, 1.0)
            labelN.show()
            boxS.pack_start(labelN)

            labelV =elementary.Label(self.window)
            labelV.size_hint_align_set(-1.0, 0.0)
            try:
              labelV.label_set(val)
            except:
              vall = ''
              for va in val:
                vall = vall + va[1] + '<br>'
              labelV.label_set(vall.replace('"',''))
            labelV.show()
            boxS.pack_end(labelV)

            self.boxSIMInfo.pack_start( boxS )


    #-------------------------------------------------------------------
    def msgbookinfo_reply_handler(self, messBookInfo):
    #-------------------------------------------------------------------
        """ Callback for the 'MessageBookInfo' dbus call.
            Receives info and adds corresponding frame to table.
        """
        print "async Msg book arrived"

        frameBook = elementary.Frame(self.window)
        frameBook.label_set(_("Message book"))
        self.books_table.pack(frameBook, 0, 0, 1, 1)
        frameBook.size_hint_weight_set(1.0, 1.0)
        frameBook.size_hint_align_set(-1.0, -1.0)
        frameBook.show()

        boxBook = elementary.Box(self.window)
        boxBook.show()
        frameBook.content_set(boxBook)

        for (key, val)  in messBookInfo.iteritems():
           # filter out "first", "min_index", they are always 1
           if not key in ('first','min_index'):
                boxS = elementary.Box(self.window)
                boxS.horizontal_set(True)
                boxS.size_hint_align_set(-1.0, 0.0)
                boxS.show()

                labelN =elementary.Label(self.window)
                labelN.label_set(key)
                labelN.size_hint_align_set(-1.0, -1.0)
                labelN.size_hint_weight_set(1.0, 1.0)
                labelN.show()
                boxS.pack_start(labelN)

                labelV =elementary.Label(self.window)
                labelV.size_hint_align_set(-1.0, 0.0)
                labelV.label_set(str( val ))
                labelV.show()
                boxS.pack_end(labelV)

                boxBook.pack_start( boxS )

        # actions
        boxS = elementary.Box(self.window)
        boxS.horizontal_set(True)
        boxS.size_hint_align_set(-1.0, 0.0)
        boxS.show()

        # clear TODO
        cleanbt = elementary.Button(self.window)
        cleanbt.clicked = self.cleanMessageBookClick
        cleanbt.label_set(_("clean"))
        cleanbt.size_hint_align_set(-1.0, 0.0)
        cleanbt.show()
        boxS.pack_end(cleanbt)

        boxBook.pack_end( boxS )


    #-------------------------------------------------------------------
    def dbusasync_error_handler(self, e):
    #-------------------------------------------------------------------
        print "received exception " + str(e)
        #TODO proper error handling

    #-------------------------------------------------------------------
    def createView(self):
    #-------------------------------------------------------------------
        self.guiUpdate = 1
        
        self.simmc = SimMstateContener( self.dbus )
        print "sim dbus state "+str(self.simmc.getDbusState())

        box1 = elementary.Box(self.window)

        # If we can't connect to the right DBus object crap out here
        if self.simmc.getDbusState==0:
            label =elementary.Label(self.window)
            label.label_set(_("Cannot connect to dbus"))
            label.size_hint_align_set(-1.0, 0.0)
            label.show()
            box1.pack_start(label)
            return box1
        
        #from here on we can assume a valid dbus object

        # add the SIM info box
        self.simmc.gsm_sim_iface.GetSimInfo(
          reply_handler = self.siminfo_reply_handler,
          error_handler=self.dbusasync_error_handler
        )

        frameInfo = elementary.Frame(self.window)
        frameInfo.label_set(_("SIM information:"))
        box1.pack_start(frameInfo)
        frameInfo.size_hint_align_set(-1.0, 0.0)
        frameInfo.show()

        self.boxSIMInfo = elementary.Box(self.window)
        frameInfo.content_set(self.boxSIMInfo)

        # table containing all messagebook/phonebook frames
        self.books_table = elementary.Table(box1)
        self.books_table.size_hint_align_set(-1.0, -1.0)
        self.books_table.size_hint_weight_set(1.0, 1.0)

        box1.pack_end(self.books_table)
        self.books_table.show()

        # add message book info
        self.simmc.gsm_sim_iface.GetMessagebookInfo(
	  reply_handler = self.msgbookinfo_reply_handler, 
          error_handler=self.dbusasync_error_handler
        )

        # List phonebook statistics
        phoneBooks = self.simmc.ListPhonebooks()
        # reset table cell pos to 1, so we always start correctly
        PhbookInfoFrame.table_pos = 1
        frames = []
        for b in phoneBooks:
            frame = PhbookInfoFrame(self.books_table, b, self)
            frames.append(frame)
            self.simmc.gsm_sim_iface.GetPhonebookInfo( b,
     	      reply_handler = frame.phonebookinfo_reply_handler, 
              error_handler=self.dbusasync_error_handler
            )

        return box1

    def stopUpdate(self):
        print "SIM desktructor"
        self.guiUpdate = 0
