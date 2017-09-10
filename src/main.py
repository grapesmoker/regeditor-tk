import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import Tkinter as tk
from ui.app import EditorApp

if __name__ == '__main__':

    root = tk.Tk()
    root.title('eRegs notice editor')
    root.geometry("1280x1024+300+300")
    app = EditorApp(root)
    root.mainloop()