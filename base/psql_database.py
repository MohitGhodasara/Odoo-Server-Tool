import psycopg2
from .baseutils import utils
from .config_manager import config
from .slash_x import hex_
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class psql(config, utils):

    def update_to_port_box(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            args[0].update_port_list()
            return result
        return wrapper

    def update_to_database_box(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            args[0].update_db_list()
            return result
        return wrapper

    @config.save_to_conf
    def on_delete_db(self):
        if self.db_list:
            if utils.messagebox.askyesno(hex_['del_war'][0], hex_['del_war'][1] % self.database_box.get()):
                if not self.database_box.get() in self.get_column('database'):
                    query = 'DROP DATABASE IF EXISTS "%s"' % self.database_box.get()
                    self.execute_sql(query)
                    self.update_db_list()
                    self.database_box.current(0)
                else:
                    print(hex_['stucked'])
                    utils.messagebox.showerror(*hex_['stucked_war'])

    def db_connect(self):
        if self.connection_data:
            try:
                self.conn = psycopg2.connect(**self.connection_data)
                self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                self.cr = self.conn.cursor()
                self.sql = True
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                parent = self.login_window if self.login_window.winfo_exists() else self.master
                utils.messagebox.showerror("Error", error, parent=parent)
                self.sql = False
                self.authentication()
        return self.sql

    def get_db_list(self):
        return self.execute_sql(hex_['query'])

    def execute_sql(self, query):
        try:
            if self.db_connect() and self.sql:
                self.cr.execute(query)
            else:
                return []
        except psycopg2.DatabaseError as error:
            print(error)
        results = self.cr.fetchall() if self.cr.rowcount > 0 else []
        self.conn.close()
        return results

    def update_db_list(self, event=None):
        self.db_list = [name[0] for name in self.get_db_list()]
        self.database_box.configure(values=self.db_list)
        return True if len(self.db_list) > 0 else False
