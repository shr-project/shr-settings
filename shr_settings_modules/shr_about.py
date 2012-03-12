import module, elementary, os, re

# Locale support
import gettext

ABOUT_TEXT = "<b>About `{0}`</><br>\
<br>\
This app is used for configuring settings on your Openmoko Neo 1973 and \
Neo Freerunner.<br>\
<br>\
License: GPLv2<br>\
Author: SHR-Project<br>\
<br>\
Version: {1}<br>Revision: {2}<br>Commit: {3}...<br>Release: {4}"


try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x

class About(module.AbstractModule):
    name = _("About")

    def createView(self):

        # create the box
        self.main = elementary.Box(self.window)
        self.main.size_hint_weight_set(1.0, 1.0)
        self.main.size_hint_align_set(-1.0, 0.0)

        ipkFile = os.popen("grep shr-settings_ /var/lib/opkg/shr-armv4t").read().split()[1]

        """
        20:21 < Ainulindale> PN-PV-rCOMMIT_NUMBER-COMMIT_HASH-PR
        20:22 < Ainulindale> (package name, package version and package revision
                             (needed to bump a package without bumping the version)
        """
        matchPattern = r'(.+)_(.+)\+r(\d+)\+([a-z0-9A-Z]+)-r(\d+)_armv4t\.ipk'
        name, ver, rev, com, rel  = re.match(matchPattern,ipkFile).groups()

        # commit is shortened to 15 characters to ensure it fits
        aboutText = ABOUT_TEXT.format(name, ver, rev, com[:15], rel)
        print aboutText

        text = elementary.Entry(self.window)
        text.text_set(aboutText)
        text.size_hint_weight_set(1.0, 1.0)
        text.size_hint_align_set(-1.0, 0.0)
        text.show()

        self.main.pack_start(text)

        self.main.show()

        return self.main
