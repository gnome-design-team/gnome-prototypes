from gi.repository import GObject, Gtk, Gio, GLib, GdkPixbuf, Gdk

GROUPS = {
		"Family": {
				"Person 1": {"id": 1, "nick": "Person 1"},
				"Person 2": {"id": 2, "nick": "Person 2"},
				"Person 3": {"id": 3, "nick": "Person 3"},
				},
		"Friends": {
				"Person 4": {"id": 4,"nick": "Person 4"},
				"Person 5": {"id": 5,"nick": "Person 5"},
				"Person 6": {"id": 6,"nick": "Person 6"},
				},
		"Work": {
				"Person 7": {"id": 7,"nick": "Person 7"},	
				"Person 8": {"id": 8,"nick": "Person 8"},	
				"Person 9": {"id": 9,"nick": "Person 9"},	
				}
		}

class Window (Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self)
		
		css_provider = Gtk.CssProvider()
		css_provider.load_from_path("style.css")
		context = Gtk.StyleContext()
		context.add_provider_for_screen (Gdk.Screen.get_default (),
										 css_provider,
										 Gtk.STYLE_PROVIDER_PRIORITY_USER)
		
		self.set_size_request(300,600)
		self._init_ui()
		self.show_all()
	
	def _init_ui(self):
		self.box = box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.add(box)
		
		self.searchEntry = SearchEntry()
		self.scrolledWindow = Gtk.ScrolledWindow()
		tempBox = Gtk.Box()
		#tempBox.set_border_width(3)
		#tempBox.pack_start(self.searchEntry, False, False, 0)
		
		self.treeview = FakeTreeView()
		evbox = Gtk.EventBox()
		self.scrolledWindow.add_with_viewport(evbox)
		evbox.add(self.treeview)
		box.pack_start(self.scrolledWindow, True, True, 0)
		
		
class FakeTreeView(Gtk.Box):
	def __init__(self):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
		
		for i, group in enumerate(GROUPS):
			if not i == 0:
				sep = Gtk.Separator(orientation=0)
				sep.set_sensitive(False)
				self.pack_start(sep, False, False, 0)
			expander = Gtk.Expander()
			expander.set_use_markup(True)
			self.pack_start(expander, False, False, 0)
			expander.set_expanded(True)
			expander.add(GroupWidget(group))
			expander.set_label_fill(True)
			
			label = Gtk.Label()
			label.set_markup("<b>%s</b>" %(group))
			label.set_alignment(0.0, 0.5)
			label.set_padding(6, 6)
			expander.set_label_widget(label)

		
class SearchEntry(Gtk.Entry):

	__gsignals__ = {
		"clear" : (GObject.SIGNAL_RUN_FIRST,
				   GObject.TYPE_NONE,
				   ()),
		"search" : (GObject.SIGNAL_RUN_FIRST,
					GObject.TYPE_NONE,
					(GObject.TYPE_STRING,)),
		"close" : (GObject.SIGNAL_RUN_FIRST,
				   GObject.TYPE_NONE,
				   ()),
	}

	default_text = "Search Contacts"
	# TODO: What is this?
	search_timeout = 0

	def __init__(self, accel_group = None):
		Gtk.Entry.__init__(self)
		self.set_width_chars(40)
		self.set_placeholder_text("Search Contacts")
		self.connect("changed", lambda w: self._queue_search())

		search_icon =\
			Gio.ThemedIcon.new_with_default_fallbacks("edit-find-symbolic")
		self.set_icon_from_gicon(Gtk.EntryIconPosition.SECONDARY, search_icon)
		#clear_icon =\
		#	Gio.ThemedIcon.new_with_default_fallbacks("edit-clear-symbolic")
		#self.set_icon_from_gicon(Gtk.EntryIconPosition.SECONDARY, clear_icon)
		self.connect("icon-press", self._icon_press)
		self.show_all()

	def _icon_press(self, widget, pos, event):
		if event.button == 1 and pos == 1:
			self.set_text("")
			self.emit("clear")

	def _queue_search(self):
		if self.search_timeout != 0:
			GObject.source_remove(self.search_timeout)
			self.search_timeout = 0

		if len(self.get_text()) == 0:
			self.emit("clear")
		else:
			self.search_timeout = GObject.timeout_add(200,
				self._typing_timeout)

	def _typing_timeout(self):
		if len(self.get_text()) > 0:
			self.emit("search", self.get_text())

		self.search_timeout = 0
		return False

class GroupWidget(Gtk.Box):
	def __init__(self, group):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
		self.group = group
		for i, person in enumerate(GROUPS[group]):
			print person
			contact = ContactWidget(person)
			self.pack_start(contact, False, False, 0)

class ContactWidget(Gtk.EventBox):
	def __init__(self, contact):
		Gtk.EventBox.__init__(self)
		vbox = Gtk.Box(orientation=1)
		self.set_can_focus(True)
		self.contact = contact
		box = Gtk.Box()
		self.add(vbox)
		vbox.pack_start(box, True, True, 0)
		sep = Gtk.Separator(orientation=0)
		vbox.pack_start(sep, True, True, 1)
		
		self.selected_color = None;
		self.normal_color = None;
		
		img = Gtk.Button()
		img.set_size_request(54,54)
		img.set_sensitive(False)
		
		box.set_border_width(9)
		box.pack_start(img, False, False, 0)
		
		nick = Gtk.Label("Bruce Wayne")
		nick.set_markup("<b>Bruce Wayne</b>")
		nick.set_alignment(0.0, 0.5)
		
		status = Gtk.Label("Busy")
		status.set_markup("<span size='small'>Busy</span>")
		status.set_alignment(0.0, 0.0)
		
		statusBox = Gtk.Box()
		statusImg = Gtk.Button()
		statusImg.set_size_request(18, 18)
		statusImg.set_sensitive(False)
		statusBox.pack_start(statusImg, False, False, 0)
		statusBox.pack_start(status, False, False, 6)
		
		label  = Gtk.Box(orientation= 1)
		label.pack_start(nick, False, False, 3)
		label.pack_start(statusBox, False, False, 3)
		label.set_border_width(6)
		
		box.pack_start(label, True, True, 6)
		
		self.connect("focus-in-event", self._on_focus_in)
		self.connect("focus-out-event", self._on_focus_out)
		self.connect("button-press-event", lambda w, e: self.grab_focus())
		box.connect("style-updated", self._on_style_updated)
		
	def _on_style_updated(self, widget):
		self.style = self.get_style_context()
		self.selected_color = self.style.get_background_color(Gtk.StateFlags.SELECTED)
		self.normal_color = self.style.get_background_color(Gtk.StateFlags.NORMAL)
		
	def _on_focus_in(self, widget, event):
		self.override_background_color(Gtk.StateFlags.NORMAL, self.selected_color)
	
	def _on_focus_out(self, widget, event):
		self.override_background_color(Gtk.StateFlags.NORMAL, self.normal_color)

if __name__ == "__main__":
	window = Window()
	mainloop = GLib.MainLoop()
	window.connect("destroy", lambda window: mainloop.quit())
	mainloop.run()

