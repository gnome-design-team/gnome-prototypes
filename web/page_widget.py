from gi.repository import WebKit, Gtk, GLib, Gio, GObject, GdkPixbuf, Gdk
import cairo
from widgets import *
from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Event, Subject, Interpretation, Manifestation

ZG = ZeitgeistClient()

class PageView(View):
    def __init__(self):
        View.__init__(self)
        self.toolbar = PageToolbar()
        self.pack_start(self.toolbar, False, False, 0)
        
        self.webview = WebKit.WebView()
        
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add(self.webview)
        self.pack_start(scrolledWindow, True, True, 0)
        
        self.webview.connect("notify::title", self.toolbar._on_title_changed)
        self.webview.connect("notify::load-status", self.toolbar._on_uri_changed)
        self.webview.connect("notify::load-status", self._on_uri_changed)
        self.toolbar.backBtn.connect("clicked", lambda x: self.webview.go_back())
        self.toolbar.fwdBtn.connect("clicked", lambda x: self.webview.go_forward())
        self.toolbar.titleBtn.connect("clicked", self._on_title_btn_clicked)
        self.toolbar.uriEntry.connect("focus-out-event", self._on_entry_focus_out)
        self.toolbar.uriEntry.connect("activate", self._on_activate)
        self.current_uri = None
        self.current_title = None
        self.current_dom = None

    def get_title(self):
        return self.webview.get_title()
        
    def _on_activate(self, widget):
        text = widget.get_text()
        if not text.startswith("http://") and not text.startswith("https://")\
            and not text.startswith("ftp://"):
            widget.set_text("http://"+text)
            text = "http://"+text
        print text
        self.webview.open(text)
        
    def _on_entry_focus_out(self, widget, event):
        self.toolbar.uriEntry.hide()
        self.toolbar.titleBtn.show()
        self.toolbar._on_style_changed(widget)
        
    def _on_title_btn_clicked(self, btn):
        self.toolbar.titleBtn.hide()
        self.toolbar.uriEntry.show()
        self.toolbar.uriEntry.set_text(self.webview.get_uri())
        self.toolbar.hbox2.set_size_request(-1, -1)
        self.toolbar.uriEntry.grab_focus()
    
    def _on_uri_changed(self, webview, load_status):
        if self.webview.get_property("load-status") ==\
            WebKit.LoadStatus.FINISHED:
            if self.current_uri != self.webview.get_uri():
                if self.current_uri:
                    event = Event()
                    event.interpretation = Interpretation.LEAVE_EVENT
                    event.manifestation = Manifestation.USER_ACTIVITY
                    event.actor = "application://web.desktop"
                    subject = Subject()
                    subject.uri = self.current_uri
                    subject.mimetype = "text/html"
                    subject.text = self.current_title
                    subject.interpretation = Interpretation.WEBSITE
                    subject.manifestation = Manifestation.REMOTE_PORT_ADDRESS
                    event.subjects = [subject]
                    ZG.insert_event(event)
                self.current_uri = self.webview.get_uri()
                self.current_title = self.webview.get_title()
                print "===>", self.current_title 
                event = Event()
                event.interpretation = Interpretation.ACCESS_EVENT
                event.manifestation = Manifestation.USER_ACTIVITY
                event.actor = "application://web.desktop"
                subject = Subject()
                subject.uri = self.current_uri
                subject.mimetype = "text/html"
                subject.text = self.current_title
                subject.interpretation = Interpretation.WEBSITE
                subject.manifestation = Manifestation.REMOTE_PORT_ADDRESS
                event.subjects = [subject]
                ZG.insert_event(event)

class PageToolbar(Toolbar):
    def __init__(self):
        Toolbar.__init__(self)
        
        self.hbox1 = hbox1 = Gtk.Box()
        hbox1.set_homogeneous(True)
        self.pagesButton = Gtk.Button("Pages")
        hbox1.pack_start(self.pagesButton, True, True, 9)
        
        buttonbox = Gtk.Box()
        self.backBtn = Gtk.Button()
        icon = Gio.ThemedIcon.new_with_default_fallbacks("go-previous-symbolic")
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.backBtn.add(image)
        self.backBtn.get_style_context().add_class('linked')
        self.backBtn.get_style_context().add_class('raised')
        self.fwdBtn = Gtk.Button()
        icon = Gio.ThemedIcon.new_with_default_fallbacks("go-next-symbolic")
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.fwdBtn.add(image)
        self.fwdBtn.get_style_context().add_class('linked')
        self.fwdBtn.get_style_context().add_class('raised')
        buttonbox.pack_start(self.backBtn, False, False, 0)
        buttonbox.pack_start(self.fwdBtn, False, False, 0)
        
        hbox1.pack_start(buttonbox, False, False, 9)
        
        self._leftGroup.add(hbox1)
        self._leftGroup.set_expand(False)
        
        hbox = Gtk.Box()
        self._centerGroup.add(hbox)
        self._centerGroup.set_expand(True)
        self.titleBtn = Gtk.Button()
        self.titleBtn.set_relief(Gtk.ReliefStyle.NONE)
        self.titleLabel = Gtk.Label()
        self.titleBtn.add(self.titleLabel)
        self.uriEntry= Gtk.Entry()
        
        hbox.pack_start(self.titleBtn, True, True, 9)
        hbox.pack_start(self.uriEntry, True, True, 9)
        
        self.hbox2 = hbox2 = Gtk.Box()
        self.shareBtn = Gtk.Button()
        icon = Gio.ThemedIcon.new_with_default_fallbacks("emblem-shared-symbolic")
        image = Gtk.Image()
        image.set_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.shareBtn.add(image)
        hbox2.pack_end(self.shareBtn, False, False, 9)
        self._rightGroup.add(hbox2)
        self.connect("style-updated", self._on_style_changed)
        
    def _on_uri_changed(self, webview, prop):
        if webview.can_go_back():
            self.backBtn.set_sensitive(True)
        else:
            self.backBtn.set_sensitive(False)
        if webview.can_go_forward():
            self.fwdBtn.set_sensitive(True)
        else:
            self.fwdBtn.set_sensitive(False)
        
        
    def _on_title_changed(self, webview, prop):
        self.titleLabel.set_markup("<b>%s</b>"%webview.get_title())
    
    def _on_style_changed(self, widget):
        self.hbox2.set_size_request(self.hbox1.get_allocation().width, -1)
        self.uriEntry.hide()


class Pages(Gtk.Notebook):
    __gsignals__ = {
        "view-pages": (GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE,
                   ())
                   }
                   
    def __init__(self):
        Gtk.Notebook.__init__(self)
        self.set_show_tabs(False)
        
    def add(self, uri):
        page = PageView()
        page.toolbar.pagesButton.connect("clicked", lambda x: self.emit("view-pages"))
        page.webview.open(uri)
        self.append_page(page, Gtk.Label("uri"))
        
        GObject.idle_add(lambda: self.set_current_page(self.page_num(page)))
        self.show_all()

class PageButton(Gtk.Button):
    def __init__(self, subject):
        Gtk.Button.__init__(self)
        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.subject = subject
        label = Gtk.Label()
        print subject.text
        label.set_markup("<b>%s</b>"%subject.text)
        label.set_ellipsize(2)
        box.pack_end(label, False, False, 0)
        self.set_size_request(202, 144)
        self.add(box)
        self.show_all()

class PageOverviewWidget(Gtk.Button):
    def __init__(self, page):
        Gtk.Button.__init__(self)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.page = page
        title = Gtk.Label()
        title.set_markup("<b>%s</b>"%self.page.get_title())
        title.set_ellipsize(3)
        box.pack_end(title, False, False, 3)
        self.add(box)
        
        hbox = Gtk.Box()
        self.closeBtn = Gtk.Button.new_from_stock("gtk-close")
        #hbox.pack_end(self.closeBtn, False, False, 0)
        box.pack_start(hbox, True, True, 0)
        
        self.set_size_request(196, -1)
        pixbuf = self._create_pixbuf()
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        box.pack_start(image, False, False, 0)
        self.set_relief(Gtk.ReliefStyle.NONE)
    
    def _create_pixbuf(self):
        view = self.page.webview
        
        allocation = view.get_allocation()
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, allocation.width, allocation.height)
        cr = cairo.Context(surface)
        
        width, height = (allocation.width, allocation.height)
        cr.rectangle(0, 0, width, height)
        view.draw(cr)
        
        new_height = (196*height)/width
        
        snapshot = Gdk.pixbuf_get_from_surface(surface, 0, 0, width, height)
        snapshot = snapshot.scale_simple(196, new_height, 1)
        return snapshot
        
