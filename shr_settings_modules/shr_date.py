import elementary, module
from datetime import date

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x


class Date(module.AbstractModule):
    name = _("Date")
    
    def createView(self):
        la = elementary.Label(self.window)
        la.label_set(date.today().strftime("%A, %d %B %Y"))
        return la
