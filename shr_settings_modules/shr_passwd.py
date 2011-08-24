import elementary, module
import pexpect, sys, time
from ecore import timer_add

# Locale support
import gettext
 
try:
	cat = gettext.Catalog("shr-settings")
	_ = cat.gettext
except IOError:
	_ = lambda x: x

__author__ = "dos"



class PasswordEntryBox(elementary.Box):
	"""
	Class for password entry
	"""

	def entry_get(self):
		return self.PasswordEntry.entry_get()
					
	def entry_set(self, value):
		return self.PasswordEntry.entry_set(value)
									
	def __init__(self, win, label, value):
		"""
		"""
															
		super(PasswordEntryBox, self).__init__(win)
		self.horizontal_set(True)

		self.size_hint_weight_set(1.0, 0.0)
		self.size_hint_align_set(-1.0, 0.0)
														
		self.window = win
		self.label  = label
		self.value  = value
																	
		self.PasswordLabel = elementary.Label(self.window)
		self.PasswordLabel.size_hint_align_set(-1.0, 0.0)
		self.PasswordLabel.text_set(self.label)
		self.PasswordLabel.show()
										
		self.PasswordEntry = elementary.Entry(self.window)
		self.PasswordEntry.single_line_set(True)
		self.PasswordEntry.password_set(True)
		self.PasswordEntry.size_hint_weight_set(1.0, 0.0)
		self.PasswordEntry.size_hint_align_set(-1.0, 0.0)
		self.PasswordEntry.entry_set(self.value)
		self.PasswordEntry.show()

		self.PasswordEntryFrame = elementary.Frame(self.window)
		self.PasswordEntryFrame.style_set("outdent_top")
		self.PasswordEntryFrame.size_hint_weight_set(1.0, 0.0)
		self.PasswordEntryFrame.size_hint_align_set(-1.0, 0.0)
		self.PasswordEntryFrame.content_set(self.PasswordEntry)
		self.PasswordEntryFrame.show()

		self.pack_start(self.PasswordLabel)
		self.pack_end(self.PasswordEntryFrame)
		self.show()


class Password(module.AbstractModule):
	name =_("Root password")
	section = _("Others")
	wizard_name = _("Root password")
	wizard_description = _("Please enter password which you want to use when, for instance, loging by SSH.")

	def changePassword(self, user, password):
		child = pexpect.spawn("/usr/bin/passwd %s" % user)

		#print password
		child.expect("New password: ", timeout = 2)
		child.sendline(password)
		time.sleep(0.5)
		result = child.expect(["Re-enter new password: ", "New password: "], timeout = 2)
		child.sendline(password)
		time.sleep(0.5)
		if result==1:
			result = child.expect("Re-enter new password: ", timeout = 2)
			child.sendline(password)
			time.sleep(0.5)
		child.expect(pexpect.EOF)
		#print child.before
		#if "passwd: password changed." in child.before:
		#	print "done"
		#else:
		#	print "not done"

	def isEnabled(self):
		return self.wizard

	def getEntryData(self):
		"""
		Returns clean values for the text entries
		"""
		password = self.entryPass.entry_get()
		password2 = self.reentryPass.entry_get()
		if password != password2:
			return -1
		

		return password

	def dialog(self, text, autoclose = False):
		dia = elementary.InnerWindow(self.window)
		dia.style_set("minimal")
		dia.show()
		label = elementary.Label(dia)
		label.text_set(text)
		label.show()
		dia.content_set(label)
		dia.activate()
		if autoclose:
			timer_add(3, dia.delete)
		return dia

	def saveData(self, *args):
		self.password = self.getEntryData()
		if self.password == -1:
			self.dialog("Passwords do not match!", True)
			return False
		if len(self.password) > 0:
			self.changePassword('root', self.password)
		return True

	def wizardClose(self):
		return self.saveData()

	def createView(self):
		"""
		Create main box then initialize Password and load the rest
		"""

		self.main = elementary.Box(self.window)

		self.entryPass = PasswordEntryBox(self.window, _("Enter password: "), '')
		self.reentryPass = PasswordEntryBox(self.window, _("Re-enter password: "), '')

		self.main.pack_end(self.entryPass)
		self.main.pack_end(self.reentryPass)

		self.main.show()

		return self.main		
			
