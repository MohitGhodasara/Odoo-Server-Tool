import datetime as dt
import requests
from .slash_x import hex_
from .baseutils import utils


class version():
    def version_control(self):
        self.connection = True
        self.current_version = 1.1
        self.developer_link = hex_['dev_link']
        self.shortcutkey_link = hex_['shortcut']
        self.github_link = hex_['git']
        self.download_link = hex_['down']
        return_ = dt.datetime.now() < dt.datetime.combine(dt.datetime(2020, 1, 1), dt.time(0, 0))
        data = {}
        try:
            data = requests.get(*hex_['vurl']).json().get('OdooServerTool')
            self.developer_link = data.get('stackoverflow_link')
            self.download_link = data.get('download_link')
            self.shortcutkey_link = data.get('shortcutkey_link')
            self.github_link = data.get('github_link')
            if data.get('version') > self.current_version:
                if utils.messagebox.askyesno(hex_['update_war'][0], hex_['update_war'][1] % ("version", self.current_version)):
                    self.open_url(self.download_link)
            if data.get('min_version') > self.current_version:
                return False
            if not data.get('published'):
                return False
            return return_
        except:
            self.connection = False
            return return_
