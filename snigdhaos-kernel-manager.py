#!/usr/bin/env python3

import os
import gi
import libs.functions as fn
from ui.ManagerGUI import ManagerGUI
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib, Gdk

base_dir = fn.os.path.dirname(fn.os.path.realpath(__file__))

app_name = "Snigdha OS Kernel Manager"
app_version = "${app_version}"
app_name_dir = "snigdhaos-kernel-manager"
app_id = "org.snigdhaos.kernelmanager"
lock_file = "/tmp/skm.lock"
pid_file = "/tmp/skm.pid"


class Main(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=app_id, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        # retrieves the default GLib MainContext, which represents the main event loop
        # GLib is a low-level core library that forms the basis of GTK and GNOME.
        default_context = GLib.MainContext.default()
        # tries to access the active_window property of the object (self) invoking this method
        win = self.props.active_window
        # checks if win is None (which would mean there's no active window)
        # if there's no active window, it creates a new instance of ManagerGUI
        if not win:
            win = ManagerGUI(
                application=self,
                app_name=app_name,
                default_context=default_context,
                app_version=app_version,
            )
        # retrieves the display associated with the window win. Gtk.Widget.get_display() 
        # returns the display that win is on.
        display = Gtk.Widget.get_display(win)

        # sets the icon for the window win to "snigdhaos-kernel-manager-tux"
        win.set_icon_name("snigdhaos-kernel-manager-tux")
        # creates a new instance of Gtk.CssProvider
        # which is used to load CSS stylesheets to style GTK widgets.
        provider = Gtk.CssProvider.new()
        # creates a new Gio.File object representing the CSS file at the path base_dir + "/snigdhaos-kernel-manager.css"
        css_file = Gio.file_new_for_path(base_dir + "/snigdhaos-kernel-manager.css")
        provider.load_from_file(css_file)
        Gtk.StyleContext.add_provider_for_display(
            display, 
            provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        win.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)
        if os.path.exists(lock_file):
            os.remove(lock_file)
        if os.path.exists(pid_file):
            os.remove(pid_file)


def signal_handler(sig, frame):
    Gtk.main_quit(0)

if __name__ == "__main__":
    try:
        # signal.signal(signal.SIGINT, signal_handler)
        if not fn.os.path.isfile(lock_file):
            with open(pid_file, "w") as f:
                f.write(str(fn.os.getpid()))
            # splash = SplashScreen()
            app = Main()
            app.run(None)
        else:
            md = Gtk.MessageDialog(
                parent=Main(),
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.YES_NO,
                text="%s Lock File Found" % app_name,
            )
            md.format_secondary_markup(
                "A %s lock file has been found. This indicates there is already an instance of <b>%s</b> running.\n\
                Click 'Yes' to remove the lock file and try running again"
                % (lock_file, app_name)
            )  # noqa

            result = md.run()
            md.destroy()

            if result in (Gtk.ResponseType.OK, Gtk.ResponseType.YES):
                pid = ""
                if fn.os.path.exists(pid_file):
                    with open(pid_file, "r") as f:
                        line = f.read()
                        pid = line.rstrip().lstrip()
                else:
                    fn.os.unlink(lock_file)
                    fn.sys.exit(1)
            else:
                fn.sys.exit(1)
    except Exception as e:
        print("Exception in __main__: %s" % e)