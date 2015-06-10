#!/usr/bin/python
from __future__ import absolute_import
try:
    from Tkinter import *
except ImportError:
    from tkinter import *

from soar.main.common import *
from soar.brain.templates import *
import soar.main.client as client
import soar.gui.robot_model as model

from getopt import getopt
import re
import math

floor = lambda *a: int(math.floor(*a))
ceil = lambda *a: int(math.ceil(*a))
sin = math.sin
cos = math.cos
pi = math.pi

def transform(origin,point):
    x,y,theta = origin
    px,py = point
    return (px*cos(theta) - py*sin(theta) + x),(px*sin(theta) + py*cos(theta) + y)

# Based on code from
# http://stackoverflow.com/questions/22835289/how-to-get-tkinter-canvas-to-dynamically-resize-to-window-width

# a subclass of Canvas for dealing with resizing of windows
class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        scale = max(wscale,hscale)
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)

class MapDraw(ResizingCanvas):
    def __init__(self,scale,parent,w,h,initial):
        self.w = w
        self.h = h
        width = parent.winfo_screenwidth()/4. * scale
        self.initial = initial
        self.robot_obj = None
        self.sonar_lines = [None]*N_SONARS
        self.position = None
        self.robot_color = "black"
        ResizingCanvas.__init__(self,parent,width=width,bg="white",highlightthickness=0.)

    def pointToIndices(self,x,y):
        nx = x*self.width/self.w
        ny = self.height * (1-y/self.h)
        return (nx,ny)

    def wall(self,x1,y1,x2,y2):
        x1,y1 = self.pointToIndices(x1,y1)
        x2,y2 = self.pointToIndices(x2,y2)
        self.create_line(x1,y1,x2,y2,fill="black",width=3)

    def robot(self,x,y,theta):
        ix,iy,itheta = self.initial
        x,y = transform((ix,iy,itheta),(x,y))
        self.position = (x,y,itheta+theta)
        pos = (x,y,itheta+theta-math.pi/2.)
        coords = (transform(pos,point) for point in model.points)
        coords = [i for p in coords for i in self.pointToIndices(*p)]
        if self.robot_obj is not None:
            self.coords(self.robot_obj,*coords)
            self.itemconfig(self.robot_obj, fill=self.robot_color)
        else:
            self.robot_obj = self.create_polygon(coords,width=1,fill=self.robot_color)

    def sonars(self,sonars):
        if self.position is None:
            return
        px,py,ptheta = self.position
        for (i,r) in sonars.items():
            x,y,theta = model.sonar_poses[i]
            if r is None:
                r = 0.
            sonar_x,sonar_y = transform((px,py,ptheta),(x,y))
            beam = transform((sonar_x,sonar_y,ptheta+theta),(r/1000.,0))
            beam_x,beam_y = self.pointToIndices(*beam)
            pixel_px,pixel_py = self.pointToIndices(sonar_x,sonar_y)
            if self.sonar_lines[i] is not None:
                self.coords(self.sonar_lines[i],pixel_px,pixel_py,beam_x,beam_y)
            else:
                self.sonar_lines[i] = self.create_line(pixel_px,pixel_py,beam_x,beam_y,width=2,fill="black")

    def collision(self, colliding):
        self.robot_color = "red" if colliding else "black"

def parse_map(map_file):
    number = "(?:\d+(?:\.(?:\d+)?)?)"

    dim_regex = "dimensions\s*\(\s*(%s)\s*,\s*(%s)\s*\)" % ((number,)*2)
    wall_regex = "wall\s*\(\s*(\(\s*%s\s*,\s*%s\s*\))\s*,\s*(\s*\(\s*%s\s*,\s*%s\s*\)\s*)\)" % ((number,)*4)
    initial_loc_regex = "initialRobotLoc\s*\(\s*(%s)\s*,\s*(%s)\s*\)" % ((number,)*2)
    initial_loc_theta_regex = "initialRobotLoc\s*\(\s*(%s)\s*,\s*(%s)\s*,(.*)\)" % ((number,)*2)

    dim_pattern = re.compile(dim_regex)
    wall_pattern = re.compile(wall_regex)
    initial_loc_pattern = re.compile(initial_loc_regex)
    initial_loc_theta_pattern = re.compile(initial_loc_theta_regex)

    walls = []
    initial_loc = None
    dims = None
    with open(map_file,'r') as m:
        for line in m:
            dim_match = dim_pattern.search(line)
            wall_match = wall_pattern.search(line)
            initial_loc_match = initial_loc_pattern.search(line)
            initial_loc_theta_match = initial_loc_theta_pattern.search(line)

            if dim_match is not None:
                dims = (eval(dim_match.group(1)),eval(dim_match.group(2)))
            if wall_match is not None:
                p1 = eval(wall_match.group(1))
                p2 = eval(wall_match.group(2))
                walls.append(p1+p2)
            if initial_loc_match is not None:
                initial_loc = ((eval(initial_loc_match.group(1)),\
                                eval(initial_loc_match.group(2)),\
                                0.))
            if initial_loc_theta_match is not None:
                initial_loc = ((eval(initial_loc_theta_match.group(1)),\
                                eval(initial_loc_theta_match.group(2)),\
                                eval(initial_loc_theta_match.group(3))))
    return dims,walls,initial_loc

def main(argv):
    scale = 1.0
    map_file = None
    port = 0
    opts,args = getopt(argv[1:],'s:m:p:',["scale=","map=","port="])
    for opt,arg in opts:
        if opt in ("-s","--scale"):
            scale = eval(arg)
        if opt in ("-m","--map"):
            map_file = arg
        if opt in ("-p","--port"):
            port = eval(arg)

    # Aspect ratio/dimensions
    w,h = 7.,7.
    initial_loc = w/2.,h/2.,0.
    walls = []
    if map_file is not None:
        (w,h),walls,initial_loc = parse_map(map_file)

    root = Tk()
    root.aspect(floor(w),ceil(h),ceil(w),floor(h))

    main_frame = Frame(root)
    main_frame.pack(fill=BOTH, expand=YES)
    map_canvas = MapDraw(scale,main_frame,w,h,initial_loc)
    map_canvas.pack(fill=BOTH, expand=YES)

    # Create map/robot/...
    for wall in walls:
        map_canvas.wall(*wall)

    # tag all of the drawn widgets
    map_canvas.addtag_all("all")
    root.title("SOAR Robot Display")

    # All is taken care of on the display side from here on
    # Let's now take care of updates
    #
    client.subscribe(POSITION_TOPIC(port),lambda p: map_canvas.robot(*p))
    client.subscribe(SONARS_TOPIC(port),map_canvas.sonars)
    client.subscribe(COLLIDES_TOPIC(port),map_canvas.collision)
    root.mainloop()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
