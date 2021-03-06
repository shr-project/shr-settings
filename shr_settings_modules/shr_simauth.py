import elementary, module, dbus

from helper import getDbusObject

from functools import partial

# Locale support
import gettext

try:
		cat = gettext.Catalog("shr-settings")
		_ = cat.gettext
except IOError:
		_ = lambda x: x


class SimAuth(module.AbstractModule):
	name = _("PIN settings")

	def isEnabled(self):
            return True

	def error(self, result):
		self.loading.text_set(_("Couldn't connect to FSO"))

        def diaclose(self, dia, *args, **kwargs):
            dia.delete()

        def dialog(self, msg, *args, **kwargs):

            dia = elementary.InnerWindow(self.window)
            dia.scale_set(1.0)

            txt = elementary.Entry(self.window)
            txt.text_set(msg)
            txt.show()
            fr = elementary.Frame(dia)
            fr.style_set('pad_medium')
            fr.size_hint_weight_set(-1.0, -1.0)
            fr.size_hint_align_set(-1.0, -1.0)
            fr.content_set(txt)
            fr.show()
            box = elementary.Box(dia)
            box.show()
            box.pack_start(fr)

            if kwargs.get('entry'):
                entryscr = elementary.Scroller(self.window)
                entryscr.content_min_limit(0,1)
                entryscr.bounce_set(0, 0)
                entryscr.policy_set(elementary.ELM_SCROLLER_POLICY_OFF, elementary.ELM_SCROLLER_POLICY_OFF)
                entryscr.size_hint_weight_set(1.0, 0.0)
                entryscr.size_hint_align_set(-1.0, -1.0)
                entry = elementary.Entry(self.window)
                entry.show()
                entry.size_hint_weight_set(1.0, 0.0)
                entry.size_hint_align_set(-1.0, -1.0)
                entry.single_line_set(True)
                entry.scale_set(2.0)
                entry.password_set(True)
                entryscr.content_set(entry)
                entryscr.show()
                entry.focus()
                box.pack_end(entryscr)

            btn = elementary.Button(dia)
#            btn.size_hint_weight_set(1.0, 0.0)
            btn.size_hint_align_set(-1.0, 0.0)
            btn.text_set('OK')
            btn.show()
            if kwargs.get('callback'):
                if kwargs.get('entry'):
                    btn._callback_add('clicked', partial(kwargs['callback'], entry, dia))
                else:
                    btn._callback_add('clicked', partial(kwargs['callback'], dia))
            else:
                btn._callback_add('clicked', partial(self.diaclose, dia))
            box.pack_end(btn)

            dia.content_set(box)
            dia.style_set("minimal_vertical")
            self.window.resize_object_add(dia)
            dia.activate()

        def required_callback(self, toggle, entry, dia, *args, **kwargs):
            try:
                pin = str(int(entry.markup_to_utf8(entry.entry_get()).replace('\n','')))
            except ValueError:
                self.diaclose(dia)
                toggle.state_set(self.sim.GetAuthCodeRequired())
                self.dialog(_('Incorrect PIN!'))
                return False

            try:
                self.sim.SetAuthCodeRequired(toggle.state_get(), pin)
            except:
                self.dialog(_('Wrong PIN!'))
                return False

            toggle.state_set(self.sim.GetAuthCodeRequired())
            self.diaclose(dia)

        def change_enter_again_callback(self, oldpin, newpin, entryagain, dia, *args, **kwargs):
            againpin = entryagain.markup_to_utf8(entryagain.entry_get()).replace('\n','')
#            print "old: " + oldpin
#            print "new: " + newpin
#            print "again: " + againpin
            self.diaclose(dia)
            if newpin == againpin:
                try:
                    self.sim.ChangeAuthCode(oldpin, newpin)
                except:
                    self.dialog(_('Wrong PIN or unknown error'))
                    return False
                self.dialog(_('PIN changed!'))
            else:
                self.dialog(_("PINs don't match!"))

        def change_enter_new_callback(self, oldpin, entry, dia, *args, **kwargs):
            try:
                newpin = str(int(entry.markup_to_utf8(entry.entry_get()).replace('\n','')))
                if len(newpin) < 4 or len(newpin) > 8:
                    raise(ValueError)
            except ValueError:
                self.diaclose(dia)
                self.dialog(_('Incorrect PIN!'))
                return False
            self.diaclose(dia)
            self.dialog(_('Enter again new SIM PIN:'), callback = partial(self.change_enter_again_callback, oldpin, newpin), entry = True)

        def change_enter_old_callback(self, entry, dia, *args, **kwargs):
            try:
                oldpin = str(int(entry.markup_to_utf8(entry.entry_get()).replace('\n','')))
            except ValueError:
                self.diaclose(dia)
                self.dialog(_('Incorrect PIN!'))
                return False
            self.diaclose(dia)
            self.dialog(_('Enter new SIM PIN:'), callback = partial(self.change_enter_new_callback, oldpin), entry = True)

        def change_pin(self, obj, *args, **kwargs):
            self.dialog(_('Enter actual SIM PIN:'), callback = self.change_enter_old_callback, entry = True)

	def auth_handle(self, obj, *args, **kargs):
		if self.sim.GetAuthCodeRequired()==obj.state_get():
			return 0

                self.dialog(_('Enter SIM PIN:'), callback = partial(self.required_callback, obj), entry = True)

	def cb_get_auth(self, state):
		self.loading.delete()

		self.toggle0 = elementary.Check(self.window)
		self.toggle0.style_set("toggle");
		self.toggle0.text_set(_("PIN code: "))
		self.toggle0.size_hint_align_set(-1.0, 0.0)
		self.toggle0.part_text_set("on", _("Enabled"));
		self.toggle0.part_text_set("off", _("Disabled"));
		self.toggle0.state_set(state)
		self.toggle0._callback_add('changed', self.auth_handle)
		self.box1.pack_end(self.toggle0)
		self.toggle0.show()

		self.btn = elementary.Button(self.window)
		self.btn.text_set(_("Change PIN"))
		self.btn.size_hint_align_set(-1.0, 0.0)
		self.btn._callback_add('clicked', self.change_pin)
		self.box1.pack_end(self.btn)
		self.btn.show()

	def createView(self):
		try:
			self.sim = getDbusObject(self.dbus,
					"org.freesmartphone.ogsmd",
					"/org/freesmartphone/GSM/Device",
					"org.freesmartphone.GSM.SIM")
		except:
			label = elementary.Label(self.window)
			label.text_set(_("Couldn't connect to FSO"))
			return label

		self.box1 = elementary.Box(self.window)

		self.loading = elementary.Label(self.window)
		self.loading.text_set(_("Please wait..."))
		self.box1.pack_start(self.loading)
		self.loading.show()

		self.sim.GetAuthCodeRequired(reply_handler=self.cb_get_auth, error_handler=self.error)

		return self.box1
