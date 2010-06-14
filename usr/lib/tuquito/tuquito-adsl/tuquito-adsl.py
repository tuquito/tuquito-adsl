#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 Tuquito ADSL 1.2
 Copyright (C) 2010
 Author: Mario Colque <mario@tuquito.org.ar>
 Tuquito Team! - www.tuquito.org.ar

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; version 3 of the License.
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
"""

import gtk, pygtk
pygtk.require('2.0')
import gettext, os, commands, threading

# i18n
gettext.install('tuquito-adsl', '/usr/share/tuquito/locale')

sudoUser = os.environ.get('SUDO_USER')
adsl = '/home/' + sudoUser + '/.tuquito/tuquito-adsl'
flagO = True

class Conect(threading.Thread):
	def __init__(self, action, builder):
		global flagO
		threading.Thread.__init__(self)
		self.action = action
		self.builder = builder
		flagO = flagO

	def notify(self, text, icon):
		sh = 'su ' + sudoUser + ' -c "notify-send \'Tuquito ADSL\' \'' + text + '\' -i ' + icon + '"'
		os.system(sh)

	def run(self):
		global flagO
		if self.action == 'on':
			gtk.gdk.threads_enter()
			self.builder.get_object('window').window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
			self.builder.get_object('statusicon').set_blinking(True)
			self.builder.get_object('statusicon').set_visible(True)
			gtk.gdk.threads_leave()

			exists = commands.getoutput('/usr/lib/tuquito/tuquito-adsl/conect on')

			if exists == 'ppp':
				os.system('echo "nameserver 208.67.222.222" > /etc/resolv.conf')
				os.system('echo "nameserver 208.67.220.220" >> /etc/resolv.conf')
				self.builder.get_object('window').window.set_cursor(None)
				self.builder.get_object('statusicon').set_tooltip(_('Connected'))
				self.builder.get_object('statusicon').set_blinking(False)
				self.builder.get_object('window').hide()
				self.builder.get_object('disconect').set_sensitive(True)
				flagO = False
				self.notify(_('Connection successfully established'), '/usr/lib/tuquito/tuquito-adsl/tuquito-adsl.svg')
				return True
		else:
			gtk.gdk.threads_enter()
			self.builder.get_object('window').window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
			self.builder.get_object('window').show_all()
			self.builder.get_object('statusicon').set_blinking(False)
			gtk.gdk.threads_leave()

			exists = commands.getoutput('/usr/lib/tuquito/tuquito-adsl/conect off')
			
			gtk.gdk.threads_enter()
			self.builder.get_object('window').window.set_cursor(None)
			self.builder.get_object('statusicon').set_visible(False)
			self.builder.get_object('conect').set_sensitive(True)
			gtk.gdk.threads_leave()
			self.notify(_('You are disconnected'), '/usr/lib/tuquito/tuquito-adsl/desconectado.svg')

class Window:
	def __init__(self):
		self.flag = True
		self.builder = gtk.Builder()
		self.builder.add_from_file('/usr/lib/tuquito/tuquito-adsl/tuquito-adsl.glade')
		self.window = self.builder.get_object('window')
		self.statusicon = self.builder.get_object('statusicon')
		self.menu = self.builder.get_object('menu')
		self.btnDisc = self.builder.get_object('disconect')
		self.btnCon = self.builder.get_object('conect')
		self.builder.get_object('message').set_label(_('<b>Attention!</b>\nYour modem is not configured yet.\nTo do this, select <i>Settings » Configure modem</i>.\nOnce configured, edit your account from <i>Settings » Edit account</i>.'))
		self.builder.get_object('messageDialog').set_title(_('Attention!'))
		self.builder.get_object('menuitem1').set_label(_('_Settings'))
		self.builder.get_object('label_user').set_label('<b>' + _('User:') + '</b>')
		self.builder.get_object('label_pass').set_label('<b>' + _('Password:') + '</b>')
		self.builder.get_object('menuModem').set_label(_('Configure modem'))
		self.builder.get_object('menuCuenta').set_label(_('Edit account'))
		self.builder.get_object('acount').set_title(_('My account'))
		self.builder.connect_signals(self)

		menuItem=gtk.ImageMenuItem(gtk.STOCK_DISCONNECT)
		menuItem.connect('activate', self.disconect)
		self.menu.append(menuItem)

		self.statusicon.connect('popup_menu', self.submenu, self.menu)
		
		if not os.path.exists(adsl):
			self.builder.get_object('messageDialog').show()

		self.window.show_all()

	def activate(self, widget, data=None):
		global flagO
		if flagO:
			self.window.hide()
			flagO = False
			return True
		else:
			self.window.show()
			flagO = True

	def submenu(self, widget, button, time, data=None):
		if button == 3:
			if data:
				data.show_all()
				data.popup(None, None, None, 3, time)
		pass

	def configModem(self, widget):
		os.system('/usr/lib/tuquito/tuquito-adsl/config-modem.sh &')

	def hideWin(self, widget, data=None):
		global flagO
		if self.flag:
			gtk.main_quit()
		else:
			if flagO:
				flagO = False
			else:
				flagO = True
			widget.hide()
		return True

	def hideMessage(self, widget, data=None):
		self.builder.get_object('messageDialog').hide()
		return True	

	def hideAcount(self, widget, data=None):
		self.builder.get_object('acount').hide()
		return True		

	def acount(self, widget):
		if not os.path.exists(adsl):
			f = open(adsl, 'w')
			f.write('USER=\nPASS=')
			f.close()
		f = open(adsl, 'r')
		g = f.readlines()
		f.close()
		for stri in g:
			stringa = stri.split('=')
			par = stringa[0].strip()
			val = stringa[1].strip()
			val = val.replace('"', '')
			val = val.replace('\n', '')
			if par == 'USER':
				if val == '':
					user = _('user@provider')
				else:
					user = str(val)
			elif par == 'PASS':
				pasw = str(val)

		self.builder.get_object('user').set_text(user)
		self.builder.get_object('pass').set_text(pasw)
		self.builder.get_object('acount').show()

	def save(self, widget):
		user = self.builder.get_object('user').get_text().strip()
		pasw = self.builder.get_object('pass').get_text().strip()

		if os.path.exists(adsl):
			f = open(adsl, 'w')
			f.write('USER="' + user + '"\n')
			f.write('PASS="' + pasw + '"\n')
			f.close()

		os.system('cp /usr/share/tuquito/adsl/templates/adsl /etc/ppp/peers/')
		cmd = "sed -i 's/user-adsl/user \"" + user + "\"/' /etc/ppp/peers/adsl"
		os.system(cmd)

		os.system('cp /usr/share/tuquito/adsl/templates/chap-secrets /etc/ppp/')
		cmd = "sed -i 's/adsl-data/\"" + user + "\" * \"" + pasw + "\"/' /etc/ppp/chap-secrets"
		os.system(cmd)

		os.system('cp /usr/share/tuquito/adsl/templates/pap-secrets /etc/ppp/')
		cmd = "sed -i 's/adsl-data/\"" + user + "\" * \"" + pasw + "\"/' /etc/ppp/pap-secrets"
		os.system(cmd)

		self.hideAcount(self)

	def conect(self, widget):
		self.flag = False
		self.btnCon.set_sensitive(False)
		hilo = Conect('on', self.builder)
		hilo.start()

	def disconect(self, widget):
		self.flag = True
		self.btnDisc.set_sensitive(False)
		hilo = Conect('off', self.builder)
		hilo.start()

if __name__ == '__main__':
	gtk.gdk.threads_init()
	Window()
	gtk.main()
