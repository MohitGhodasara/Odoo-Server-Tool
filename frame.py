# !/usr/bin/env python3
# coding: utf-8

import os

from base import *
from base.baseutils import utils
from base.config_manager import config
from base.psql_database import psql
from base.version_manager import version
from base.os_control import control
from base.slash_x import hex_


class server(tk.Frame, control, version, psql):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.set_os()
        self.version_bool = True
        if not self.version_control():
            self.version_bool = False
            return None
        self.master = master
        self.master.title("Server Tool")
        self.icon = tk.Image("photo", data=hex_['icon_base64'] if sys.version_info[0] >= 3 else "")
        self.logo = tk.Image("photo", data=hex_['logo_base64'] if sys.version_info[0] >= 3 else "")
        self.master.tk.call('wm', 'iconphoto', self.master._w, self.icon)
        self.master.resizable(False, False)
        self.master.geometry("490x300")
        self.master.protocol("WM_DELETE_WINDOW", self.on_exit)

        self.login_window = tk.Toplevel(self, class_="Login")
        self.login_window.tk.call('wm', 'iconphoto', self.login_window._w, self.icon)
        self.login_window.resizable(False, False)
        self.login_window.geometry("0x0")
        self.login_window.protocol("WM_DELETE_WINDOW", lambda: self.on_toplevel_exit(self.login_window))

        self.paths_window = tk.Toplevel(self, class_="Path")
        self.paths_window.tk.call('wm', 'iconphoto', self.paths_window._w, self.icon)
        self.paths_window.resizable(False, False)
        self.paths_window.geometry("0x0")
        self.paths_window.protocol("WM_DELETE_WINDOW", lambda: self.on_toplevel_path_exit(self.paths_window))
        self.paths_window.withdraw()

        self.data = []
        self.index = 0
        self.sql = False
        self.keys = False
        self.U_I = True
        self.connection_data = {}
        self.db_list = []
        self.running_port_list = []
        self.widget_name = {}
        self.widget_keys = {}
        self.geometry = "490x300"
        self.geometry_basic = "120x160"
        self.primary_color = "#875A7B"
        self.danger_color = "#F16567"
        self.secondary_color = "#00A09D"
        self.white_color = "#ffffff"
        self.active_color = "#007a77"
        self.terminal_option = ''

        self.style_btn = {} if self.os == 'darwin' else {"highlightbackground" if self.os == 'darwin' else "bg": self.secondary_color, "fg": self.white_color, "activebackground": self.active_color, "activeforeground": self.white_color}
        self.style_small_btn = {} if self.os == 'darwin' else {"highlightbackground" if self.os == 'darwin' else "bg": self.primary_color, "fg": self.white_color, "activebackground": self.active_color, "activebackground": self.active_color, "activeforeground": self.white_color}

        self.logo_label = tk.Label(self, text="odoo", font=font.Font(size=20, weight='bold'), fg=self.white_color, bg=self.primary_color)
        self.database_label = tk.Label(self, text="Database")
        self.port_label = tk.Label(self, text="Server Port")
        self.module_label = tk.Label(self, text="Module")

        self.host_str = tk.StringVar(self.login_window, value="127.0.0.1")
        self.database_str = tk.StringVar(self.login_window, value="postgres")
        self.username_str = tk.StringVar(self.login_window, value="openpg" if self.os == "windows" else "postgres")
        self.password_str = tk.StringVar(self.login_window, value="openpgpwd" if self.os == "windows" else "postgres")
        self.autosave = tk.IntVar(self.login_window, value=0)

        self.server_str = tk.StringVar(self.paths_window, value="/")
        self.community_str = tk.StringVar(self.paths_window, value="(optional)")
        self.enterprise_str = tk.StringVar(self.paths_window, value="(optional)")
        self.python_str = tk.StringVar(self.paths_window, value="(optional)")
        self.terminal_str = tk.StringVar(self.paths_window, value="(optional)")

        self.module_str = tk.StringVar(self.master, value="")
        self.module_box = tk.Entry(self, textvariable=self.module_str)
        self.module_box.insert("0", "")
        self.lambda_bind('<Control-m>', '<Alt-m>', self.module_box, self.module_label)

        self.database_box = ttk.Combobox(self)
        self.database_box.bind("<<ComboboxSelected>>")
        self.database_box.bind('<FocusOut>', self.update_db_list)

        # self.database_box.bind('<Button-1>', lambda event: self.prevent_default())
        self.lambda_bind('<Control-d>', '<Alt-d>', self.database_box, self.database_label)

        self.default_port = tk.IntVar(self.master, value=8069)
        self.port_box = ttk.Combobox(self, textvariable=self.default_port, validate='key', validatecommand=(self.master.register(self.validate), '%d', '%s', '%S'))
        self.port_box.bind("<KeyRelease>", self.on_port_key_press)
        self.port_box.bind("<FocusOut>", self.on_portbox_focusout)
        self.lambda_bind('<Control-a>', '<Alt-a>', self.port_box, self.port_label)

        self.start_btn = tk.Button(self, text="Start", command=lambda: self.on_toggle(), relief="raised", **self.style_btn)
        self.lambda_bind('<Control-r>', '<Alt-r>', self.start_btn, display_key=False)
        self.lambda_bind('<Control-s>', '<Alt-s>', self.start_btn)

        self.debug = tk.IntVar()
        self.debug.set(1)
        self.debug_mode = tk.Checkbutton(self, text="Debug", variable=self.debug, command=lambda: self.save_config())
        self.lambda_bind('<Control-v>', '<Alt-v>', self.debug_mode)

        self.with_data = tk.IntVar()
        self.with_data.set(1)
        self.with_demo_data = tk.Checkbutton(self, text="With Data", variable=self.with_data, command=lambda: self.save_config())
        self.lambda_bind('<Control-w>', '<Alt-w>', self.with_demo_data)

        self.template = tk.IntVar()
        self.template.set(0)
        self.template_mode = tk.Checkbutton(self, text="template", variable=self.template, command=lambda: self.on_template_mode())
        self.lambda_bind('<Alt-t>', '<Alt-t>', self.template_mode)

        self.session = tk.IntVar()
        self.session.set(0)
        self.multi_session = tk.Checkbutton(self, text="Multi Session", variable=self.session, command=lambda: self.save_config())
        self.lambda_bind('<Control-b>', '<Alt-b>', self.multi_session)

        self.ent = tk.IntVar()
        self.ent.set(1)
        self.enterprise = tk.Checkbutton(self, text="Enterprise", variable=self.ent, command=lambda: self.check_path())
        self.lambda_bind('<Control-e>', '<Alt-e>', self.enterprise)

        self.kill_btn = tk.Button(self, text="Terminate", command=lambda: self.on_terminate(), **self.style_btn)
        self.lambda_bind('<Control-t>', '<Control-Delete>', self.kill_btn)

        self.delete_btn = tk.Button(self, text="Delele", command=lambda: self.on_delete(), **self.style_btn)
        self.lambda_bind('<Control-x>', '<Alt-x>', self.delete_btn)

        self.stop_btn = tk.Button(self, text="Stop", command=lambda: self.on_stop(), **self.style_btn)
        self.lambda_bind('<Control-c>', '<Alt-c>', self.stop_btn)

        self.about_btn = tk.Button(self, text="✍", command=lambda: self.on_about(), relief="raised", font=font.Font(size=12, weight='bold'), bg=self.white_color)

        self.dir_path = tk.Button(self, text="Config", command=lambda: self.get_path_window(), font=font.Font(size=7), **self.style_small_btn)
        self.lambda_bind('<Control-slash>', '<Alt-slash>', self.dir_path, display_key=False)

        self.advanced_mode = tk.IntVar()
        self.advanced_mode.set(1)
        self.advanced_btn = tk.Button(self, text="▶▶", command=lambda: self.resize_window(), font=font.Font(size=7), **self.style_small_btn)
        self.lambda_bind('<Control-space>', '<Alt-space>', self.advanced_btn, display_key=False)

        self.items = tk.Variable()
        self.run_box = tk.Listbox(self, listvariable=self.items)
        self.run_box.bind("<<ListboxSelect>>", self.on_item_select)
        self.run_box.bind("<FocusOut>", self.on_runbox_focusout)
        self.lambda_bind('<Control-l>', '<Alt-l>', self.run_box)

        self.U_I_btn = tk.Button(self, text="U", command=lambda: self.on_U_I(), **self.style_small_btn)
        self.lambda_bind('<Control-u>', '<Alt-u>', self.U_I_btn, display_key=False)
        self.lambda_bind('<Control-i>', '<Alt-i>', self.U_I_btn, display_key=False)

        self.delete_db_btn = tk.Button(self, text="D", command=lambda: self.on_delete_db(), **self.style_small_btn)
        # self.lambda_bind('<Control-Delete>', '<Delete>', self.delete_db_btn)
        self.port_up = tk.Button(self, text="▲", command=lambda: self.on_port_btn('up'), font=font.Font(size=6), **self.style_small_btn)
        self.port_down = tk.Button(self, text="▼", command=lambda: self.on_port_btn('down'), font=font.Font(size=6), **self.style_small_btn)
        self.load_config()
        self.update_list_status()
        self.set_terminal()

        self.lambda_bind('<KeyPress>', bind=self.shortcuts_press)
        self.lambda_bind('<KeyRelease>', bind=self.shortcuts_release)
        self.lambda_bind('<Control-q>', bind=self.on_exit)
        self.lambda_bind('<Prior>', bind=lambda event: self.always_on_top(True))
        self.lambda_bind('<Next>', bind=lambda event: self.always_on_top(False))
        self.master.bind('<FocusIn>', self.update_list_status)
        self.place_all()
        self.place()

    @utils.reset_keys
    def resize_window(self):
        if self.advanced_mode.get():
            def geometry(x, y, height=25, width=110):
                # 40 110 40 110 40 110 40
                col = (10, 190, 340)
                row = (30, 70, 100, 165, 205, 245)
                return {'x': col[x], 'y': row[y], 'height': height, 'width': width}
            self.master.withdraw()
            self.advanced_mode.set(0)

            self.module_label.place_forget()
            self.module_box.place_forget()
            self.module_box.place_forget()
            self.debug_mode.place_forget()
            self.multi_session.place_forget()
            self.run_box.place_forget()
            self.dir_path.place_forget()
            self.U_I_btn.place_forget()
            self.logo_label.place_forget()

            self.logo_label.place(x=0, y=0, height=25, width=120)
            self.logo_label.config(font=font.Font(size=10, weight='bold'))

            self.start_btn.place(x=10, y=105, height=25, width=50)
            self.stop_btn.place(x=60, y=105, height=25, width=50)

            self.delete_db_btn.place(x=10, y=68, height=27, width=20)
            self.database_box.place(x=29, y=70, height=25, width=80)

            if self.os == 'darwin':
                self.port_box.place(x=33, y=35, height=25, width=77)
                self.port_up.place(x=10, y=35, height=25, width=13)
                self.port_down.place(x=23, y=35, height=25, width=13)
            else:
                self.port_box.place(x=29, y=35, height=25, width=80)
                self.port_up.place(x=10, y=35, height=13, width=20)
                self.port_down.place(x=10, y=47, height=13, width=20)

            self.about_btn.place(x=85, y=138, height=20, width=25)
            self.advanced_btn.place(x=10, y=138, height=20, width=25)
            self.advanced_btn.config(text="◀◀")

            font_basic = font.Font(size=10 if self.os == 'darwin' else 8)
            self.start_btn.config(font=font_basic)
            self.stop_btn.config(font=font_basic)
            self.delete_db_btn.config(font=font_basic)
            self.database_box.config(font=font_basic)
            self.port_box.config(font=font_basic)

            self.geometry = self.master.winfo_geometry()
            if self.geometry_basic == "120x160":
                self.geometry_basic = "120x160-0-0"
            self.master.geometry(self.geometry_basic)
            self.master.update_idletasks()
            self.master.bind('<Button-1>', self.clickwin)
            self.master.bind('<B1-Motion>', self.dragwin)
            if self.os == "linux":
                self.master.wm_attributes('-type', 'popup_menu')
            elif self.os == "windows":
                self.master.overrideredirect(1)
            else:
                self.master.unbind('<Button-1>')
                self.master.unbind('<B1-Motion>')
                pass
            self._offsetx = 0
            self._offsety = 0
            self.always_on_top(True)
            self.master.deiconify()
            self.master.focus_force()
        else:
            self.master.withdraw()
            self.advanced_mode.set(1)
            self.advanced_btn.config(text="▶▶")
            self.start_btn.config(font="TkDefaultFont")
            self.stop_btn.config(font="TkDefaultFont")
            self.delete_db_btn.config(font="TkDefaultFont")
            self.database_box.config(font="TkDefaultFont")
            self.port_box.config(font="TkDefaultFont")
            self.geometry_basic = self.master.winfo_geometry()
            self.master.geometry(self.geometry)
            self.master.update_idletasks()
            self.master.unbind('<Button-1>')
            self.master.unbind('<B1-Motion>')
            if self.os == "linux":
                self.master.wm_attributes('-type', 'normal')
            elif self.os == "windows":
                self.master.overrideredirect(0)
            else:
                pass
            self.master.wm_state('normal')
            self.logo_label.config(font=font.Font(size=20, weight='bold'))
            self.place_all()

            self.always_on_top(False)
            self.master.update_idletasks()
            self.master.deiconify()
            self.master.focus_force()

    def dragwin(self, event):
        x = self.master.winfo_pointerx() - self._offsetx
        y = self.master.winfo_pointery() - self._offsety
        self.master.geometry('+{x}+{y}'.format(x=x, y=y))

    def clickwin(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def place_all(self):
        def geometry(x, y, height=25, width=110):
            # 40 110 40 110 40 110 40
            col = (40, 190, 340)
            row = (60, 90, 125, 165, 205, 245)
            return {'x': col[x], 'y': row[y], 'height': height, 'width': width}

        self.logo_label.place(x=0, y=0, height=45, width=490)
        self.module_label.place(geometry(0, 0))
        self.database_label.place(geometry(1, 0))
        self.port_label.place(geometry(2, 0))

        self.debug_mode.place(x=40, y=125, height=25)
        self.multi_session.place(x=40, y=155, height=25)
        self.with_demo_data.place(x=190, y=125, height=25)
        self.enterprise.place(x=190, y=155, height=25)

        self.module_box.place(x=58, y=90, height=25, width=90)
        self.database_box.place(x=210, y=90, height=25, width=85)
        self.port_box.place(x=364, y=90, height=25, width=86)

        self.about_btn.place(x=461, y=278, height=20, width=25)
        self.U_I_btn.place(x=40, y=89, height=27, width=20)
        self.delete_db_btn.place(x=191, y=89, height=27, width=20)
        if self.os == 'darwin':
            self.port_up.place(x=340, y=90, height=25, width=13)
            self.port_down.place(x=353, y=90, height=25, width=13)
        else:
            self.port_up.place(x=340, y=90, height=13, width=25)
            self.port_down.place(x=340, y=102, height=13, width=25)
        self.dir_path.place(x=3, y=47, height=20, width=40)
        self.advanced_btn.place(x=3, y=278, height=20, width=25)
        self.kill_btn.place(geometry(2, 2))
        self.delete_btn.place(geometry(2, 3))
        self.stop_btn.place(geometry(2, 4))
        self.start_btn.place(geometry(2, 5))

        self.run_box.place(x=40, y=190, height=80, width=260)

    def authentication(self):
        def geometry(x, y, height=25, width=110):
            col = (40, 150)
            row = (50, 80, 110, 150)
            return {'x': col[x], 'y': row[y], 'height': height, 'width': width}
        self.login_window.wm_title("PostgreSQL")
        self.login_window.geometry("300x200+%s+%s" % (self.master.winfo_x() + 100, self.master.winfo_y() + 30))
        self.login_window.lift()
        self.master.wm_attributes('-alpha', 0.7)
        self.login_window.grab_set()
        self.login_window.bind("<Control-q>", self.on_exit)
        self.login_window.bind("<FocusOut>", lambda event: self.login_window.lift())
        self.login_window.bind("<Return>", lambda event: login_btn.invoke())
        postgresql_label = tk.Label(self.login_window, text="PostgreSQL", font=font.Font(size=15, weight='bold'), fg=self.white_color, bg=self.primary_color)
        database_label = tk.Label(self.login_window, text="Database")
        username_label = tk.Label(self.login_window, text="Username")
        password_label = tk.Label(self.login_window, text="Password")
        database_box = tk.Entry(self.login_window, textvariable=self.database_str)
        username_box = tk.Entry(self.login_window, textvariable=self.username_str)
        password_box = tk.Entry(self.login_window, textvariable=self.password_str)
        login_btn = tk.Button(self.login_window, text="Login", command=lambda: self.on_login(), relief="raised", **self.style_btn)
        auto_save = tk.Checkbutton(self.login_window, text=" Auto Login", font=font.Font(size=8), variable=self.autosave)
        postgresql_label.place(x=0, y=0, height=40, width=300)
        database_label.place(geometry(0, 0, width=None))
        database_box.place(geometry(1, 0))
        username_label.place(geometry(0, 1, width=None))
        username_box.place(geometry(1, 1))
        password_label.place(geometry(0, 2, width=None))
        password_box.place(geometry(1, 2))
        auto_save.place(geometry(0, 3, width=None))
        login_btn.place(geometry(1, 3))

    def get_path_window(self):
        def geometry(x, y, height=25, width=110):
            col = (40, 300)
            row = (70, 100, 130, 160, 190)
            return {'x': col[x], 'y': row[y], 'height': height, 'width': width}
        self.paths_window.deiconify()
        self.paths_window.wm_title("Server Path")
        self.paths_window.geometry("450x250+%s+%s" % (self.master.winfo_x() + 20, self.master.winfo_y() + 10))
        self.paths_window.lift()
        self.master.wm_attributes('-alpha', 0.7)
        self.paths_window.grab_set()
        self.paths_window.bind("<Control-q>", self.on_exit)
        # self.paths_window.bind("<FocusOut>", lambda event: self.paths_window.lift())
        paths_label = tk.Label(self.paths_window, text="Server Path", font=font.Font(size=12, weight='bold'), fg=self.white_color, bg=self.primary_color)
        server_path_box = tk.Entry(self.paths_window, textvariable=self.server_str)
        community_path_box = tk.Entry(self.paths_window, textvariable=self.community_str)
        enterprise_path_box = tk.Entry(self.paths_window, textvariable=self.enterprise_str)
        python_path_box = tk.Entry(self.paths_window, textvariable=self.python_str)
        terminal_path_box = tk.Entry(self.paths_window, textvariable=self.terminal_str)

        server_btn = tk.Button(self.paths_window, text="odoo-bin", command=lambda: self.on_bin(server_btn), relief="raised", **self.style_btn)
        community_btn = tk.Button(self.paths_window, text="Community", command=lambda: self.on_community(), relief="raised", **self.style_btn)
        enterprise_btn = tk.Button(self.paths_window, text="Enterprise", command=lambda: self.on_enterprise(), relief="raised", **self.style_btn)
        python_btn = tk.Button(self.paths_window, text="Python", command=lambda: self.on_python(), relief="raised", **self.style_btn)
        treminal_btn = tk.Button(self.paths_window, text="Terminal", command=lambda: self.on_terminal(), relief="raised", **self.style_btn)

        if self.get_server_status():
            server_btn.configure(bg=self.primary_color)
            self.dir_path.configure(bg=self.primary_color)
        else:
            server_btn.configure(bg=self.danger_color)
            self.dir_path.configure(bg=self.danger_color)

        paths_label.place(x=0, y=0, height=40, width=450)
        server_path_box.place(geometry(0, 0, width=250))
        community_path_box.place(geometry(0, 1, width=250))
        enterprise_path_box.place(geometry(0, 2, width=250))
        python_path_box.place(geometry(0, 3, width=250))
        terminal_path_box.place(geometry(0, 4, width=250))

        server_btn.place(geometry(1, 0))
        community_btn.place(geometry(1, 1))
        enterprise_btn.place(geometry(1, 2))
        python_btn.place(geometry(1, 3))
        treminal_btn.place(geometry(1, 4))

    @config.save_to_conf
    def on_login(self):
        self.connection_data = {'dbname': self.database_str.get(), 'user': self.username_str.get(), 'password': self.password_str.get(), 'host': self.host_str.get()}
        if self.db_connect():
            self.conn.close()
            self.login_window.grab_release()
            self.login_window.destroy()
            self.master.wm_attributes('-alpha', 1)
            if self.update_db_list() and not self.database_box.get():
                self.database_box.current(0)

    @psql.update_to_database_box
    def on_template_mode(self, event=None):
        if self.template.get():
            self.module_label.configure(text="Database")
            self.database_label.configure(text="Template")
            self.U_I_btn.configure(state="disabled")
            self.delete_db_btn.configure(state="disabled")
            self.module_str.set("")
        else:
            self.module_label.configure(text="Module")
            self.database_label.configure(text="Database")
            self.delete_db_btn.configure(state="normal")
            self.U_I_btn.configure(state="normal")
            self.module_str.set("")

    def on_port_btn(self, key):
        if self.port_box.get() and int(self.port_box.get()) < 65535:
            if key == 'up':
                self.default_port.set(int(self.port_box.get()) + 1)
            elif key == 'down' and int(self.port_box.get()) > 1024:
                self.default_port.set(int(self.port_box.get()) - 1)

    def get_color(self):
        status = self.get_value('port', self.port_box.get(), 'status')
        return self.primary_color if status == 'Running' else self.danger_color if status == 'Stop' else tk.Button().cget("background")

    def on_item_select(self, event):
        if self.data and event.widget.curselection():
            w = event.widget
            index = int(w.curselection()[0]) or 0
            self.port_box.delete('0', 'end')
            self.default_port.set(self.data[index][self.get('port')])
            try:
                database = self.get_value('port', self.port_box.get(), 'database')
                self.database_box.current(self.db_list.index(database))
            except:
                self.update_db_list()
            status = self.get_value('port', self.port_box.get(), 'status')
            self.start_btn.configure(text="Restart" if status == 'Running' else "Start")

    def on_U_I(self, event=None):
        self.U_I_btn.configure(text="I" if self.U_I else "U")
        self.U_I = not self.U_I

    def on_database_select(self):
        pass

    def on_port_key_press(self, event):
        if event.keycode == 111:
            self.port_up.invoke()
        elif event.keycode == 116:
            self.port_down.invoke()
        else:
            if self.port_box.get() in self.get_column('port'):
                status = self.get_value('port', self.port_box.get(), 'status')
                self.start_btn.configure(text="Restart" if status == 'Running' else "Start")
            else:
                self.start_btn.configure(text="Start")

    @psql.update_to_port_box
    def on_portbox_focusout(self, event):
        if not self.port_box.get():
            self.default_port.set(0)
        if not 1024 <= int(self.port_box.get()) <= 65535:
            messagebox.showerror(*hex_['range'])

    @config.save_to_conf
    def set_runbox_port_color(self, port, color):
        index = self.get_value('port', port, 'index')
        if isinstance(index, int):
            list_index = self.get_column('index').index(index)
            self.set_value('port', port, 'status', 'Running' if color == self.primary_color else 'Stop')
            self.run_box.itemconfig(list_index, {'bg': color, 'fg': self.white_color})

    def on_about(self):
        self.master.wm_attributes('-alpha', 0.7)
        about_us = tk.Toplevel(self.master, class_="About")
        about_us.resizable(False, False)
        about_us.title("info")
        about_us.geometry("300x250+%s+%s" % (self.master.winfo_x() + 100, self.master.winfo_y() + 10))
        about_us.protocol("WM_DELETE_WINDOW", lambda: self.on_toplevel_exit(about_us))
        about_us.tk.call('wm', 'iconphoto', about_us._w, self.icon)
        about_label = tk.Label(about_us, text="info", font=font.Font(size=12, weight='bold'), fg=self.white_color, bg=self.primary_color)
        version = tk.Label(about_us, text="Version %s" % self.current_version, fg="blue", font=font.Font(size=7))
        developer = tk.Label(about_us, text=hex_['dev'], cursor="hand2", font=font.Font(size=8))
        developer.bind("<Button-1>", lambda event: self.open_url(self.developer_link))
        msg = tk.Label(about_us, text=hex_['msg'], font=font.Font(size=9))
        short_keys = tk.Label(about_us, text="Shortcut Keys", fg="blue", cursor="hand2", font=font.Font(size=7))
        short_keys.bind("<Button-1>", lambda event: self.open_url(self.shortcutkey_link))
        github = tk.Label(about_us, text="Github", fg="blue", cursor="hand2", font=font.Font(size=7))
        github.bind("<Button-1>", lambda event: self.open_url(self.github_link))
        img_label = tk.Label(about_us, image=self.logo)
        img_label.image = self.logo
        about_label.place(x=0, y=0, height=40, width=300)
        img_label.place(x=0, y=60, height=64, width=300)
        msg.place(x=0, y=130, width=300)

        version.place(x=0, y=180, width=300)
        short_keys.place(x=0, y=200, width=300)
        github.place(x=0, y=160, width=300)
        developer.place(x=0, y=220, width=300)

    def get_command(self, string=False):
        options = {}
        options['terminal'] = self.default_terminal if self.debug.get() and self.os != 'darwin' else ''
        options['path'] = "%python-path% %server-path%" if self.os == 'windows' else self.server_str.get()
        options['addons'] = '--addons-path=%(ent)s,%(community)s' % {'ent': self.enterprise_str.get(), 'community': self.community_str.get()} if self.ent.get() else ''
        options['without_data'] = '' if self.with_data.get() else '--without-demo=WITHOUT_DEMO'
        options['port'] = '--xmlrpc-port=%s' % self.port_box.get() if self.port_box.get() else ''
        options['db'] = '--database=%s' % (self.module_box.get().strip() if self.template.get() else self.database_box.get().strip())
        options['db_filter'] = '--db-filter=%s' % (self.module_box.get().strip() if self.template.get() else self.database_box.get().strip())
        options['module'] = "%s%s" % ('--update=' if self.U_I else '--init=', self.module_box.get()) if self.module_box.get() and not self.template.get() else ''
        options['dev_all'] = '--dev=all'
        options['template'] = '--db-template=%s' % self.database_box.get() if self.template.get() else ''
        options['log'] = '--logfile=LOGFILE' if not self.debug.get() else ''
        terminal = "%(terminal)s||%(path)s||%(addons)s||%(db)s||" \
            "%(db_filter)s||%(dev_all)s||%(without_data)s||" \
            "%(port)s||%(log)s||%(module)s||%(template)s" % options
        try:
            return_ = terminal.replace('||', ' ') if string else [
                x for x in terminal.split('||') if x != '']
        except:
            print(hex_['path_err'])
            self.set_terminal(default=True)
        return return_

    @config.save_to_conf
    def run_server(self, mode="Start"):
        if self.get_server_status():
            self.default_port.set(0) if not self.port_box.get() else None
            if 1024 <= int(self.port_box.get()) <= 65535:
                process = self.run_as_os()
                self.open_profile(process) if self.session.get() and mode == "Start" else None
                self.create_data(process, self.on_delete(replace=True) if mode != "Start" else None)
                self.start_btn.configure(text="Restart")
                self.set_runbox_port_color(self.port_box.get(), self.primary_color)
                print("Database: %s is Running on Port: %s" % (self.database_box.get(), self.port_box.get()))
            else:
                messagebox.showerror(*hex_['range'])
        else:
            messagebox.showerror(*hex_['server_war'])
            self.get_path_window()

    def on_bin(self, widget, path=False, alert=True):
        self.paths_window.grab_release()
        if isinstance(path, bool) and not path:
            path = filedialog.askopenfilename(initialdir='.')
        if self.is_server_path(path):
            widget.configure(bg=self.primary_color)
            self.server_str.set(path)
        else:
            if alert:
                retry = messagebox.askyesno(*hex_['not_bin'])
                self.on_bin(widget) if retry else widget.configure(bg=self.danger_color)
            else:
                widget.configure(bg=self.danger_color)
        self.paths_window.grab_set()

    def on_community(self, path=False, alert=True):
        self.paths_window.grab_release()
        if isinstance(path, bool) and not path:
            path = filedialog.askdirectory(initialdir='.')
        if self.is_path(path):
            directory, bin_ = os.path.split(path)
            self.community_str.set(path)
            if bin_.lower() != 'addons' and alert:
                if messagebox.askyesno(*hex_['addons_war']):
                    self.on_community()
        else:
            self.community_str.set("(optional)")
        self.paths_window.grab_set()

    def on_enterprise(self, path=False):
        self.paths_window.grab_release()
        if isinstance(path, bool) and not path:
            path = filedialog.askdirectory(initialdir='.')
        if self.is_path(path):
            self.enterprise_str.set(path)
        else:
            self.enterprise_str.set("(optional)")
        self.paths_window.grab_set()

    def on_python(self, path=False):
        self.paths_window.grab_release()
        if isinstance(path, bool) and not path:
            path = filedialog.askopenfilename(initialdir='.')
        if self.is_path(path):
            self.python_str.set(path)
        else:
            self.python_str.set("(optional)")
        self.paths_window.grab_set()

    def on_terminal(self, path=False, alert=True):
        self.paths_window.grab_release()
        if isinstance(path, bool) and not path:
            path = filedialog.askopenfilename(initialdir='.')
        if self.is_path(path):
            self.terminal_str.set(path)
            self.default_terminal = path
            if not self.is_terminal(path) and alert:
                if messagebox.askyesno(*hex_['terminal_war']):
                    self.on_terminal()
        else:
            self.set_terminal(default=True)
            self.terminal_str.set("(optional)")
        self.paths_window.grab_set()

    @utils.reset_keys
    @config.save_to_conf
    @psql.update_to_port_box
    @psql.update_to_database_box
    def on_stop(self, port=False, event=None):
        if self.port_box.get() in self.get_column('port') or port:
            port = self.port_box.get()
            process = self.get_value('port', port, 'thread')
            if not isinstance(process, str):
                process.terminate()
            self.kill_pid(self.is_port_running(port, True))
            self.start_btn.configure(text="Start")
            self.set_runbox_port_color(port, self.danger_color)

    @utils.reset_keys
    @config.save_to_conf
    def on_delete(self, replace=False):
        if self.data:
            index = self.get_value('port', self.port_box.get(), 'index')
            if isinstance(index, int):
                list_index = self.get_column('index').index(index)
                self.on_stop()
                self.run_box.delete(list_index)
                if not replace:
                    self.data.pop(list_index)
                    self.index -= 1
                return list_index

    @utils.reset_keys
    @psql.update_to_port_box
    def on_toggle(self, event=None):
        if self.port_box.get() in self.get_column('port'):
            if self.get_value('port', self.port_box.get(), 'status') == 'Running' and \
                    self.get_value('port', self.port_box.get(), 'database') == self.database_box.get():
                self.run_server("Restart")
            else:
                self.set_value('port', self.port_box.get(), 'status', 'Running')
                self.run_server("Restart")
        else:
            self.run_server()

    def on_toplevel_path_exit(self, widget):
        self.master.wm_attributes('-alpha', 1)
        self.master.lift()
        self.on_bin(self.dir_path, path=self.server_str.get())
        self.on_community(path=self.community_str.get(), alert=False)
        self.on_enterprise(path=self.enterprise_str.get())
        self.on_python(path=self.python_str.get())
        self.on_terminal(path=self.terminal_str.get(), alert=False)
        self.ent.set(1 if all([self.is_path(self.enterprise_str.get()), self.is_path(self.enterprise_str.get())]) else 0)
        self.get_server_status()
        widget.grab_release()
        widget.withdraw()

    def on_toplevel_exit(self, widget):
        self.master.wm_attributes('-alpha', 1)
        self.master.lift()
        widget.destroy()
        self.sql = False

    def on_exit(self, event=None):
        parent = self.login_window if self.login_window.winfo_exists() else self.master
        if messagebox.askyesno(*hex_['exit'], parent=parent):
            self.save_config()
            self.master.destroy()
