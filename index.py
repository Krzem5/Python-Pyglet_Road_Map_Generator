from pyglet.gl import *;from pyglet.window import key;from math import sin, cos, pi, sqrt;from pyglet.font import load as load_font;import pyglet.font



class Road:
    def __init__(self,x,z,x2,z2,tm,cl):self.batch=pyglet.graphics.Batch();self.batch.add(2,GL_LINES,None,('v3i',(x,1,z,x2,1,z2)),('c3B',self.rd_color(round(sqrt((x2-x)**2+(z2-z)**2)*100)/100,tm,cl)))
    def draw(self):self.batch.draw()
    def rd_color(self,d,tm,cl):
        speed=int(d/tm*60//10*10) if int(d/tm*60//10*10)!=0 else 10
        speed=speed if int(str(speed)[:-1])%2==1 else (int(str(speed)[:-1])+1)*10
        c_={10:(130,0,0),30:(230,0,0),50:(230,70,0),70:(230,120,0),90:(230,180,0),110:(170,230,0),130:(110,230,0),150:(0,230,100),170:(0,230,170)}
        c=c_[speed] if speed in list(c_.keys()) else (100,255,210)
        c=c if cl else (0,230,0)
        return c*2
class Point:
    def __init__(self,x,z):self.batch=pyglet.graphics.Batch();self.batch.add(4,GL_QUADS,None,('v3f',(x-0.125,1.001,z+0.125,x+0.125,1.001,z+0.125,x+0.125,1.001,z-0.125,x-0.125,1.001,z-0.125)),('c3B',(330,330,330)*4));self.batch.add(4,GL_QUADS,None,('v3f',(x-0.125,1,z+0.125,x+0.125,1,z+0.125,x+0.125,1,z-0.125,x-0.125,1,z-0.125)),('c3B',(330,330,330)*4));self.batch.add(4,GL_QUADS,None,('v3f',(x-0.125,0.999,z+0.125,x+0.125,0.999,z+0.125,x+0.125,0.999,z-0.125,x-0.125,0.999,z-0.125)),('c3B',(330,330,330)*4))
    def draw(self):self.batch.draw()
class Marker:
    def __init__(self):self.on=False
    def on_(self,x,z):self.on,self.batch=True,pyglet.graphics.Batch();self.batch.add(4,GL_QUADS,None,('v3f',(x-0.125,1.002,z+0.125,x+0.125,1.002,z+0.125,x+0.125,1.002,z-0.125,x-0.125,1.002,z-0.125)),('c3B',(177,177,177)*4))
    def off(self):self.on=False
    def draw(self):self.batch.draw()
class Camera:
    def __init__(self,pos=(0,0,0),rot=(0,0)):self.pos,self.rot=list(pos),list(rot)
    def mouse_motion(self,dx,dy):
        dx/=8;dy/=8
        self.rot[0]+=dy
        self.rot[1]-=dx
        if self.rot[0]>90:self.rot[0]=90
        if self.rot[0]<-90:self.rot[0]=-90
    def update(self,dt,keys):
        dx,dz=dt*5*sin(-self.rot[1]/180*pi),dt*5*cos(-self.rot[1]/180*pi)
        if keys[key.W]:self.pos=[self.pos[0]+dx,self.pos[1],self.pos[2]-dz]
        if keys[key.S]:self.pos=[self.pos[0]-dx,self.pos[1],self.pos[2]+dz]
        if keys[key.A]:self.pos=[self.pos[0]-dz,self.pos[1],self.pos[2]-dx]
        if keys[key.D]:self.pos=[self.pos[0]+dz,self.pos[1],self.pos[2]+dx]
        if keys[key.SPACE]:self.pos=[self.pos[0],self.pos[1]+dt*5,self.pos[2]]
        if keys[key.LSHIFT]:self.pos=[self.pos[0],self.pos[1]-dt*5,self.pos[2]]
class Roads(pyglet.window.Window):
    '''===Program Keys===
W,A,S,D - movement
SPACE,LEFT SHIFT - up/down
MOUSE MOVEMENT - look around
ESC - quit
P - toggle mouse pointer
C - toggle road colors
Q - select point
E - remove last seleced point from the list
TAB - remove/add road
R - change the travel time of the selected road
T - toggle road info
I - show this list'''
    def __init__(self,fn,*args,**kwargs):
        self.fn=fn if fn.endswith('.rd') else fn+'.rd'
        super().__init__(width=1920,height=1080,caption=f'Roads - {self.fn}',resizable=False,fullscreen=True)
        glClearColor(0,0,0,0)
        glEnable(GL_DEPTH_TEST)
        self.set_minimum_size(1920,1080)
        self.points,self.mouse,self.colors,self.drawing,self.marker,self.marker2,self.all_points,self.fps_,self.rd_info_=[],True,False,[],Marker(),Marker(),[],False,True
        f=open(self.fn,'r')
        self.roads={((int(li.replace('\n','').replace(' ','').split(':')[0].split(';')[0].split(',')[0]),int(li.replace('\n','').replace(' ','').split(':')[0].split(';')[0].split(',')[1])),(int(li.replace('\n','').replace(' ','').split(':')[0].split(';')[1].split(',')[0]),int(li.replace('\n','').replace(' ','').split(':')[0].split(';')[1].split(',')[1]))):float(li.replace('\n','').replace(' ','').split(':')[1]) for li in f if li.replace('\n','').replace(' ','')!=''}
        f.close()
        [[self.all_points.append((x,z)),self.all_points.append((x2,z2))] for ((x,z),(x2,z2)) in list(self.roads.keys())]
        [self.points.append((x,z)) for ((x,z),(_,_)) in list(self.roads.keys()) if (x,z) not in self.points]
        [self.points.append((x,z)) for ((_,_),(x,z)) in list(self.roads.keys()) if (x,z) not in self.points]
        self.show_colors()
        self.cam=Camera((list(self.roads.keys())[0][0][0],3,list(self.roads.keys())[0][0][1]),(-45,180)) if len(list(self.roads.keys()))>0 else Camera((0,3,0),(-45,180))
        self.rd_info=pyglet.font.Text(load_font('',15,bold=True),' -',color=(0.4,0.4,0.4,0.4),x=10,y=1050)
        self.keys=key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)
        self.fps=pyglet.clock.ClockDisplay()
        pyglet.app.run()
    def on_mouse_motion(self,x,y,dx,dy):self.cam.mouse_motion(dx,dy)
    def on_key_press(self,KEY,MOD):
        self.drawing.reverse();reverse_drawing=list(self.drawing.copy());self.drawing.reverse();del_rd=False
        if KEY==key.ESCAPE:self.close()
        if KEY==key.P:self.mouse=not self.mouse
        if KEY==key.I:print(self.__doc__)
        if KEY==key.C:self.show_colors()
        if KEY==key.F:self.fps_=not self.fps_
        if KEY==key.T:self.rd_info_=not self.rd_info_
        if (round(self.cam.pos[0]),round(self.cam.pos[2])) not in self.drawing and len(self.drawing)<2 and KEY==key.Q:self.drawing.append((round(self.cam.pos[0]),round(self.cam.pos[2])))
        if len(self.drawing)==2 and tuple(self.drawing) in list(self.roads.keys()) and KEY==key.R:self.change_road_time(self.drawing)
        if len(self.drawing)==2 and tuple(reverse_drawing) in list(self.roads.keys()) and KEY==key.R:self.change_road_time(reverse_drawing)
        if len(self.drawing)==2 and tuple(self.drawing) in list(self.roads.keys()) and KEY==key.TAB:self.del_road(self.drawing);del_rd=True
        if len(self.drawing)==2 and tuple(reverse_drawing) in list(self.roads.keys()) and KEY==key.TAB:self.del_road(reverse_drawing);del_rd=True
        if len(self.drawing)==2 and tuple(self.drawing) not in list(self.roads.keys()) and KEY==key.TAB and not del_rd:self.add_road(self.drawing)
        if len(self.drawing)==2 and tuple(reverse_drawing) not in list(self.roads.keys()) and KEY==key.TAB and not del_rd:self.add_road(reverse_drawing)
        if len(self.drawing)>0 and KEY==key.E:self.drawing.reverse();self.drawing.remove(self.drawing[0])
        self.marker.on_(*self.drawing[0]) if len(self.drawing)>0 else self.marker.off()
        self.marker2.on_(*self.drawing[1]) if len(self.drawing)>1 else self.marker2.off()
    def update(self,dt):self.cam.update(dt,self.keys)
    def add_road(self,d):
        f=open(self.fn,'a')
        tm=float(self.input_('Road travel time (in minutes)?\t'))
        f.write(f'{d[0][0]},{d[0][1]};{d[1][0]},{d[1][1]}:{tm}\n')
        f.close()
        self.all_points.append(d[0])
        self.all_points.append(d[1])
        self.roads[tuple(d)]=tm
        if d[0] not in self.points:[self.points.append(d[0]),self.models.append(Point(*d[0]))]
        if d[1] not in self.points:[self.points.append(d[1]),self.models.append(Point(*d[1]))]
        self.models.append(Road(*d[0],*d[1],tm,self.colors))
        self.marker.off()
    def del_road(self,d):
        self.roads.pop(tuple(d))
        f=open(self.fn,'r')
        f_=[li for li in f]
        f.close()
        f=open(self.fn,'w')
        [f.write(li) for li in f_ if not li.startswith(f'{d[0][0]},{d[0][1]};{d[1][0]},{d[1][1]}:')]
        f.close()
        self.all_points.remove(d[0])
        self.all_points.remove(d[1])
        if self.all_points.count(d[0])<1:self.points.remove(d[0])
        if self.all_points.count(d[1])<1:self.points.remove(d[1])
        self.models=[Road(x,z,x2,z2,tm,self.colors) for (((x,z),(x2,z2)),tm) in list(self.roads.items())]+[Point(x,z) for (x,z) in self.points]
        self.drawing=[]
    def change_road_time(self,d):
        tm=float(self.input_(f'New road travel time (the current travel time is {self.roads[tuple(d)]} min)?\t'))
        self.roads[tuple(d)]=tm
        f=open(self.fn,'r')
        f_=[li for li in f]
        f.close()
        f=open(self.fn,'w')
        [f.write(li if not li.startswith(f'{d[0][0]},{d[0][1]};{d[1][0]},{d[1][1]}:') else f'{d[0][0]},{d[0][1]};{d[1][0]},{d[1][1]}:{tm}\n') for li in f_]
        f.close()
        self.models=[Road(x,z,x2,z2,tm,self.colors) for (((x,z),(x2,z2)),tm) in list(self.roads.items())]+[Point(x,z) for (x,z) in self.points]
    def show_colors(self):
        self.colors=not self.colors
        self.models=[Road(x,z,x2,z2,tm,self.colors) for (((x,z),(x2,z2)),tm) in list(self.roads.items())]+[Point(x,z) for (x,z) in self.points]
    def road_info(self):
        self.drawing.reverse();reverse_drawing=list(self.drawing.copy());self.drawing.reverse()
        if tuple(self.drawing) in list(self.roads.keys()):d=self.drawing
        elif tuple(reverse_drawing) in list(self.roads.keys()):d=reverse_drawing
        else:d=[]
        if len(d)==2:
            dis=round(sqrt((d[1][0]-d[0][0])**2+(d[1][1]-d[0][1])**2)*100)/100
            speed=int(dis/self.roads[tuple(d)]*60//10*10) if int(dis/self.roads[tuple(d)]*60//10*10)!=0 else 10
            speed=speed if int(str(speed)[:-1])%2==1 else (int(str(speed)[:-1])+1)*10
            return f'distance - {dis} km\ntravel time - {self.roads[tuple(d)]} min\nspeed - {speed} km/h'
        else:return ' -'
    def input_(self,q):return input(q)
    def on_draw(self):
        self.clear()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70,self.width/self.height,0.05,1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glPushMatrix()
        glRotatef(-self.cam.rot[0],1,0,0)
        glRotatef(-self.cam.rot[1],0,1,0)
        glTranslatef(-self.cam.pos[0],-self.cam.pos[1],-self.cam.pos[2])
        [mdl.draw() for mdl in self.models]
        self.marker.draw() if self.marker.on else 0;self.marker2.draw() if self.marker2.on else 0
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0,self.width,0,self.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        if self.fps_:self.fps.draw()
        if self.rd_info_:self.rd_info.text=self.road_info();self.rd_info.draw()
        self.set_exclusive_mouse(1) if self.mouse else self.set_exclusive_mouse(0)
if __name__=='__main__':Roads('roads')
