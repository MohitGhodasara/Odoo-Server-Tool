import os
import psutil
import subprocess
from .config_manager import config


class control(config):

    def get_running_pid(self):
        ls = []
        "python.exe" if self.os == "windows" else "python3"
        if self.os == 'linux':
            process_name = 'python3'
        elif self.os == 'windows':
            process_name = 'python.exe'
        elif self.os == 'darwin':
            process_name = 'python'
        else:
            pass
        for p in psutil.process_iter():
            try:
                all_process = p.name()
            except (psutil.AccessDenied, psutil.ZombieProcess):
                pass
            except psutil.NoSuchProcess:
                continue
            if all_process.lower() == process_name:
                ls.append(p.pid)
        return ls

    def is_port_running(self, port, kill=False):
        status = False
        for p in psutil.process_iter():
            try:
                for conns in p.connections(kind='inet'):
                    if conns.laddr[1] == int(port):
                        status = p.pid
            except:
                pass
        return status

    @config.save_to_conf
    def on_terminate(self, event=None):
        self.run_box.delete(0, "end")
        self.data = []
        self.index = 0
        pids = self.get_running_pid()
        for pid in pids:
            if pid != os.getpid():
                try:
                    self.kill_pid(pid)
                except:
                    pass

    def kill_pid(self, pid):
        try:
            if pid:
                # os.kill(int(pid), signal.SIGTERM)
                psutil.Process(pid).terminate()
        except (psutil.AccessDenied, psutil.ZombieProcess):
            pass

    def open_url(self, url):
        chrome = "start chrome" if self.os == "windows" else "google-chrome"
        os.system('%s %s' % (chrome, url))

    def is_path(self, string):
        return False if str(string).lower() in ['false', '/', '(optional)', 'none', '()', ' ', ''] else True

    def is_terminal(self, terminal):
        return True if subprocess.call(['which', terminal], stdout=subprocess.PIPE) == 0 else False

    def is_server_path(self, path):
        if self.is_path(path):
            directory, bin_ = os.path.split(path)
            if bin_.lower() == 'odoo-bin':
                self.dir_path.configure(bg=self.primary_color)
                return_ = True
            else:
                self.dir_path.configure(bg=self.danger_color)
                return_ = False
        else:
            self.dir_path.configure(bg=self.danger_color)
            return_ = False
        return return_

    def run_as_windows(self):
        env = os.environ.copy()
        if self.is_path(self.server_str.get()):
            env["server-path"] = '"%s"' % self.server_str.get()
        if self.is_path(self.python_str.get()):
            env["python-path"] = '"%s"' % self.python_str.get()
        if self.is_path(self.community_str.get()):
            env["addons-path"] = '"%s"' % self.community_str.get()
        if self.is_path(self.enterprise_str.get()):
            env["ent-addons-path"] = '"%s"' % self.enterprise_str.get()
        return subprocess.Popen(self.get_command(), shell=True, env=env)

    def run_as_linux(self):
        return subprocess.Popen(self.get_command())

    def run_as_darwin(self):
        if self.debug.get():
            os.system('echo "%s ; rm -- \$0" > darwin ; chmod +x darwin ;' % self.get_command(string=True))
            _execute = "%s darwin" % self.default_terminal.replace("||", " ")
            return_ = subprocess.Popen(_execute.split())
        else:
            return_ = subprocess.Popen(self.get_command())
        return return_

    def run_as_os(self):
        if self.os == 'linux':
            return_ = self.run_as_linux()
        elif self.os == 'windows':
            return_ = self.run_as_windows()
        elif self.os == 'darwin':
            return_ = self.run_as_darwin()
        else:
            return_ = self.run_as_linux()
        return return_

    def open_profile(self, process):
        chrome = "start chrome" if self.os == "windows" else "google-chrome"
        params = (chrome, self.port_box.get(), "Profile %s" % self.index if self.index else 'Default')
        command = '%s http://localhost:%s --profile-directory="%s"' % params
        os.system(command)
