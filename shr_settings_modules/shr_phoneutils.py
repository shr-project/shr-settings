import phoneutils, elementary, module
from ecore import timer_add
import re, dbus

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
	wizard_name = _("Local numbers settings")
	wizard_description = _("Please enter information matching to phone numbers in your country.")

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

	def parsePrefixData(self):
		file = open('/etc/phoneprefix', 'r' )

		self.countries = {}
		self.prefixes = {}

		s=1
		while s:
			line = file.readline()
			if not line:
				s = 0
			else:
				line = line[:len(line)-1]
				res = re.match(r'^([\w\-.()/&]+)\s*=\s*([0-9|]*)\s*,\s*([0-9|]*)\s*,\s*([0-9|]*)\s*$', line)
				if res:
					self.countries[res.group(1)] = [res.group(2), res.group(3), res.group(4)]
					self.prefixes[res.group(2)] = res.group(1)


	def closeInwin(self, dia, *args, **kargs):
		dia.delete()
		return False

	def saveData(self, *args):

		self.ip, self.np, self.cc, self.ac = self.getEntryData()
		#print self.ip, self.np, self.cc, self.ac
		#data=self.getEntryData()
		phoneutils.set_codes(self.ip, self.np, self.cc, self.ac)
		phoneutils.save_config()
		if not self.wizard:
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
			return True
		else:
			dia = elementary.InnerWindow(self.window)
			dia.style_set('minimal')
			lab = elementary.Label(self.window)
			lab.label_set(_("Settings could not be saved!<br>All values must be numbers!"))
			lab.show()
			dia.content_set(lab)
			self.window.resize_object_add(dia)
			dia.show()
			dia.activate()
			timer_add(1.5, self.closeInwin, dia)
			return False

	def wizardClose(self):
		return self.Validate()

	def simInfoArrived(self, siminfo):
		try:
			country = None
			if 'country' in siminfo.keys():
				# country is in -> ogsmd
				country = siminfo['country']
			else:
				# country is not in -> fsogsmd
				mcc = siminfo['imsi'][:6]
				data_world_obj = self.dbus.get_object( 'org.freesmartphone.odatad', '/org/freesmartphone/Data/World' )
				data_world_iface = dbus.Interface(data_world_obj, 'org.freesmartphone.Data.World')
				country_code = data_world_iface.GetCountryCodeForMccMnc(mcc)
				country_codes = data_world_iface.GetAllCountries()
				for item in country_codes:
					if item[0] == country_code:
						country = item[1].replace(" ", "_")
			if country in self.countries:
				self.cc, self.ip, self.np = self.countries[country]
				print self.cc;
			elif 'dial_prefix' in siminfo.keys():
				prefix = siminfo['dial_prefix']
				prefix.replace('+','')
				self.cc, self.ip, self.np = self.countries[self.prefixes[prefix]]
			self.entryIP.entry_set(self.ip)
			self.entryNP.entry_set(self.np)
			self.entryCC.entry_set(self.cc)
		except:
			print "parsing org.freesmartphone.GSM.SIM.GetSimInfo failed, using fsogsmd?"
		self.dia.delete()

	def simInfoFailed(self, error):
		print str(error)
		self.dia.delete()

	def createView(self):
		"""
		Create main box then initialize phoneutils and load the rest
		"""

		self.main = elementary.Box(self.window)

		phoneutils.init()
		self.parsePrefixData()
		self.ip, self.np, self.cc, self.ac = self.loadEntryData()

		if self.wizard:
			try:
				gsm_sim_obj = self.dbus.get_object( 'org.freesmartphone.ogsmd', '/org/freesmartphone/GSM/Device' )
				gsm_sim_iface = dbus.Interface(gsm_sim_obj, 'org.freesmartphone.GSM.SIM')

				siminfo = gsm_sim_iface.GetSimInfo(reply_handler = self.simInfoArrived, error_handler = self.simInfoFailed)

				self.dia = elementary.InnerWindow(self.window)
				self.dia.style_set('minimal')
				lab = elementary.Label(self.window)
				lab.label_set(_("Please wait..."))
				lab.show()
				self.dia.content_set(lab)
				self.window.resize_object_add(self.dia)
				self.dia.show()
				self.dia.activate()
			except:
				print "dbus fail"

		self.entryIP = PhoneUtilsEntryBox(self.window, _("Your international prefix: "), self.ip)
		self.entryNP = PhoneUtilsEntryBox(self.window, _("Your national prefix: "), self.np)
		self.entryCC = PhoneUtilsEntryBox(self.window, _("Your country code: "), self.cc)
		self.entryAC = PhoneUtilsEntryBox(self.window, _("Your area/network code: "), self.ac)

		self.main.pack_end(self.entryIP)
		self.main.pack_end(self.entryNP)
		self.main.pack_end(self.entryCC)
		self.main.pack_end(self.entryAC)

		if not self.wizard:
			self.btSave = elementary.Button(self.window)
			self.btSave.label_set(_("Save"))
			self.btSave.show()
			self.btSave.size_hint_align_set(-1.0, 0.0)
			self.main.pack_end(self.btSave)

			self.btSave._callback_add('clicked', self.Validate)

		self.main.show()

		return self.main		
			
