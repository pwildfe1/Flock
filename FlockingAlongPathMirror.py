import rhinoscriptsyntax as rs
import math as m
import random as r

class myBoid:
    def __init__(self,pos,vec,range,boids,CURVE):
        self.pos = pos
        self.vec = vec
        self.pt = rs.AddPoint(pos)
        self.range = range
        self.flock = boids
        self.guide = CURVE
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
        self.pt = rs.MoveObject(self.pt,self.vec)
        self.pos = rs.PointAdd(self.pos,self.vec)
        #if self.pos!=start:
        #    trace = rs.AddLine(start,self.pos)
        return self.pos
    def mirror(self):
        param = rs.CurveClosestPoint(self.guide,self.pos)
        tan = rs.CurveTangent(self.guide,param)
        crvPt = rs.EvaluateCurve(self.guide,param)
        vector = rs.VectorCreate(self.pos,crvPt)
        axis = rs.VectorCrossProduct(tan,vector)
        mirorVec = rs.VectorRotate(vector,180,axis)
        mirrorStart = rs.PointAdd(self.pos,mirorVec*2)
        vec = rs.VectorRotate(self.vec,180,axis)
        vec = rs.VectorUnitize(vec)*self.range
        mirrorPos = rs.PointAdd(mirrorStart,vec)
        if mirrorStart!=mirrorPos:
            mirrorTrace = rs.AddLine(mirrorStart,mirrorPos)
        return mirrorPos

class myFlock:
    def __init__(self,positions,vectors,THRES,FACTOR,CURVE):
        self.boids = []
        self.range = THRES
        self.factor = FACTOR
        self.guide = CURVE
        for i in range(len(positions)):
            self.boids.append(myBoid(positions[i],vectors[i],self.range,positions,self.guide))
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
    def cohesion(self):
        center = self.getCnt()
        param = rs.CurveClosestPoint(self.guide,center)
        center = rs.EvaluateCurve(self.guide,param)
        for i in range(len(self.boids)):
            avg = rs.VectorCreate(center,self.boids[i].pos)*self.factor
            self.boids[i].vec = rs.PointAdd(self.boids[i].vec,avg)
        return rs.CurveNormalizedParameter(self.guide,param)

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
    radius = rs.GetReal("please enter radius of starting",6)
    positions = []
    crvPts = []
    curves = []
    pos=[]
    vec=[]
    num=5
    time=50
    progress = 0
    norm = rs.CurveTangent(guide,rs.CurveClosestPoint(guide,rs.CurveStartPoint(guide)))
    plane = rs.PlaneFromNormal(rs.CurveStartPoint(guide),norm)
    circle = rs.AddCircle(plane,6)
    startPos = rs.DivideCurve(circle,num)
    for i in range(num):
        position = startPos[i]
        pos.append(position)
        param = rs.CurveParameter(guide,0)
        vec.append(rs.CurveTangent(guide,param))
        crvPts.append([position])
    flock = myFlock(pos,vec,thres,factor,guide)
    for i in range(time):
        if(progress!=1):
            for j in range(len(flock.boids)):
                positions.append(flock.boids[j].trace())
            for j in range(len(positions)):
                crvPts[j].append(positions[j])
            positions = []
            flock.separate()
            flock.align()
            progress = flock.cohesion()
    for i in range(len(crvPts)):
        curves.append(rs.AddCurve(crvPts[i],1))

Main()