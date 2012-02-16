from gi.repository import Gtk, GLib, GObject, Gio
from widgets import *

class ToggleButton(Gtk.ToggleButton):
    def __init__(self, text):
        Gtk.ToggleButton.__init__(self)
        self.text = text
        self.label = Gtk.Label()
        self.label.set_markup("  %s  " %text)
        self.add(self.label)
        self.connect("toggled", self._on_toggled)
        self.set_size_request(100, 34)
        
    def _on_toggled(self, label):
        if self.get_active():
            self.label.set_markup("<b>  %s  </b>"%self.text)
        else:
            self.label.set_markup("  %s  " %self.text)

class HomeToolbar(Toolbar):
    __gsignals__ = {
        "switched": (GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE,
                   (GObject.TYPE_INT,)),
                   }
    def __init__(self):
        Toolbar.__init__(self)
        
        self._rightGroup.set_expand(True)
        self._leftGroup.set_expand(True)
        
        hbox = Gtk.HBox()
        hbox.set_homogeneous(True)
        #gtk_style_context_add_class (hbox.get_style_context (hbox), "linked");
        
        recentBtn = ToggleButton("Recent")
        favoriteBtn = ToggleButton("Favorites")
        queueBtn = ToggleButton("Queue")
        
        hbox.get_style_context().add_class("linked")
        self.toggleBtns = btns = [recentBtn, favoriteBtn, queueBtn]
        for button in btns:
            button.get_style_context().add_class('linked');
            button.get_style_context().add_class('raised');
            hbox.pack_start(button, True, True, 0)
            button.connect("toggled", self._on_toggled)
        
        self._centerGroup.add(hbox)
        self._is_busy = False
        
        recentBtn.set_active(True)
        
    def _on_toggled(self, widget):
        if not self._is_busy:
            self._is_busy = True
            for btn in self.toggleBtns:
                if not btn == widget:
                    btn.set_active(False)
                else:
                    if not btn.get_active():
                        btn.set_active(True)
            self._is_busy = False
            self.emit("switched", self.toggleBtns.index(widget))
            

class HomeView(View):
    def __init__(self, pages):
        View.__init__(self)
        
        self.pages = pages
        
        box = Gtk.Box()
        box.set_size_request(-1, 1)
        self.pack_start(box, False, False, 0)
        
        self.toolbar = HomeToolbar()
        self.pack_start(self.toolbar, False, False, 0)
        

        
        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        
        self.recentDashboard = RecentDashboard()
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledWindow.add_with_viewport(self.recentDashboard)
        self.notebook.append_page(scrolledWindow, Gtk.Label("Recent"))
        
        self.favDashboard = FavoriteDashboard()
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledWindow.add_with_viewport(self.favDashboard)
        self.notebook.append_page(scrolledWindow, Gtk.Label("Favorties"))
        
        self.queueDashboard = QueueDashboard()
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledWindow.add_with_viewport(self.queueDashboard)
        self.notebook.append_page(scrolledWindow, Gtk.Label("Queue"))
        
        self.pack_start(self.notebook, True, True, 0)
        
        self.toolbar.connect("switched", self._on_switched)
        
    def _on_switched(self, widget, index):
        self.notebook.set_current_page(index)
        
    def reset(self):
        self.recentDashboard.reset()
        
    def add_page(self, page):
        self.recentDashboard.add_page(page)

class RecentDashboard(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        
        self.openPages = OpenPages()
        self.pack_start(self.openPages, False, False, 0)
        
        self.recentPages = CurrentPages()
        self.pack_start(self.recentPages, False, False, 0)
        
    def add_page(self, page):
        self.openPages.add_page(page)
        
    def reset(self):
        self.openPages.grid.reset()
        self.recentPages.reset()

class FavoriteDashboard(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

class QueueDashboard(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        
class OpenPages(Gtk.Toolbar):
    def __init__(self):
        Gtk.Toolbar.__init__(self)
        self.get_style_context().add_class("primary-toolbar");
        
        item = Gtk.ToolItem()
        
        self.search = SearchEntry()
        box = Gtk.Box()
        box.pack_start(Gtk.Box(), True, True, 0)
        box.pack_start(self.search, False, False, 0)
        box.pack_start(Gtk.Box(), True, True, 0)
        
        vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        vbox.set_border_width(3)
        vbox.pack_start(box, False, False, 9)
        item.add(vbox)
        item.set_expand(True)
        #self.pack_start(item, True, True, 0)
        self.insert(item, 0)
        
        self.grid = ItemGrid()
        vbox.pack_start(self.grid, True, True, 0)
    
    def add_page(self, page):
        self.grid.add_page(page)

class CurrentPages(ItemGrid):
    def __init__(self):
        ItemGrid.__init__(self)
        self.set_border_width(3)

class SearchEntry(Gtk.Entry):
    __gsignals__ = {
        "clear": (GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE,
                   ()),
        "search": (GObject.SIGNAL_RUN_FIRST,
                    GObject.TYPE_NONE,
                    (GObject.TYPE_STRING,)),
        "close": (GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE,
                   ()),
    }

    search_timeout = 0

    def __init__(self, accel_group = None):
        Gtk.Entry.__init__(self)
        self.set_width_chars(40)
        self.set_placeholder_text("Search...")
        self.connect("changed", lambda w: self._queue_search())

        search_icon =\
            Gio.ThemedIcon.new_with_default_fallbacks("edit-find-symbolic")
        self.set_icon_from_gicon(Gtk.EntryIconPosition.PRIMARY, search_icon)
        clear_icon =\
            Gio.ThemedIcon.new_with_default_fallbacks("edit-clear-symbolic")
        self.set_icon_from_gicon(Gtk.EntryIconPosition.SECONDARY, clear_icon)
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


