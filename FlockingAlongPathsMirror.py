import rhinoscriptsyntax as rs
import math as m
import random as r

class myBoid:
    def __init__(self,pos,vec,range,boids,CURVES):
        self.pos = pos
        self.vec = vec
        self.pt = rs.AddPoint(pos)
        self.range = range
        self.flock = boids
        self.guides = CURVES
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
        return self.pos
    def getCrv(self):
        crv = rs.PointClosestObject(self.pos,self.guides)[0]
        return crv
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
    def __init__(self,positions,vectors,THRES,FACTOR,CURVES):
        self.boids = []
        self.range = THRES
        self.factor = FACTOR
        self.guides = CURVES
        for i in range(len(positions)):
            self.boids.append(myBoid(positions[i],vectors[i],self.range,positions,self.guides))
    def separate(self):
        for i in range(len(self.boids)):
            sum=[0,0,0]
            index=self.boids[i].findClosest()
            for j in range(len(index)):
                factor=(1-rs.Distance(self.boids[index[j]].pos,self.boids[i].pos)/self.range)
                closeVec=rs.VectorCreate(self.boids[index[j]].pos,self.boids[i].pos)
                sum = rs.PointAdd(sum,closeVec*factor)
            if len(index)>0:
                avg = sum/len(index)
                self.boids[i].vec = rs.PointAdd(self.boids[i].vec,-avg)
    def align(self):
        for i in range(len(self.boids)):
            sum=[0,0,0]
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
    def getSets(self):
        indexes = []
        sets = []
        for i in range(len(self.boids)):
            min = 100000000
            for j in range(len(self.guides)):
                param = rs.CurveClosestPoint(self.guides[j],self.boids[i].pos)
                close = rs.EvaluateCurve(self.guides[j],param)
                dist = rs.Distance(self.boids[i].pos,close)
                if dist<min:
                    min = dist
                    index = j
            indexes.append(index)
        for i in range(len(self.guides)):
            set = []
            for j in range(len(self.boids)):
                if indexes[j]==i:
                    set.append(j)
            sets.append(set)
        print sets
        return sets
    def cohesion(self):
        sets = self.getSets()
        maxParam = 0
        removals = []
        newBoids = []
        for i in range(len(sets)):
            posSet = []
            if len(sets[i])!=0:
                for j in range(len(sets[i])):
                    posSet.append(self.boids[sets[i][j]].pos)
                center=centerPt(posSet)
                param = rs.CurveClosestPoint(self.guides[i],center)
                center = rs.EvaluateCurve(self.guides[i],param)
                for j in range(len(sets[i])):
                    avg = rs.VectorCreate(center,self.boids[sets[i][j]].pos)*self.factor
                    self.boids[sets[i][j]].vec = rs.PointAdd(self.boids[sets[i][j]].vec,avg)
                if param>.95:
                    removals.append(sets[i][j])
                if param>max:
                    maxParam = param
                    maxLine = self.guides[i]
        return rs.CurveNormalizedParameter(maxLine,maxParam)

def centerPt(points):
    sum = [0,0,0]
    for i in range(len(points)):
        sum = rs.PointAdd(sum,points[i])
    center = sum/len(points)
    return center

def Main():
    guides = rs.GetObjects("please select guide curve",rs.filter.curve)
    thres = rs.GetReal("please enter range of boid",15)
    factor = rs.GetReal("please enter factor of cohesion",.5)
    radius = rs.GetReal("please enter radius of starting",20)
    positions = []
    crvPts = []
    startPos = []
    pos=[]
    vec=[]
    curves = []
    num=5
    time=100
    progress = 0
    for i in range(len(guides)):
        norm = rs.CurveTangent(guides[i],rs.CurveClosestPoint(guides[i],rs.CurveStartPoint(guides[i])))
        plane = rs.PlaneFromNormal(rs.CurveStartPoint(guides[i]),norm)
        circle = rs.AddCircle(plane,radius)
        #rect = rs.AddRectangle(plane,radius,radius)
        #rect = rs.MoveObject(rect,[-radius/2,0,-radius/2])
        startPos.extend(rs.DivideCurve(circle,num))
    for i in range(len(startPos)):
        position = startPos[i]
        pos.append(position)
        min = 1000000
        for j in range(len(guides)):
            param = rs.CurveClosestPoint(guides[j],position)
            close = rs.EvaluateCurve(guides[j],param)
            dist = rs.Distance(close,position)
            if dist<min:
                index = j
        crv = guides[index]
        param = rs.CurveParameter(crv,0)
        vec.append(rs.CurveTangent(crv,param))
        crvPts.append([position])
    flock = myFlock(pos,vec,thres,factor,guides)
    for i in range(time):
        if progress<.95:
            for j in range(len(flock.boids)):
                positions.append(flock.boids[j].trace())
            for j in range(len(positions)):
                crvPts[j].append(positions[j])
            positions = []
            flock.separate()
            flock.align()
            progress = flock.cohesion()
    for i in range(len(crvPts)):
        curves.append(rs.AddCurve(crvPts[i],3))

Main()