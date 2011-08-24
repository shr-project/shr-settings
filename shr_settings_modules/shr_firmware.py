import module, elementary

MODELS = {
	'Sirloin OMAP3430 board':'Palm Pre',
	'Nokia RX-51 board':'Nokia N900',
	'trout':'HTC Dream' }

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x

class Firmware(module.AbstractModule):
    name = _("Firmware")
    section = _("Others")
    wizard_name = _("Firmware")

    def mergeList(self, list):
        value = ''
        for pos in list:
            value += pos
        return value

    def dictFromFile(self, file):
        dic = {}
        for line in file:
            line = line.replace('\t','')
            line = line.split(': ')
            dic[line[0]] = self.mergeList(line[1:])
        return dic

    def isEnabled(self):
        if not self.wizard:
            return False

        verFile = open("/proc/cpuinfo", "r").read().split('\n')
        ver = self.dictFromFile(verFile)
        self.model = ver['Hardware']

        return self.model in MODELS

    def createView(self):

        self.wizard_description =  _("Your device, %s, needs some external firmware to be installed in order to make everything working correctly. Those firmwares are non-free and can't be redistributed with SHR, so you have to download them on your own. Please check this page for more details." % MODELS[self.model])

        text = elementary.Label(self.window)
        text.text_set("http://wiki.shr-project.org/trac/wiki/Firmware ")
        text.size_hint_weight_set(1.0, 1.0)
        text.size_hint_align_set(0.0, 0.0)
        text.show()

        return text
