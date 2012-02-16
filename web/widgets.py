from gi.repository import Gtk, GLib

class Toolbar(Gtk.Toolbar):
    def __init__(self):
        Gtk.Toolbar.__init__(self)
        
        self.set_icon_size(Gtk.IconSize.LARGE_TOOLBAR)
        
        self._rightGroup = Gtk.ToolItem()
        self._centerGroup = Gtk.ToolItem()
        self._leftGroup = Gtk.ToolItem()
        
        self.insert(self._leftGroup, -1)
        self.insert(self._centerGroup, -1)
        self.insert(self._rightGroup, -1)

class View(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        
class ItemGrid(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.widgets = []
        
    def reset(self):
        print "==>"
        self.widgets = []
        for widget in self.get_children():
            self.remove(widget)
        
    def add_page(self, widget):
        index = len(self.widgets)%4
        if index == 0:
            hbox = Gtk.Box()
            hbox.set_homogeneous(True)
            self.pack_start(hbox, False, False, 6)
            for i in xrange(4):
                hbox.pack_end(Gtk.Label(), False, False, 6)
        
        hbox = self.get_children()[-1]
        hbox.remove(hbox.get_children()[index])
        hbox.pack_start(widget, False, False, 6)
        self.widgets.append(widget)
