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
    def __init__(self,positions,vectors,THRES,FACTOR):
        self.boids = []
        self.range = THRES
        self.factor = FACTOR
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
    def getCnt(self):
        sum=[0,0,0]
        for i in range(len(self.boids)):
            sum = rs.PointAdd(sum,self.boids[i].pos)
        center = sum/len(self.boids)
        return center
    def cohesion(self,guideCrv):
        center = self.getCnt()
        param = rs.CurveClosestPoint(guideCrv,center)
        center = rs.EvaluateCurve(guideCrv,param)
        for i in range(len(self.boids)):
            avg = rs.VectorCreate(center,self.boids[i].pos)*self.factor
            self.boids[i].vec = rs.PointAdd(self.boids[i].vec,avg)
    def bias(self,guideCrv,factor):
        center = self.getCnt()
        param = rs.CurveClosestPoint(guideCrv,center)
        tan = rs.CurveTangent(guideCrv,param)
        for i in range(len(self.boids)):
            param = rs.CurveClosestPoint(guideCrv,self.boids[i].pos)
            pt = rs.EvaluateCurve(guideCrv,param)
            vector = rs.VectorCreate(pt,self.boids[i].pos)
            self.boids[i].vec = rs.PointAdd(self.boids[i].vec,vector*factor)
            #self.boids[i].vec = rs.PointAdd(self.boids[i].vec,vector*factor)

def genRandomSign():
    sign = 1
    factor = r.random()
    if factor>.5:
        sign = -sign
    return sign

def genRandom(x,y,z):
    x=r.random()*x*genRandomSign()
    y=r.random()*y*genRandomSign()
    z=r.random()*z*genRandomSign()
    return rs.PointAdd([0,0,0],[x,y,z])

def Main():
    guide = rs.GetObject("please select guide curve",rs.filter.curve)
    thres = rs.GetReal("please enter range of boid",10)
    factor = rs.GetReal("please enter factor of cohesion",.5)
    bias = rs.GetReal("please enter factor of bias",.05)
    num=30
    time=20
    pos=[]
    vec=[]
    for i in range(30):
        pos.append(rs.PointAdd(rs.CurveStartPoint(guide),genRandom(10,10,10)))
        param = rs.CurveParameter(guide,0)
        vec.append(rs.CurveTangent(guide,param))
    flock = myFlock(pos,vec,thres,factor)
    for i in range(time):
        for j in range(len(flock.boids)):
            position=flock.boids[j].trace()
        flock.separate()
        flock.align()
        flock.cohesion(guide)
        #flock.bias(guide,bias)

Main()