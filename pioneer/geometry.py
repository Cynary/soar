from math import sqrt

PRECISION = 1e-5

class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def distance(self,p2):
        if isinstance(p2,Point):
            return abs(self-p2)
        elif isinstance(p2,Segment):
            return p2.distance(self)
        else:
            print("Can only calculate distance to Points, and Segments")
            return NotImplemented

    # Returns a perpendicular vector
    def perpendicular(self):
        return Point(-self.y,self.x)

    def __add__(self,p2):
        if not isinstance(p2,Point):
            print("Can only add two points")
            return NotImplemented
        return Point(self.x+p2.x,self.y+p2.y)
    __radd__ = __add__
    def __sub__(self,p2):
        if not isinstance(p2,Point):
            print("Can only subtract two points")
            return NotImplemented
        return Point(self.x-p2.x,self.y-p2.y)
    def __rsub__(self,p2):
        if not isinstance(p2,Point):
            print("Can only subtract two points")
            return NotImplemented
        return Point(p2.x-self.x,p2.y-self.y)
    def __mul__(self,p2):
        if isinstance(p2,Point): # Dot product
            return self.x*p2.x + self.y*p2.y
        elif isinstance(p2,(int,float)):
            return Point(self.x*p2,self.y*p2)
        else:
            print("Can only multiply a point by a number, or dot it with another point")
            return NotImplemented
    __rmul__ = __mul__
    def __div__(self,c):
        if not isinstance(c,(int,float)):
            print("Can only divide by numbers")
            return NotImplemented
        return Point(self.x/c,self.y/c)
    __truediv__ = __div__
    def __floordiv__(self,c):
        if not isinstance(c,(int,float)):
            print("Can only divide by numbers")
            return NotImplemented
        return Point(self.x//c,self.y//c)
    def __neg__(self):
        return Point(-self.x,-self.y)
    def __pos__(self):
        return Point(self.x,self.y)
    def __abs__(self):
        return sqrt(self.x**2 + self.y**2)

    def __str__(self):
        return "(%f,%f)" % (self.x,self.y)
    def __repr__(self):
        return "Point(%f,%f)" % (self.x,self.y)

    def __eq__(self,other):
        return isinstance(other,Point) and \
            abs(other.x-self.x) <= PRECISION and \
            abs(other.y-self.y) <= PRECISION
    def __ne__(self,other):
        return not (self==other)

# From http://www.toptal.com/python/computational-geometry-in-python-from-theory-to-implementation
def ccw(a,b,c):
    """Tests whether the turn formed by A, B, and C is ccw"""
    return (b.x-a.x)*(c.y-a.y) > (b.y-a.y)*(c.x-a.x)

class Segment:
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2

    def distance(self,p,segment=True):
        if not isinstance(p,Point,segment=True):
            print("Can only calculate distance to Points")
            return NotImplemented
        # Return minimum distance between line segment, and point p
        v = self.p2-self.p1; # Segment vector
        l2 = v*v
        if l2 == 0: # Segment is one point
            return p.distance(self.p1)

        # Consider the line extending the segment, parameterized as v + t (w - v).
        # We find projection of point p onto the line.
        # It falls where t = [(p-v) . (w-v)] / |w-v|^2
        t = (p-self.p1)*(self.p2-self.p1)/l2;
        if segment:
            if (t < 0.0):
                return self.p1.distance(p); # Beyond the 'v' end of the segment
            elif (t > 1.0):
                return self.p2.distance(p); # Beyond the 'w' end of the segment
        projection = self.p1 + v*t; # Projection falls on the segment
        return projection.distance(p);

    def intersects(self,other):
        if not isinstance(other,Segment):
            print("Can only calculate intersection with other segments")
            return NotImplemented
        a1,b1 = self.p1,self.p2
        a2,b2 = other.p1,other.p2
        return \
            ccw(a1,b1,a2) != ccw(a1,b1,b2) and ccw(a2,b2,a1) != ccw(a2,b2,b1)

    def on_segment(self,p):
        if not isinstance(p,Point):
            print("Can only check if a point is in a segment")
            return NotImplemented
        perp = (self.p1-self.p2).perpendicular()
        p1,p2 = p+PRECISION*perp,p-PRECISION*perp
        return self.intersects(Segment(p1,p2))

    def intersection_point(self,other):
        if not isinstance(other,Segment):
            print("Can only calculate intersection with other segments")
            return NotImplemented
        if not self.intersects(other):
            return None

        x1 = self.p1.x;
        y1 = self.p1.y;
        x2 = self.p2.x;
        y2 = self.p2.y;

        xx1 = other.p1.x;
        yy1 = other.p1.y;
        xx2 = other.p2.x;
        yy2 = other.p2.y;

        top = (yy1-y1)*(x2-x1) - (xx1-x1)*(y2-y1);
        bottom = (xx2-xx1)*(y2-y1) - (yy2-yy1)*(x2-x1);
        alpha_2 = float(top)/bottom;

        if (abs(bottom) < PRECISION):
            return other.p1 if self.on_segment(other.p1) else other.p2;

        return other.p2 * alpha_2 + other.p1 * (1-alpha_2);

    def __abs__(self):
        return abs(self.p1-self.p2)
    def __str__(self):
        return "%s -> %s" % (self.p1,self.p2)
    def __repr__(self):
        return "Segment(%s,%s)" % (repr(self.p1),repr(self.p2))
