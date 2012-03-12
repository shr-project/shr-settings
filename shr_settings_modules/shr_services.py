# -*- coding: utf-8 -*-
import dircache
import module, elementary, os
from ecore import idler_add
from functools import partial

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class ButtonServer( elementary.Button ):
    def set_osCmd( self, cmd ):
        self.osCmd = cmd

    def get_osCmd( self ):
        return self.osCmd

class Services(module.AbstractModule):
    name = _("Services settings")

    def destroyDebug(self, obj, *args, **kargs):
        self.windeb.hide()
        self.windeb.delete()

    def hover_hide(self, obj, *args, **kargs):
        self.ser_box.delete()
        self.ser_hover.delete()

    def closex(self, action, dia, *args, **kwargs):
        self.startDebugWin(action)
        self.closedia(dia)

    def closedia(self, dia, *args, **kwargs):
        dia.delete()

    def xrestart(self, action, text, *args, **kargs):
        dia = elementary.InnerWindow(self.win)
        self.win.resize_object_add(dia)
        frame = elementary.Frame(self.win)
        dia.style_set('minimal_vertical')
        dia.scale_set(1.0)
        frame.text_set(_('Are you sure?'))
        dia.content_set(frame)
        frame.show()
        box = elementary.Box(self.win)
        frame.content_set(box)
        box.show()
        label = elementary.Entry(self.win)
        label.size_hint_align_set(-1.0, -1.0)
        label.size_hint_weight_set(1.0, 0.0)
        label.text_set(text)
        label.show()
        box.pack_start(label)
        hbox = elementary.Box(self.win)
        hbox.horizontal_set(True)
        box.pack_end(hbox)
        hbox.show()

        yes = elementary.Button(self.win)
        yes.text_set(_('Yes'))
        yes.show()
        yes._callback_add('clicked', partial(self.closex, action, dia))
        hbox.pack_start(yes)

        no = elementary.Button(self.win)
        no.text_set(_('No'))
        no.show()
        no._callback_add('clicked', partial(self.closedia, dia))
        hbox.pack_end(no)

        dia.show()
        dia.activate()


    def startbtClick(self, obj, *args, **kargs):
        """ Callback when start/stop/reload has been pressed """
        # delete the hover with Start/stop buttons
        self.ser_box.delete()
        self.ser_hover.delete()
        if kargs.get('warning'):
            self.xrestart( obj.get_osCmd(), kargs['warning_text'] )
        else:
            self.startDebugWin( obj.get_osCmd() )

    def debugIdler(self, dia, box1, cmd):
        specialcmds = {'/etc/init.d/phoneuid stop':'(killall -9 phoneuid && echo "phoneuid stopped") || echo "killall: phoneuid: no process killed"',
                       '/etc/init.d/phoneuid start':('echo "Starting phoneuid..."', 'DISPLAY=:0 phoneui-wrapper.sh &'),
                       '/etc/init.d/phoneuid restart':('(killall -9 phoneuid phoneui-wrapper.sh && echo "phoneuid stopped") || echo "killall: phoneuid: no process killed" && echo "Starting phoneuid..."', 'DISPLAY=:0 phoneui-wrapper.sh &')
                      }
        if cmd in specialcmds:
            cmd=specialcmds[cmd]

        extracmd = None
        if isinstance(cmd, tuple):
            extracmd = cmd[1]
            cmd = cmd[0]

        c = os.popen( cmd, "r" )
        while 1:
            line = c.readline().replace("\n","")
            if not line:
                break  
            print "line ["+line+"]"
            lb = elementary.Label(self.windeb)
            lb.text_set(line)
            lb.size_hint_align_set(-1.0, 0.0)
            box1.pack_end(lb)
            lb.show()

        if extracmd:
            os.system(extracmd)

        dia.delete()
        return False

    def startDebugWin(self, cmd):
        print "Services startDebugWin [info]"
        self.windeb = elementary.Window("servicesDebug", elementary.ELM_WIN_BASIC)
        self.windeb.title_set(_("Service output"))
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
        fr.text_set(_("Service output"))
        fr.size_hint_align_set(-1.0, 0.0)
        box0.pack_end(fr)
        fr.show()

        sc = elementary.Scroller(self.windeb)
        sc.size_hint_weight_set(1.0, 1.0)
        sc.size_hint_align_set(-1.0, -1.0)
        box0.pack_end(sc)
        sc.show()

        cancelbt = elementary.Button(self.windeb)
        cancelbt._callback_add('clicked', self.destroyDebug)
        cancelbt.text_set(_("Close"))
        cancelbt.size_hint_align_set(-1.0, 0.0)
        cancelbt.show()
        box0.pack_end(cancelbt)

        box1 = elementary.Box(self.windeb)
        box1.size_hint_weight_set(1.0, -1.0)
        sc.content_set(box1)
        box1.show()
        
        self.windeb.show()

        dia = elementary.InnerWindow(self.windeb)
        dia.show()
        self.windeb.resize_object_add(dia)
        diala = elementary.Label(dia)
        diala.text_set(_('Executing...'))
        diala.show()
        dia.content_set(diala)
        dia.style_set('minimal')
        dia.activate()
        idler_add(partial(self.debugIdler, dia, box1, cmd))

    def clicked_serviceBox(self, win, *args, **kargs):
        service = win.name_get()

        self.ser_hover = elementary.Hover(self.win)
        self.ser_hover.size_hint_align_set(-1.0, -1.0)
        self.ser_hover.size_hint_weight_set(1.0, 1.0)
#        self.ser_hover.style_set("hoversel_vertical")
        self.ser_hover.show()
        self.ser_hover._callback_add('clicked', self.hover_hide)
#        self.window.resize_object_add(self.ser_hover)

        ser_box = elementary.Box(self.ser_hover)       
        ser_box.show()
#        ser_box.size_hint_align_set(-1.0, -1.0)
        ser_box.size_hint_weight_set(1.0, 1.0)
        self.ser_hover.content_set("swallow?!", ser_box)
        self.ser_hover.parent_set(ser_box)
        self.ser_hover.target_set(win)

        startbt = ButtonServer(self.win)
        startbt.set_osCmd("/etc/init.d/" + service + " start")
        startbt._callback_add('clicked', partial( self.startbtClick, warning = kargs.get('warning'), warning_text = kargs.get('warning_text')))
        startbt.text_set(_("start") )
#        startbt.size_hint_align_set(-1.0, 0.0)
#        startbt.size_hint_weight_set(1.0, 1.0)
        startbt.show()
        ser_box.pack_start(startbt)

        restartbt = ButtonServer(self.win)
        restartbt.set_osCmd("/etc/init.d/"+ service +" restart")
        restartbt._callback_add('clicked', partial( self.startbtClick, warning = kargs.get('warning'), warning_text = kargs.get('warning_text')))
        restartbt.text_set(_("restart"))
#        restartbt.size_hint_align_set(-1.0, 0.0)
        restartbt.show()
        ser_box.pack_end(restartbt)

        stopbt = ButtonServer(self.win)
        stopbt.set_osCmd("/etc/init.d/"+ service +" stop")
        stopbt._callback_add('clicked', partial( self.startbtClick, warning = kargs.get('warning'), warning_text = kargs.get('warning_text')))
        stopbt.text_set(_("stop"))
#        stopbt.size_hint_align_set(-1.0, 0.0)
        stopbt.show()
        ser_box.pack_end(stopbt)
        self.ser_box = ser_box
        self.win.resize_object_add(self.ser_box)


    def createView(self):
        """ main entry to the module that creates and returns the view """
        btn = elementary.Button(self.window)
        btn.text_set(_('Services list'))
        btn._callback_add('clicked', self.makeWindow)
        return btn

    def makeWindow(self, *args, **kwargs):
        self.win = elementary.Window('settings-services', elementary.ELM_WIN_BASIC)
        win = self.win
        bg = elementary.Background(win)
        win.resize_object_add(bg)
        win.title_set(_('Services'))
        win.autodel_set(True)
        bg.show()
        box = elementary.Box(win)
        win.resize_object_add(box)
        box.show()
        scroller = elementary.Scroller(win)
        scroller.bounce_set(0,0)
        frame = elementary.Frame(win)
        frame.text_set(self.name)
        frame.size_hint_align_set(-1.0, -1.0)
        frame.size_hint_weight_set(1.0, 0.0)
        scroller.content_set(frame)

        scroller.size_hint_align_set(-1.0, -1.0)
        scroller.size_hint_weight_set(1.0, 1.0)

        box.pack_start(scroller)

        scroller.show()

        quitbt = elementary.Button(win)
        quitbt._callback_add('clicked', partial(self.windowClose, win))
        quitbt.text_set(_("Quit"))
        quitbt.size_hint_align_set(-1.0, 0.0)
        ic = elementary.Icon(quitbt)
        ic.file_set( "/usr/share/pixmaps/shr-settings/icon_quit.png" )
        ic.scale_set(1,1)
        ic.smooth_set(1)
        quitbt.icon_set(ic)
        quitbt.show()
        box.pack_end(quitbt)


        box0 = elementary.Box(win)

        label = elementary.Label(box0)
        label.text_set(_("Please wait..."))
        box0.pack_start(label)
        label.show()

        idler_add(partial(self.windowIdler, label, box0))

        box0.show()
        frame.content_set(box0)
        frame.show()
        win.show()

    def windowClose(self, win, *args, **kwargs):
        win.delete()

    def windowIdler(self, label, box0, *args, **kwargs):
        label.delete()

        frame = elementary.Frame(box0)
        frame.style_set('outdent_top')
        frame.size_hint_align_set(-1.0, -1.0)
        frame.size_hint_weight_set(1.0, 0.0)
        frame.show()
        topbox = elementary.Box(box0)
        topbox.show()
        frame.content_set(topbox)
        tops = [('frameworkd', _('Stopping frameworkd will stop all smartphone related functions. Do you really want to proceed?')),
                ('fsodeviced', _('Stopping fsodeviced will stop idle notifier and few other functions. Do you really want to proceed?')),
                ('phonefsod', _('Stopping phonefsod will stop all phone related functions. Do you really want to proceed?')),
                ('phoneuid', _('Stopping phoneuid will stop all phone user interface related functions. Do you really want to proceed?')),
                ('xserver-nodm', _('Stopping X server will stop all running applications. Do you really want to proceed?'))]
        for top in tops:
            btn = elementary.Button(box0)
            btn.text_set(top[0])
            btn.name = top[0]
            btn.size_hint_align_set(-1.0, -1.0)
            btn.size_hint_weight_set(1.0, 1.0)
            btn._callback_add('clicked', partial(self.clicked_serviceBox, warning = True, warning_text = top[1]))
            btn.show()
            topbox.pack_end(btn)
        box0.pack_start(frame)

        dontshow = ["rc", "rcS", "reboot", "halt", "umountfs", "sendsigs", "rmnologin", "functions", "usb-gadget", "frameworkd", "xserver-nodm", "phonefsod", "phoneuid", 
                    "fsodeviced"]

        servicesList = dircache.listdir("/etc/init.d/")
        servicesList.sort()
        for i in servicesList:
            if ((len(i.split(".sh"))==1) and (not(i in dontshow))):
                boxSSS = elementary.Button(box0)
                boxSSS.text_set(i)
                boxSSS.name = i
                #boxSSS.horizontal_set(True)
                boxSSS.size_hint_align_set(-1.0, -1.0)
                boxSSS.size_hint_weight_set(1.0, 1.0)
                boxSSS._callback_add('clicked', self.clicked_serviceBox)
                boxSSS.show()
                box0.pack_end(boxSSS)
             
        return False
