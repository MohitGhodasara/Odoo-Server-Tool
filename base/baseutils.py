import time
import sys
import platform
import base64
from .slash_x import hex_


class utils():

    if sys.version_info[0] >= 3:
        from tkinter import messagebox
    else:
        import tkMessageBox as messagebox

    def performance(method):
        def perform(*args, **kwargs):
            ts = time.time()
            result = method(*args, **kwargs)
            te = time.time()
            print('Function', method.__name__, 'time:',
                  round((te - ts) * 1000, 8), 'ms')
            return result
        return perform

    def lambda_bind(self, control_key, key=False, bind=None, bind_with=None, display_key=True):
        if not callable(bind) and bind.winfo_class() in ['Button', 'Checkbutton']:
            method = self.invoke_widget
            if display_key:
                self.set_key(bind, display_key if isinstance(display_key, str) else control_key[1:-1])
            if bind.winfo_class() == 'Button':
                bind.bind("<Return>", lambda call: method(bind))
        elif not callable(bind) and bind.winfo_class() in ['Entry', 'TCombobox']:
            method = self.set_focus_select
        elif not callable(bind) and bind.winfo_class() in ['Listbox']:
            method = self.set_focus
        else:
            method = None
        if bind_with and display_key:
            self.set_key(bind_with, control_key[1:-1])
            bind.bind("<Control-a>", lambda call: self.select_all(bind))
        self.master.bind(control_key, lambda call: method(bind)) if method else self.master.bind(control_key, bind)
        self.master.bind(key, lambda call: method(bind)) if key else None

    def set_os(self):
        self.os = platform.system().lower()

    def set_terminal(self, default=False):
        if self.is_path(self.terminal_str.get()) and not default:
            if self.terminal_option:
                self.default_terminal = '%s||%s' % (self.terminal_str.get(), self.terminal_option)
            else:
                self.default_terminal = self.terminal_str.get()
        else:
            if self.os == 'linux' and self.is_terminal('gnome-terminal'):
                self.terminal_option = self.terminal_option if self.terminal_option else '--maximize||--'
                self.default_terminal = 'gnome-terminal||%s' % self.terminal_option
            elif self.os == 'darwin':
                self.terminal_option = self.terminal_option if self.terminal_option else '-a'
                self.default_terminal = 'open||%s||Terminal' % self.terminal_option
            elif self.os == 'windows':
                self.terminal_option = self.terminal_option if self.terminal_option else '/c'
                self.default_terminal = 'start||cmd.exe||%s' % self.terminal_option
            else:
                self.os = None
                if self.is_terminal('gnome-terminal'):
                    self.default_terminal = 'gnome-terminal'
                else:
                    self.default_terminal = 'bash'
                    self.default_terminal_nodebug = 'bash'

    def always_on_top(self, event=None):
        self.master.attributes('-topmost', event)
        if event:
            self.master.wm_attributes('-alpha', 0.7)
            self.master.bind('<FocusIn>', lambda event: self.master.wm_attributes('-alpha', 1))
            self.master.bind('<FocusOut>', lambda event: self.master.wm_attributes('-alpha', 0.7))
        else:
            self.master.wm_attributes('-alpha', 1)
            self.master.unbind('<FocusIn>')
            self.master.unbind('<FocusOut>')

    def update_list_status(self, event=None):
        for port in self.get_column("port"):
            if self.is_port_running(port):
                self.set_runbox_port_color(port, self.primary_color)
            else:
                self.set_runbox_port_color(port, self.danger_color)

    def set_focus(self, widget):
        widget.focus()

    def set_focus_select(self, widget):
        self.set_focus(widget)
        self.select_all(widget)
        return 'break'

    def prevent_default(self):
        return 'break'

    def invoke_widget(self, widget):
        widget.invoke()

    def select_all(self, widget):
        widget.selection_range(0, "end")
        return 'break'

    def replace_key(self, dictionary):
        for key, val in dictionary.items():
            val['object'].configure(text=key, fg=val['fg'], bg=val['bg'])

    def force_shortcuts_release(self):
        if self.keys:
            self.shortcuts_release(event=True)

    def shortcuts_release(self, event=None):
        if isinstance(event, bool) == event or (event.keycode in (37, 262145) and self.keys):
            self.keys = False
            self.replace_key(self.widget_name)

    def shortcuts_press(self, event=None):
        if event.keycode in (37, 262145) and not self.keys:
            self.keys = True
            self.replace_key(self.widget_keys)

    def set_key(self, widget, key):
        widget_config = {'object': widget, 'fg': widget.cget('fg'), 'bg': widget.cget('bg')}
        self.widget_name[widget.cget('text')] = widget_config
        self.widget_keys[key] = widget_config

    def validate(self, action, prior_value, text):
        if(action == '1'):
            if text in '0123456789':
                port = (int(prior_value if prior_value != '' else 0) * 10) + int(text if text != '' else 0)
                return True if port <= 65535 else False
            else:
                return False
        else:
            return True

    def check_path(self, event=None, alert=True):
        if self.ent.get():
            if all([self.is_path(self.enterprise_str.get()), self.is_path(self.enterprise_str.get())]):
                return True
            else:
                if alert:
                    messagebox.showerror(*hex_['addons_err'])
                self.ent.set(0)

    def add_separator(self, str_):
        return str_.replace(" ", "||")

    def remove_separator(self, str_):
        return str_.replace("||", " ")

    def reset_keys(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            args[0].force_shortcuts_release()
            return result
        return wrapper

    def get_server_status(self):
        path = self.server_str.get()
        return True if self.is_server_path(path) else False

    def get(self, name):
        return {'index': 0, 'database': 1, 'port': 2, 'thread': 3, 'status': 4}[name]

    def set_value(self, search_column, search_val, set_column, set_val):
        self.data[self.get_column(search_column).index(search_val)][
            self.get(set_column)] = set_val

    def get_value(self, search_column, search_val, get_column):
        try:
            return self.data[self.get_column(search_column).index(search_val)][self.get(get_column)]
        except:
            return None

    def get_column(self, name):
        return list(zip(*self.data))[self.get(name)] if self.data else []

    def create_data(self, object_data, last_index=None):
        index = object_data[self.get('index')] if isinstance(object_data, list) else self.index
        database = object_data[self.get('database')] if isinstance(object_data, list) else self.database_box.get()
        port = object_data[self.get('port')] if isinstance(object_data, list) else self.port_box.get()
        thread = "Object" if isinstance(object_data, list) else object_data
        self.run_box.insert(self.index, "   {:<15} Running on : {}".format(database, port))
        if isinstance(last_index, int):
            self.set_value('index', last_index, 'database', database)
        else:
            self.data.append(list((index, database, port, thread, 'Running')))
            self.index += 1

    def transform(self, str_):
        return base64.b64decode(str_)

    def update_port_list(self):
        if self.get_column("port"):
            self.running_port_list = self.get_column("port")
            self.port_box.configure(values=self.running_port_list)
        return True if len(self.running_port_list) > 0 else False

    def on_runbox_focusout(self, event):
        self.run_box.selection_clear(0, "end")
