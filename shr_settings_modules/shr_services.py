import dircache, re
import module, elementary, os


class ButtonServer( elementary.Button ):
    def set_osCmd( self, cmd ):
        self.osCmd = cmd

    def get_osCmd( self ):
        return self.osCmd

class Services(module.AbstractModule):
    name = "Services"

    def reloadbtClick(self, obj, event, *args, **kargs):
        self.winser.hide()
        del self.winser
        print "Services reloadbtClick [info]"
        self.sssbtClick( obj, event)

    def destroyInfo(self, obj, event, *args, **kargs):
        self.winser.hide()

    def destroyDebug(self, obj, event, *args, **kargs):
        self.windeb.hide()

    def startbtClick(self, obj, event, *args, **kargs):
        self.startDebugWin( obj.get_osCmd() )

    def stopbtClick(self, obj, event, *args, **kargs):
        self.startDebugWin( obj.get_osCmd() )

    def startDebugWin(self, cmd):
        print "Services startDebugWin [info]"
        self.windeb = elementary.Window("servicesDebug", elementary.ELM_WIN_BASIC)
        self.windeb.title_set("Services start|stop debug")
        self.windeb.autodel_set(True)

        self.bgdeb = elementary.Background(self.windeb)
        self.windeb.resize_object_add(self.bgdeb)
        self.bgdeb.size_hint_weight_set(1.0, 1.0)
        self.bgdeb.show()

        box0 = elementary.Box(self.windeb)
        box0.size_hint_weight_set(1.0, 1.0)
        self.windeb.resize_object_add(box0)
        box0.show()

        fr = elementary.Frame(self.windeb)
        fr.label_set("Services start|stop debug")
        fr.size_hint_align_set(-1.0, 0.0)
        box0.pack_end(fr)
        fr.show()

        sc = elementary.Scroller(self.windeb)
        sc.size_hint_weight_set(1.0, 1.0)
        sc.size_hint_align_set(-1.0, -1.0)
        box0.pack_end(sc)
        sc.show()

        cancelbt = elementary.Button(self.windeb)
        cancelbt.clicked = self.destroyDebug
        cancelbt.label_set("Close")
        cancelbt.size_hint_align_set(-1.0, 0.0)
        cancelbt.show()
        box0.pack_end(cancelbt)

        box1 = elementary.Box(self.windeb)
        box1.size_hint_weight_set(1.0, -1.0)
        sc.content_set(box1)
        box1.show()
        
        self.windeb.show()

        c = os.popen( cmd, "r" )
        while 1:
            line = c.readline()
            if not line:
                break
            print "line ["+line+"]"
            lb = elementary.Label(self.windeb)
            lb.label_set(line)
            box1.pack_end(lb)
            lb.show()


    def sssbtClick(self, obj, event):
        print "Services sssbtClick [info]"
        self.winser = elementary.Window("servicesInfo", elementary.ELM_WIN_BASIC)
        self.winser.title_set("Services list")
        self.winser.autodel_set(True)

        self.bginfo = elementary.Background(self.winser)
        self.winser.resize_object_add(self.bginfo)
        self.bginfo.size_hint_weight_set(1.0, 1.0)
        self.bginfo.show()

        box0 = elementary.Box(self.winser)
        box0.size_hint_weight_set(1.0, 1.0)
        self.winser.resize_object_add(box0)
        box0.show()

        fr = elementary.Frame(self.winser)
        fr.label_set("Services list")
        fr.size_hint_align_set(-1.0, 0.0)
        box0.pack_end(fr)
        fr.show()

        sc = elementary.Scroller(self.winser)
        sc.size_hint_weight_set(1.0, 1.0)
        sc.size_hint_align_set(-1.0, -1.0)
        box0.pack_end(sc)
        sc.show()

        """
        reloadbt = elementary.Button(self.winser)
        reloadbt.clicked = self.reloadbtClick
        reloadbt.label_set("Reload")
        reloadbt.size_hint_align_set(-1.0, 0.0)
        reloadbt.show()
        box0.pack_end(reloadbt)
        """
        
        cancelbt = elementary.Button(self.winser)
        cancelbt.clicked = self.destroyInfo
        cancelbt.label_set("Close")
        cancelbt.size_hint_align_set(-1.0, 0.0)
        cancelbt.show()
        box0.pack_end(cancelbt)

        box1 = elementary.Box(self.winser)
        box1.size_hint_weight_set(1.0, -1.0)
        sc.content_set(box1)
        box1.show()

        servicesList = dircache.listdir("/etc/init.d/")


        servicesList.sort()
        for i in servicesList:
            #how to make horizontal box?
            boxSSS = elementary.Box(self.winser)
            boxSSS.horizontal_set(True)
            boxSSS.size_hint_align_set(-1.0, 0.0)
            

            startbt = ButtonServer(self.winser)
            startbt.set_osCmd("/etc/init.d/"+i+" start")
            startbt.clicked = self.startbtClick
            startbt.label_set("start")
            startbt.size_hint_align_set(-1.0, 0.0)
            startbt.show()
            boxSSS.pack_start(startbt)
            
            stopbt = ButtonServer(self.winser)
            stopbt.set_osCmd("/etc/init.d/"+i+" stop")
            stopbt.clicked = self.stopbtClick
            stopbt.label_set("stop")
            stopbt.size_hint_align_set(-1.0, 0.0)
            stopbt.show()
            boxSSS.pack_end(stopbt)

            fo = elementary.Frame(self.winser)
            fo.label_set( i )
            fo.size_hint_align_set(-1.0, 0.0)
            fo.show()
            fo.content_set( boxSSS )

            boxSSS.show()
            box1.pack_end(fo)



        self.winser.show()

    def createView(self):
        self.editable = False

        box0 = elementary.Box(self.window)

        sssbt = elementary.Button(self.window)
        sssbt.label_set("start | stop")
        sssbt.size_hint_align_set(-1.0, 0.0)
        sssbt.clicked = self.sssbtClick
        box0.pack_end(sssbt)
        sssbt.show()


        return box0
