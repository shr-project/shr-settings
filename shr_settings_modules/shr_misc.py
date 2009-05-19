import elementary, module

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class Misc(module.AbstractModule):
    name = _("Miscellaneous settings")
    
    def createView(self):
        la = elementary.Label(self.window)
        la.label_set(_("Suspend, dim time and etc."))
        return la

