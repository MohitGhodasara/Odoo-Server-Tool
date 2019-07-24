import sys

from . import baseutils
from . import config_manager
from . import version_manager
from . import psql_database
from . import slash_x


if sys.version_info[0] >= 3:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter import font
    from tkinter import messagebox
    from tkinter import filedialog
else:
    import Tkinter as tk
    import tkFont as font
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    import ttk
