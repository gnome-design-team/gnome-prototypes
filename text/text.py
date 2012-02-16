from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GdkPixbuf
from gi.repository import GtkSource

class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.notebook = Gtk.Notebook()
        self.set_size_request(640, 480)
        #self.add(self.notebook)
        
        view = View(None, None)
        
        #self.notebook.append_page(view, view.header)
        self.notebook.set_show_tabs(False)
        self.add(view)
        
        self.show_all()

class TabHeader(Gtk.Box):
    def __init__(self, title):
        Gtk.Box.__init__(self)
        self.label = Gtk.Label(title)
        self.closeBtn = Gtk.Button()
        img = Gtk.Image.new_from_stock("gtk-close", 1)
        self.closeBtn.set_alignment(1.0, 0.5)
        #self.closeBtn.add(img)
        self.closeBtn.set_size_request(4, 4)
        self.closeBtn.set_relief(Gtk.ReliefStyle.NONE)
        self.pack_start(self.label, True, True, 3)
        self.pack_end(img, False, False, 0)
        self.show_all()

class View(Gtk.Box):
    def __init__(self, title=None, uri=None):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)
        if not title:
            title = "Untitled Document"
        self.title = title
        print self.title
        if not uri:
            uri = "/tmp/u"
        self.uri = uri
        self.header = TabHeader(self.title)
        self.toolbar = Toolbar()
        self.sourceView = GtkSource.View()
        self.pack_start(self.toolbar, False, False, 0)
        self.pack_end(self.sourceView, True, True, 0)
        self.show_all()

class Toolbar(Gtk.Toolbar):
    def __init__(self):
        Gtk.Toolbar.__init__(self)
        self.get_style_context().add_class("primary-toolbar");
        self.set_icon_size(Gtk.IconSize.LARGE_TOOLBAR)
        
        self._rightGroup = Gtk.ToolItem()
        self._centerGroup = Gtk.ToolItem()
        self._leftGroup = Gtk.ToolItem()
        
        self.insert(self._leftGroup, -1)
        self.insert(self._centerGroup, -1)
        self.insert(self._rightGroup, -1)
        
        self._centerGroup.set_expand(True)
        
        self._leftBox = Gtk.Box()
        self._leftGroup.add(self._leftBox)
        #self._leftBox.pack_start(Gtk.Box(), False, False, 0)
        
        self.homeBtn = Gtk.Button()
        self.homeBtn.get_style_context().add_class('raised')
        icon = Gio.ThemedIcon.new_with_default_fallbacks("user-home-symbolic")
        image = Gtk.Image()
        image.set_from_gicon(icon, 1)
        self.homeBtn.add(image)
        self._leftBox.pack_start(self.homeBtn, True, True, 1)
        #self._leftBox.set_spacing(9)
        
        """==============="""
        self.documentBtn = Gtk.ToggleButton()
        self._leftBox.pack_start(self.documentBtn, True, True, 5)
        
        #self.documentBtn.get_children()[0].remove(self.documentBtn.get_children()[0].get_children()[0])
        self.documentBtn.get_style_context().add_class('raised')
        
        #arrow = self.documentBtn.get_children()[0].get_children()[0].get_children()[0]
        #self.documentBtn.get_children()[0].get_children()[0].remove(arrow)
        icon = Gio.ThemedIcon.new_with_default_fallbacks("text-x-generic-symbolic")
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.MENU)
        hbox = Gtk.Box()
        hbox.pack_start(image, False, False, 0)
        arrow = Gtk.Arrow()
        arrow.set(1,1)
        hbox.pack_start(arrow, False, False, 0)
        hbox.set_spacing(3)
        self.documentBtn.add(hbox)
        self.documentMenu = Gtk.Menu()
        #self.documentBtn.set_menu(self.documentMenu)
        """==============="""
        self.documentSaveAsMenuItem = Gtk.MenuItem.new_with_label("Save As...")
        self.documentMenu.append(self.documentSaveAsMenuItem);
        self.documentPrintMenuItem = Gtk.MenuItem.new_with_label("Print...")
        self.documentMenu.append(self.documentPrintMenuItem);
        self.documentStatsMenuItem = Gtk.MenuItem.new_with_label("Statistics")
        self.documentMenu.append(self.documentStatsMenuItem);
        self.documentPrefMenuItem = Gtk.MenuItem.new_with_label("Preferences")
        self.documentMenu.append(self.documentPrefMenuItem);
        
        self.documentMenu.show_all()
        
        self._rightBox = Gtk.Box()
        self._rightGroup.add(self._rightBox)
        
        self.abcBtn = Gtk.Button()
        self.abcBtn.get_style_context().add_class('raised')
        label = Gtk.Label()
        self.abcBtn.add(label)
        label.set_markup("<span size='small'><b>abc</b></span>")
        self._rightBox.pack_start(self.abcBtn, False, False, 0)
        
        self.saveBtn = Gtk.Button()
        icon = Gio.ThemedIcon.new_with_default_fallbacks("document-save-symbolic")
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.MENU)
        self.saveBtn.add(image)
        
        """================"""
        self.historyBtn = Gtk.ToggleButton()
        #self.historyBtn.get_children()[0].remove(self.historyBtn.get_children()[0].get_children()[0])
        #arrow = self.historyBtn.get_children()[0].get_children()[0].get_children()[0]
        #self.historyBtn.get_children()[0].get_children()[0].remove(arrow)
        icon = Gio.ThemedIcon.new_with_default_fallbacks("document-open-recent-symbolic")
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.MENU)
        hbox = Gtk.Box()
        hbox.pack_start(image, False, False, 0)
        arrow = Gtk.Arrow()
        arrow.set(1,1)
        hbox.pack_start(arrow, False, False, 0)
        hbox.set_spacing(6)
        self.historyBtn.add(hbox)
        
        self.historyMenu = Gtk.Menu()
        #self.historyBtn.set_menu(self.documentMenu)
        """================"""
        
        hbox = Gtk.Box()
        self.saveBtn.get_style_context().add_class('linked')
        self.saveBtn.get_style_context().add_class('raised')
        self.historyBtn.get_style_context().add_class('linked')
        self.historyBtn.get_style_context().add_class('raised')
        hbox.pack_start(self.saveBtn, False, False, 0)
        hbox.pack_start(self.historyBtn, False, False, 0)
        self._rightBox.pack_start(hbox, False, False, 6)
        
        self.findBtn = Gtk.Button()
        hbox = Gtk.Box()
        icon = Gio.ThemedIcon.new_with_default_fallbacks("edit-find-symbolic")
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.MENU)
        label = Gtk.Label("Find")
        hbox.set_spacing(6)
        hbox.set_border_width(1)
        hbox.pack_start(image, False, False, 0)
        hbox.pack_start(label, False, False, 0)
        self.findBtn.add(hbox)
        self.findBtn.get_style_context().add_class('raised')
        self._rightBox.pack_start(self.findBtn, False, False, 0)
        
if __name__ == "__main__":
    window = Window()
    mainloop = GLib.MainLoop()
    window.connect("destroy", lambda window: mainloop.quit())
    mainloop.run()
