# !/usr/bin/env python3
# coding: utf-8

from base import *
import frame


if __name__ == "__main__":
    try:
        root = tk.Tk(className='Server')
        root_server = frame.server(root)
        if root_server.version_bool:
            root_server.pack(fill="both", expand=True)
            root.mainloop()
        else:
            root.update_idletasks()
            messagebox.showerror(*slash_x.hex_['ver_err'])
            root.destroy()
    except BaseException as e:
        print("Error: ", e)
