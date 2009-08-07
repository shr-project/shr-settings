import elementary, module, dbus

# Locale support
import gettext

try:
		cat = gettext.Catalog("shr-settings")
		_ = cat.gettext
except IOError:
		_ = lambda x: x


def getDbusObject (bus, busname , objectpath , interface):
	dbusObject = bus.get_object(busname, objectpath)
	return dbus.Interface(dbusObject, dbus_interface=interface)


class SimAuth(module.AbstractModule):
	name = _("SIM card authentification on startup")

	def isEnabled(self):
		try:
			self.gsm=getDbusObject(self.dbus,
				"org.freesmartphone.ousaged",
				"/org/freesmartphone/Usage",
				"org.freesmartphone.Usage")
			return self.gsm.GetResourceState("GSM")
		except:
			return 0


	def error(self, result):
		self.loading.label_set(_("Error while reading the auth status."))


	def auth_handle(self, obj, event, *args, **kargs):
		if self.sim.GetAuthCodeRequired()==obj.state_get():
			return 0

		pin = self.PinEntry.entry_get().replace("<br>","")

		if pin=="PIN" or pin=="Enter PIN here":
			self.PinEntry.entry_set("Enter PIN here")
		else :
			self.PinEntry.entry_set("PIN")

		if obj.state_get()==0:
			try:
				self.sim.SetAuthCodeRequired(0, pin)
			except:
				pass
		else:
			try:
				self.sim.SetAuthCodeRequired(1, pin)
			except:
				pass

		obj.state_set(self.sim.GetAuthCodeRequired())


	def cb_get_auth(self, state):
		self.loading.delete()

		self.toggle0 = elementary.Toggle(self.window)
		self.toggle0.label_set(_("SIM card checks pin: "))
		self.toggle0.size_hint_align_set(-1.0, 0.0)
		self.toggle0.states_labels_set(_("Yes"),_("No"))
		self.toggle0.state_set(self.sim.GetAuthCodeRequired())
		self.toggle0.changed = self.auth_handle
		self.box1.pack_end(self.toggle0)

		self.toggle0.show()

		self.PinEntry = elementary.Entry(self.window)
		self.PinEntry.single_line_set(True)
		self.PinEntry.entry_set("PIN")
		self.box1.pack_end(self.PinEntry)
		self.PinEntry.show()


	def createView(self):
		try:
			self.sim = getDbusObject(self.dbus,
					"org.freesmartphone.ogsmd",
					"/org/freesmartphone/GSM/Device",
					"org.freesmartphone.GSM.SIM")
		except:
			label = elementary.Label(self.window)
			label.label_set(_("Couldn't connect to FSO"))
			return label

		self.box1 = elementary.Box(self.window)

		self.loading = elementary.Label(self.window)
		self.loading.label_set(_("Please wait..."))
		self.box1.pack_start(self.loading)
		self.loading.show()

		self.sim.GetAuthCodeRequired(reply_handler=self.cb_get_auth, error_handler=self.error)

		return self.box1
