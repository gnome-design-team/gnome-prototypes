#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, GLib, GObject
from home_widget import HomeView
from page_widget import Pages, PageOverviewWidget, ZG, PageButton
from zeitgeist.datamodel import Event, Subject

class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_size_request(1024, 600)
        
        self.set_title("Web")
        
        self.box = Gtk.Notebook()
        
        self.pages = Pages()
        self.home = HomeView(self.pages)
        
        self.pages.connect("view-pages", self._on_view_pages)
        
        self.box.append_page(self.home, Gtk.Label("Home"))
        self.box.append_page(self.pages, Gtk.Label("Pages"))
        
        self.pages.add("http://www.google.com")
        self.pages.add("http://www.gnome.org")
        self.pages.add("http://www.facebook.com")
        self.pages.add("http://www.twitter.com")
        self.pages.add("http://www.kde.org")
        self.pages.add("http://www.ubuntu.com")
        
        self.add(self.box)
        self.show_all()
        self.box.set_current_page(1)
        self.box.set_show_tabs(False)
        
    def _on_view_pages(self, widget):
        self.home.reset()
        uris = []
        for pIndex in xrange(self.pages.get_n_pages()):
            self.pages.set_current_page(pIndex)
            page = self.pages.get_nth_page(pIndex)
            overviewPage = PageOverviewWidget(page)
            overviewPage.connect("clicked", self._on_page_clicked)
            self.home.add_page(overviewPage)
            uris.append(page.webview.get_uri())
        self.home.show_all()
        self.box.set_current_page(0)
        
        def callback(events):
            self.home.recentDashboard.recentPages.reset()
            for event in events:
                page = PageButton(event.subjects[0])
                print event.subjects[0].uri
                self.home.recentDashboard.recentPages.add_page(page)
            self.home.show_all()
        event = Event()
        event.actor = "application://web.desktop"
        event.subjects = []
        for uri in uris:
            if uri:
                subject = Subject()
                subject.uri = "!"+uri
                event.subjects.append(subject)
        print event
        ZG.find_events_for_template(event, callback, result_type=2)
    
    def _on_page_clicked(self, widget):
        self.box.set_current_page(1)
        self.pages.set_current_page(self.pages.page_num(widget.page))
        self.pages.show()

if __name__ == "__main__":
    window = Window()
    mainloop = GLib.MainLoop()
    window.connect("destroy", lambda window: mainloop.quit())
    mainloop.run()

