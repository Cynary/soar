from __future__ import absolute_import
from ..main.common import *
from ..brain.templates import *
import soar.main.client as client

PIONEER_PROC = "python -m soar.pioneer.soar"
SIM_PROC = lambda m: "python -m soar.pioneer.simulator -m %s" % m
GUI_PROC = lambda m: "python -m soar.gui.robot -m %s" % m
BRAIN_PROC = lambda f: "python %s" % f

try:
    from Tkinter import *
    import tkFileDialog as filedialog
except ImportError:
    from tkinter import *
    from tkinter import filedialog

class SoarUI(Tk):
    def __init__(self,parent):
        Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
        self.real_set = False
        self.brain = None
        self.map = None
        self.file_opt = {
            'defaultextension': '.py',
            'filetypes': [('all files','.*'),('python files','.py')],
            'parent': parent,
            'title': "Find your file",
        }

    def initialize(self):
        self.grid()

        self.start = Button(self,text=u'START',command=self.start_cmd)
        self.pause = Button(self,text=u'PAUSE',command=self.pause_cmd)
        self.step = Button(self,text=u'STEP',command=self.step_cmd)
        self.reload = Button(self,text=u'RELOAD',command=self.reload_cmd)
        self.map_but = Button(self,text=u'MAP',command=self.map_cmd)
        self.brain_but = Button(self,text=u'BRAIN',command=self.brain_cmd)
        self.sim = Button(self,text=u'SIMULATOR',command=self.sim_cmd)
        self.real = Button(self,text=u'REAL ROBOT',command=self.real_cmd)

        self.start.grid(column = 0, row = 0, sticky='EW')
        self.pause.grid(column = 1, row = 0, sticky='EW')
        self.step.grid(column = 2, row = 0, sticky='EW')
        self.reload.grid(column = 3, row = 0, sticky='EW')
        self.brain_but.grid(column = 4, row = 0, sticky='EW')
        self.map_but.grid(column = 5, row = 0, sticky='EW')
        self.sim.grid(column = 6, row = 0, sticky='EW')
        self.real.grid(column = 7, row = 0, sticky='EW')

        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)

    def start_cmd(self):
        assert self.brain is not None and (self.real_set or self.map is not None)
        client.message(BRAIN_MSG,CONTINUE_MSG)

    def pause_cmd(self):
        assert self.brain is not None and (self.real_set or self.map is not None)
        client.message(BRAIN_MSG,PAUSE_MSG)

    def step_cmd(self):
        assert self.brain is not None and not self.real_set and self.map is not None
        client.message(BRAIN_MSG,STEP_MSG)

    def reload_cmd(self):
        assert self.brain is not None and (self.real_set or self.map is not None)
        client.message(BRAIN_MSG,CLOSE_MSG)
        client.message(OPEN_MSG,PIONEER_PROC if self.real_set else SIM_PROC(self.map))
        client.message(OPEN_MSG,BRAIN_PROC(self.brain))

    def brain_cmd(self):
        new_brain = filedialog.askopenfilename(**self.file_opt)
        if new_brain != '':
            self.brain = new_brain
        client.message(BRAIN_MSG,CLOSE_MSG)
        client.message(OPEN_MSG,BRAIN_PROC(self.brain))

    def map_cmd(self):
        self.map = filedialog.askopenfilename(**self.file_opt)
        client.message(OPEN_MSG,GUI_PROC(self.map))

    def sim_cmd(self):
        assert self.map is not None
        self.real_set = False
        self.pause_cmd()
        client.message(SIM_MSG,CLOSE_MSG)
        client.message(OPEN_MSG,SIM_PROC(self.map))

    def real_cmd(self):
        self.real_set = True
        self.pause_cmd()
        client.message(SIM_MSG,CLOSE_MSG)
        client.message(OPEN_MSG,PIONEER_PROC)

if __name__ == "__main__":
    app = SoarUI(None)
    app.title("Snakes On A Robot")
    app.mainloop()
    client.message(CLOSE_MSG)
