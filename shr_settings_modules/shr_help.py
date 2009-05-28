import module, elementary

# Locale support
import gettext

ABOUT_TEXT = "\
<b>Using SHR-Settings</><br>\
<br><em>Power</><br>\
Help with Power Settings here<br>\
<br><em>Phone</><br>\
Help with Phone Settings here<br>\
<br><em>Profiles</><br>\
Help with Profiles Settings here<br>\
<br><em>Connectivity</><br>\
Help with Connectivity Settings here<br>\
<br><em>GPS</><br>\
Help with GPS Settings here<br>\
<br><em>Date/Time</><br>\
Help with Date/Time Settings here<br>\
<br><em>Services</><br>\
Help with Services Settings here<br>\
<br><em>Others</><br>\
Help with Others here<br>\
<br><em>Help</><br>\
You need help with the help?  Eh?"


try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x

class Help(module.AbstractModule):
    name = _("Help")

    def createView(self):

        # create the box
        self.main = elementary.Box(self.window)
        self.main.size_hint_weight_set(1.0, 1.0)
        self.main.size_hint_align_set(-1.0, 0.0)

        # This isn't working yet, not sure why
        text = elementary.AnchorView(self.window)
        text.text_set(HELP_TEXT)
        text.size_hint_weight_set(1.0, 1.0)
        text.size_hint_align_set(-1.0, 0.0)
        text.show()

        self.main.pack_start(text)

        self.main.show()

        return self.main
