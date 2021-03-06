"""
Overview of the GUI:
Composed of action buttons:
- Brain: allows a user to load a brain
- Map: allows a user to load a map
- Start/Step/Pause/Reload: control the running of the brain
- Real Robot/Simulator: choose whether to talk to the real robot, or simulate it

The user is required to choose a brain to be able to talk to the real robot.
If the user wishes to simulate a robot, then it needs to choose a map as well.

Actions related to brain/map:
Map button - the GUI showing the map is launched; if a brain is loaded:
- Robot is launched (by default simulator, might launch the real robot if it was
  selected).
- Start/Step/Pause/Reload buttons are enabled.
- Simulator button is enabled
- Real Robot button should already be enabled.
  If no brain is loaded, should not enable any buttons.

Brain button - if no map is loaded, then no file is launched.

These action buttons allow a user to load a map/brain.
Followed by this, the user may talk to the robot
The state variable keeps track of the current state of the simulator, brain, etc.
It is assumed that the simulator never fails. Ditto for the map GUI.
If the real robot communication fails, this failure is ignored
It
"""

from __future__ import absolute_import
import time
from ..main.common import *
from ..brain.templates import *
from ..main import client

PIONEER_PROC = "python -m soar.pioneer.soar"
SIM_PROC = lambda m: "python -m soar.pioneer.simulator -m %s" % m
GUI_PROC = lambda m: "python -m soar.gui.robot -m %s" % m
BRAIN_PROC = lambda f: "python %s" % f

# Topic triggered when brain dies
BRAIN_DEATH = "BRAIN_DEATH"
brain_death_ignore = Event()
brain_open = Event()

try:
    from Tkinter import *
    import tkFileDialog as filedialog
except ImportError:
    from tkinter import *
    from tkinter import filedialog

class SoarUI(Tk):
    def __init__(self,parent):
        global brain_death_ignore
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

        self.start = Button(self,text=u'START',command=self.start_cmd, padx=50, pady=50, state=DISABLED)
        self.pause = Button(self,text=u'PAUSE',command=self.pause_cmd, padx=50, pady=50, state=DISABLED)
        self.step = Button(self,text=u'STEP',command=self.step_cmd, padx=50, pady=50, state=DISABLED)
        self.reload = Button(self,text=u'RELOAD',command=self.reload_cmd, padx=50, pady=50, state=DISABLED)
        self.map_but = Button(self,text=u'MAP',command=self.map_cmd, padx=50, pady=50, state=NORMAL)
        self.brain_but = Button(self,text=u'BRAIN',command=self.brain_cmd, padx=50, pady=50, state=NORMAL)
        self.sim = Button(self,text=u'SIMULATOR',command=self.sim_cmd, padx=50, pady=50, state=DISABLED)
        self.real = Button(self,text=u'REAL ROBOT',command=self.real_cmd, padx=50, pady=50, state=DISABLED)

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

    def reset(self):
        ready_for_action = NORMAL if self.map is not None and self.brain is not None else DISABLED
        self.start.config(state=ready_for_action)
        self.pause.config(state=ready_for_action)
        self.step.config(state=ready_for_action)
        self.reload.config(state=ready_for_action)
        self.sim.config(state=ready_for_action)
        self.real.config(state=ready_for_action)

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
        global brain_death_ignore
        assert self.brain is not None and (self.real_set or self.map is not None)
        # Reload consists of killing the brain, and simulator (or real robot process),
        # followed by opening them up again. We ignore brain death once when doing this.
        #
        if brain_open.is_set():
            brain_death_ignore.set()
        client.message(BRAIN_MSG,CLOSE_MSG)
        client.message(OPEN_MSG,PIONEER_PROC if self.real_set else SIM_PROC(self.map))
        client.message(OPEN_MSG,BRAIN_PROC(self.brain))
        brain_open.set()

    def brain_cmd(self):
        new_brain = filedialog.askopenfilename(**self.file_opt)
        old_brain = self.brain
        if new_brain:
            self.brain = new_brain
        else:
            return
        if self.map is not None:
            self.reload_cmd()
        self.reset()

    def map_cmd(self):
        new_map = filedialog.askopenfilename(**self.file_opt)
        if new_map:
            self.map = new_map
        else:
            return
        client.message(OPEN_MSG,GUI_PROC(self.map))
        # SUCH A HACK
        time.sleep(0.1)

        if self.brain is not None:
            self.reload_cmd()
        self.reset()

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
    brain_open.clear()
    brain_death_ignore.clear()
    def brain_death(_):
        print("BRAIN DEATH", brain_death_ignore.is_set())
        if not brain_death_ignore.is_set():
            brain_open.clear()
            app.brain = None
            app.reset()
        else:
            brain_death_ignore.clear()
    client.subscribe(BRAIN_DEATH,brain_death)
    app.mainloop()
    client.message(CLOSE_MSG)
