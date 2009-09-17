import phoneutils, elementary, module
from ecore import timer_add

# Locale support
import gettext
 
try:
	cat = gettext.Catalog("shr-settings")
	_ = cat.gettext
except IOError:
	_ = lambda x: x

__author__ = "soltys"



class PhoneUtilsEntryBox(elementary.Box):
	"""
	Class for libphoneutils entry
	"""

	def entry_get(self):
		return self.phoneutilsEntry.entry_get()
					
	def entry_set(self, value):
		return self.phoneutilsEntry.entry_set(value)
									
	def __init__(self, win, label, value):
		"""
		"""
															
		super(PhoneUtilsEntryBox, self).__init__(win)
		self.horizontal_set(True)

                self.size_hint_weight_set(1.0, 0.0)
                self.size_hint_align_set(-1.0, 0.0)
														
		self.window = win
		self.label  = label
		self.value  = value
																	
		self.phoneutilsLabel = elementary.Label(self.window)
		self.phoneutilsLabel.size_hint_align_set(-1.0, 0.0)
		self.phoneutilsLabel.label_set(self.label)
		self.phoneutilsLabel.show()
										
		self.phoneutilsEntry = elementary.Entry(self.window)
		self.phoneutilsEntry.single_line_set(True)
                self.phoneutilsEntry.size_hint_weight_set(1.0, 0.0)
                self.phoneutilsEntry.size_hint_align_set(-1.0, 0.0)
		self.phoneutilsEntry.entry_set(self.value)
		self.phoneutilsEntry.show()

		self.phoneutilsEntryFrame = elementary.Frame(self.window)
		self.phoneutilsEntryFrame.style_set("outdent_top")
                self.phoneutilsEntryFrame.size_hint_weight_set(1.0, 0.0)
                self.phoneutilsEntryFrame.size_hint_align_set(-1.0, 0.0)
		self.phoneutilsEntryFrame.content_set(self.phoneutilsEntry)
		self.phoneutilsEntryFrame.show()

		self.pack_start(self.phoneutilsLabel)
		self.pack_end(self.phoneutilsEntryFrame)
		self.show()


class Phoneutils(module.AbstractModule):
	name =_("Phoneutils settings")
	section = _("Phone")

	def getEntryData(self):
		"""
		Returns clean values for the text entries
		"""
		ip = self.entryIP.entry_get().replace("<br>","")
		np = self.entryNP.entry_get().replace("<br>","")
		cc = self.entryCC.entry_get().replace("<br>","")
		ac = self.entryAC.entry_get().replace("<br>","")

		return ip,np,cc,ac

	def loadEntryData(self):
		"""
		Loads data from libphoneutils
		"""
	
		ip = phoneutils.get_user_international_prefix()
		np = phoneutils.get_user_national_prefix()
		cc = phoneutils.get_user_country_code()
		ac = phoneutils.get_user_area_code()

		return ip,np,cc,ac


        def closeInwin(self, dia, *args, **kargs):
                dia.delete()
                return False

	def saveData(self, *args):

		self.ip, self.np, self.cc, self.ac = self.getEntryData()
		#print self.ip, self.np, self.cc, self.ac
		#data=self.getEntryData()
		phoneutils.set_codes(self.ip, self.np, self.cc, self.ac)
		phoneutils.save_config()
                dia = elementary.InnerWindow(self.window)
                dia.style_set('minimal')
                lab = elementary.Label(self.window)
                lab.label_set(_("Settings saved!"))
                lab.show()
                dia.content_set(lab)
                self.window.resize_object_add(dia)
                dia.show()
                dia.activate()
                timer_add(1.5, self.closeInwin, dia)


	def Validate(self, *args):
		new = self.getEntryData()
		old = self.loadEntryData()
		bad = 0

		if new != old:
			for entry in new:
				if not (entry.isdigit() or entry==''):
					bad +=1
		if bad == 0:
			self.saveData()

		else:
			dia = elementary.InnerWindow(self.window)
			dia.style_set('minimal')
			lab = elementary.Label(self.window)
			lab.label_set(_("Settings could not be saved!<br>All values must me numbers!"))
			lab.show()
			dia.content_set(lab)
			self.window.resize_object_add(dia)
			dia.show()
			dia.activate()
			timer_add(1.5, self.closeInwin, dia)


	def createView(self):
		"""
		Create main box then initialize phoneutils and load the rest
		"""

		self.main = elementary.Box(self.window)

		phoneutils.init()
		self.ip, self.np, self.cc, self.ac = self.loadEntryData()

		self.entryIP = PhoneUtilsEntryBox(self.window, _("Your international prefix: "), self.ip)
		self.entryNP = PhoneUtilsEntryBox(self.window, _("Your national prefix: "), self.np)
		self.entryCC = PhoneUtilsEntryBox(self.window, _("Your country code: "), self.cc)
		self.entryAC = PhoneUtilsEntryBox(self.window, _("Your area/network code: "), self.ac)

		self.main.pack_end(self.entryIP)
		self.main.pack_end(self.entryNP)
		self.main.pack_end(self.entryCC)
		self.main.pack_end(self.entryAC)

		self.btSave = elementary.Button(self.window)
		self.btSave.label_set(_("Save"))
		self.btSave.show()
		self.btSave.size_hint_align_set(-1.0, 0.0)
		self.main.pack_end(self.btSave)

		self.btSave.clicked = self.Validate

		self.main.show()

		return self.main		
			
