import module, elementary

# Locale support
import gettext

try:
    cat = gettext.Catalog("shr-settings")
    _ = cat.gettext
except IOError:
    _ = lambda x: x

class ImageInfo(module.AbstractModule):
    name = _("Image information")

    def mergeList(self, list):
        value = ''
        for pos in list:
            value += pos
        return value

    def dictFromFile(self, file):
        dic = {}
        for line in file:
            line = line.split(': ')
            if len(line)>1:
                dic[line[0]] = self.mergeList(line[1:])
            else:
                line = line[0].split(' ')
                if len(line)>1:
                    dic[line[0]] = self.mergeList(line[1:])
                else:
                    dic[line[0]] = None
        return dic

    def infoadd(self, text):
        return elementary.Entry.utf8_to_markup(text)+'<br>'

    def createView(self):

        # create the box
        self.main = elementary.Box(self.window)
        self.main.size_hint_weight_set(1.0, 1.0)
        self.main.size_hint_align_set(-1.0, 0.0)

        verFile = open("/etc/shr-version", "r").read().split('\n')

#        matchPattern = r'(.+)_(.+)\+r(\d+)\+([a-z0-9A-Z]+)-r(\d+)_armv4t\.ipk'
#        ipkInfo = re.match(matchPattern,ipkFile).groups()
#        aboutText = ABOUT_TEXT.format(ipkInfo)
#        print aboutText

        ver = self.dictFromFile(verFile)
        print ver
        info = self.infoadd(_("SHR: ") + ver['SHR'])
        info += self.infoadd(_("Branch: ") + ver['Built from branch'])
        info += self.infoadd(_("Revision: ") + ver['Revision'])

        text = elementary.Entry(self.window)
        text.text_set(info)
        text.scale_set(0.9)
        text.size_hint_weight_set(1.0, 1.0)
        text.size_hint_align_set(-1.0, 0.0)
        text.show()

        self.main.pack_start(text)

        self.main.show()

        return self.main
