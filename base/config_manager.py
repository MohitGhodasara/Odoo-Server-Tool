import configparser
import json
from .baseutils import utils
from .slash_x import hex_


class config():

    def save_to_conf(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            args[0].save_config()
            return result
        return wrapper

    def save_config(self):
        def set_default(obj):
            return list(obj) if isinstance(obj, set) else 'Object'
        config = configparser.ConfigParser(allow_no_value=True)
        config["default"] = {}
        config["list"] = {}
        config["postgresql"] = {}
        config["default"]['server'] = self.server_str.get()
        config["default"]['community'] = self.community_str.get()
        config["default"]['enterprise'] = self.enterprise_str.get()
        config["default"]['python'] = self.python_str.get()
        config["default"]['terminal'] = self.terminal_str.get()

        config["default"]['geometry'] = str(self.master.winfo_geometry()) if self.advanced_mode.get() else self.geometry
        config["default"]['command'] = "%s # %s terminal options" % (self.remove_separator(self.terminal_option), hex_['hint'] if self.os == 'linux' else self.os)
        config["default"]['database'] = str(self.database_box.get())
        config["default"]['os'] = str(self.os)
        config['default']['debug'] = str(self.debug.get())
        config['default']['with_data'] = str(self.with_data.get())
        config['default']['ent'] = str(self.ent.get())
        config['default']['session'] = str(self.session.get())
        config['default']['autologin'] = str(self.autosave.get())
        config["list"]["index"] = str(list(self.get_column('index')))
        config["list"]["port"] = str(list(self.get_column('port')))
        config["list"]["database"] = str(list(self.get_column('database')))
        config["postgresql"]["host"] = str(self.host_str.get())
        config["postgresql"]["database"] = str(self.database_str.get())
        config["postgresql"]["username"] = str(self.username_str.get())
        if self.autosave.get() and self.sql:
            config["postgresql"]["password"] = str(self.password_str.get())
        with open('server.conf', 'w') as configfile:
            config.write(configfile)

    def load_config(self):
        def get_or_null(option, key):
            try:
                str_ = config.get(option, key)
                if "#" in str_:
                    return str_[:str_.index("#")].strip()
                return str_
            except:
                return ""
        config = configparser.ConfigParser()
        try:
            config.read('server.conf')
            if config.has_section('default'):
                self.server_str.set(get_or_null('default', 'server'))
                self.dir_path.configure(bg=self.primary_color if self.is_server_path(self.server_str.get()) else self.danger_color)
                community = get_or_null('default', 'community')
                enterprise = get_or_null('default', 'enterprise')
                python = get_or_null('default', 'python')
                terminal = get_or_null('default', 'terminal')
                self.community_str.set(community if self.is_path(community) else '(optional)')
                self.enterprise_str.set(enterprise if self.is_path(enterprise) else '(optional)')
                self.python_str.set(python if self.is_path(python) else '(optional)')
                self.terminal_str.set(python if self.is_path(terminal) else '(optional)')

                self.database_box.set(config.get('default', 'database'))
                self.debug.set(config.get('default', 'debug'))
                if config.get('default', 'ent') and self.check_path(alert=False):
                    self.ent.set(1)
                self.with_data.set(config.get('default', 'with_data'))
                self.session.set(config.get('default', 'session'))
                if config.get('default', 'geometry') == "1x1+0+0":
                    self.geometry = "490x300"
                else:
                    self.geometry = config.get('default', 'geometry')
                self.master.geometry(self.geometry)
                if get_or_null('default', 'command'):
                    self.terminal_option = self.add_separator(get_or_null('default', 'command'))
                if config.has_section('list'):
                    index = json.loads(config.get('list', 'index'))
                    port = json.loads(config.get('list', 'port').replace("'", '"'))
                    database = json.loads(config.get('list', 'database').replace("'", '"'))
                    for inx, prt, db in zip(index, port, database):
                        self.create_data([inx, db, prt])
                        self.run_box.itemconfig(inx, {'bg': self.danger_color, 'fg': self.white_color})
                        self.index += 1
            if config.has_section('postgresql'):
                self.host_str.set(config.get("postgresql", "host"))
                self.database_str.set(config.get("postgresql", "database"))
                self.username_str.set(config.get("postgresql", "username"))
                self.password_str.set(get_or_null("postgresql", "password"))
                self.autosave.set(config.getint('default', 'autologin'))
                self.on_login() if self.autosave.get() else self.authentication()
            else:
                self.dir_path.configure(bg=self.danger_color)
                utils.messagebox.showinfo(*hex_['conf_war'])
                self.authentication()
        except:
            utils.messagebox.showinfo(*hex_['conf_err'])
            self.get_path_window()
