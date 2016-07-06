import rhinoscriptsyntax as rs
import math as m
import random as r

class myBoid:
    def __init__(self,pos,vec,range,boids):
        self.pos = pos
        self.vec = vec
        self.pt = rs.AddPoint(pos)
        self.range = range
        self.flock = boids
    def findClosest(self):
        indexes = []
        for i in range(len(self.flock)):
            dist=rs.Distance(self.flock[i],self.pos)
            if dist<self.range and dist>0:
                indexes.append(i)
        return indexes
    def trace(self):
        start = self.pos
        dir=[1,0,0]
        self.vec=rs.VectorUnitize(self.vec)*self.range
        self.vec=rs.PointAdd(self.vec,dir)
        self.pt = rs.MoveObject(self.pt,self.vec)
        self.pos = rs.PointAdd(self.pos,self.vec)
        if self.pos!=start:
            trace = rs.AddLine(start,self.pos)
        return self.pos

class myFlock:
    def __init__(self,positions,vectors):
        self.boids = []
        self.range = 5
        self.factor = .15
        for i in range(len(positions)):
            self.boids.append(myBoid(positions[i],vectors[i],self.range,positions))
    def separate(self):
        sum=[0,0,0]
        for i in range(len(self.boids)):
            index=self.boids[i].findClosest()
            for j in range(len(index)):
                factor=(1-rs.Distance(self.boids[index[j]].pos,self.boids[i].pos)/self.range)
                closeVec=rs.VectorCreate(self.boids[index[j]].pos,self.boids[i].pos)
                sum = rs.PointAdd(sum,closeVec*factor)
            if len(index)>0:
                avg = sum/len(index)
                self.boids[i].vec = rs.PointAdd(self.boids[i].vec,-avg)
    def align(self):
        sum=[0,0,0]
        for i in range(len(self.boids)):
            index=self.boids[i].findClosest()
            for j in range(len(index)):
                factor=(1-rs.Distance(self.boids[index[j]].pos,self.boids[i].pos)/self.range)
                sum = rs.PointAdd(sum,self.boids[index[j]].vec*factor)
            if len(index)>0:
                avg = sum/len(index)
                self.boids[i].vec = rs.PointAdd(self.boids[i].vec,avg)
    def cohesion(self):
        sum=[0,0,0]
        for i in range(len(self.boids)):
            sum = rs.PointAdd(sum,self.boids[i].pos)
        center = sum/len(self.boids)
        for i in range(len(self.boids)):
            avg = rs.VectorCreate(center,self.boids[i].pos)*self.factor
            self.boids[i].vec = rs.PointAdd(self.boids[i].vec,avg)

def genRandom(x,y,z):
    x=r.random()*x
    y=r.random()*y
    z=r.random()*z
    return rs.PointAdd([0,0,0],[x,y,z])

def Main():
    num=10
    time=20
    pos=[]
    vec=[]
    for i in range(int(num/2)):
        position = genRandom(10,10,10)
        vector = genRandom(1,1,1)
        pos.append(position)
        pos.append([-position[0],-position[1],position[2]])
        vec.append(vector)
        vec.append(vector)
    flock = myFlock(pos,vec)
    for i in range(time):
        for j in range(len(flock.boids)):
            position=flock.boids[j].trace()
        flock.separate()
        flock.align()
        flock.cohesion()

Main()