from cmu_graphics import *
import math
import random
import time

#CONSTANTS
kAppWidth, kAppHeight = 1600, 1000
kAppInitPauseState = False

kSpeedResistance = 0.1     # resistance to speed based on current speed - PERCENTAGE
kPitchResistance = 0.1     # resistance to speed based on current pitch - PERCENTAGE
kRollFactor      = 0.05    # roll increase based on current roll - PERCENTAGE 
kRollFactorReduction = 1/5 # roll increase reduction based on current roll - RATIO
kleftSpeedFactor = 5.0     # side speed increase factor based on current roll - PERCENTAGE
kGravity = -.4              # downward acceleration due to gravity - UNITS / STEP / STEP

kMaxPlayerAcceleration = 10
kMaxPlayerSpeed = 50

kRollControlMultiplier = 1 / 10
kAimControlMultiplier = 1 / 4

kStepsPerSecond = 30 
kMotionStepsPerSecond = 5
kMotionTimeFactor = kMotionStepsPerSecond / kStepsPerSecond

kTrailLength = 5
kTrailOpacity = 40
kTrailWidth = 3
kDiscBorderWidth = 4
kFrisbeeSize = 30
kFrisbeeColor = 'lightBlue'
kTrailColor = kFrisbeeColor
kShadowColor = 'black'
kDiscGradient = gradient(*[kFrisbeeColor]*4, 'skyBlue', 'steelBlue', start='center')

kGrassLight, kGrassMedium, kGrassDark = rgb(20, 150, 50), rgb(30, 125, 30), rgb(20, 100, 10)

kBackgroundGradient0 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='left')
kBackgroundGradient1 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='center')
kBackgroundGradient2 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//200), start='top')
kBackgroundGradient3 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//150), start='left-top')
kBackgroundGradient4 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//300), start='right-top')

kTeamColors = ['black', 'white']

floorTexture = './CMU Classes/15112/FrisbeeFlight_15112_TP/Images/Grass.png'
 
class Vector2():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def unitVector(self):
        mag = self.magnitude()
        if mag == 0: return Vector2(0,0)
        return Vector2(self.x / mag, self.y / mag)
        
    def magnitude(self):
        return (self.x**2+self.y**2)**.5

    def __eq__(self, other):
        if isinstance(other, Vector2):
            return self.x == other.x and self.y == other.y
        return False
        
    def __repr__(self):
        return(f'Vector2({int(self.x)},{int(self.y)})')
    
    def __hash__(self):
        return hash(str(self))
    
    def multiplyBy(self, other):
        if isinstance(other, int):
            self.x *= other*abs(self.unitVector().x)
            self.y *= other*abs(self.unitVector().y)
        elif isinstance(other, Vector2):
            self.x *= other.x
            self.y *= other.y
        else:
            print(f'ERROR: Cannot multiply Vector2 by {type(other)}')

    def multipliedBy(self, other):
        if isinstance(other, int) or isinstance(other, float):
            x = self.x * other*abs(self.unitVector().x)
            y = self.y * other*abs(self.unitVector().y)
        elif isinstance(other, Vector2):
            x = self.x * other.x
            y = self.y * other.y
        else:
            print(f'ERROR: Cannot multiply Vector2 by {type(other)}')
        return Vector2(x,y)

    def tup(self):
        return (self.x, self.y)

    def add(self, other):
        if isinstance(other, int):
            self.x += other *abs(self.unitVector().x)
            self.y += other *abs(self.unitVector().y)
        elif isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
        else:
            print(f'ERROR: Cannot add {type(other)} to Vector2')
    
    def added(self, other):
        if isinstance(other, int):
            x = self.x + other * self.unitVector().x
            y = self.y + other * self.unitVector().y
        elif isinstance(other, Vector2):
            x = self.x + other.x
            y = self.y + other.y
        else:
            print(f'ERROR: Cannot add {type(other)} to Vector2')
        return Vector2(x, y)
    
    def subtract(self, other):
        if isinstance(other, int):
            self.x -= other *self.unitVector().x
            self.y -= other *self.unitVector().y
        elif isinstance(other, Vector2):
            self.x -= other.x
            self.y -= other.y
        else:
            print(f'ERROR: Cannot subtract {type(other)} from Vector2')
    
    def subtracted(self, other):
        if isinstance(other, int):
            x = self.x - other * self.unitVector().x
            y = self.y - other * self.unitVector().y
        elif isinstance(other, Vector2):
            x = self.x - other.x
            y = self.y - other.y
        else:
            print(f'ERROR: Cannot subtract {type(other)} from Vector2')
        return Vector2(x, y)

    def dotProduct(self, other):
        if isinstance(other, Vector2):
            return self.x * other.x + self.y * other.y
        return None
    
    def clamped(self, value):
        if isinstance(value, int):
            value = abs(value)
            unitVector = self.unitVector()
            xFactor, yFactor = abs(unitVector.x), abs(unitVector.y)
            x = min(max(self.x, -value*xFactor), value*xFactor) 
            y = min(max(self.y, -value*yFactor), value*yFactor) 
            return Vector2(x, y)
        return Vector2(0,0)

class Vector3():
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
    
    def __eq__(self, other):
        if isinstance(other, Vector3):
            return self.x==other.x and self.y==other.y and self.z==other.z
        return False

    def __repr__(self):
        return(f'Vector3({int(self.x)},{int(self.y)}, {int(self.z)})')
    
    def __hash__(self):
        return hash(str(self))

    def unitVector(self):
        mag = self.magnitude()
        if mag == 0: return Vector3(0,0,0)
        return Vector3(self.x / mag, self.y / mag, self.z / mag)

    def dotProduct(self, other):
        if isinstance(other, Vector3):
            return self.x * other.x + self.y * other.y + self.z*other.z
        return None
    
    def crossProduct(self, other):
        if isinstance(other, Vector3):
            i =   self.y*other.z - self.z*other.y
            j = -(self.x*other.z - self.z*other.x)
            k =   self.x*other.y - self.y*other.x
            return Vector3(i, j, k)

    def magnitude(self):
        return (self.x**2+self.y**2+self.z**2)**.5
    
class Player():
    def __init__(self, vec2, number, team, isDefending, hasFrisbee):
        self.pos = vec2
        self.goalPos = vec2
        self.velocity = Vector2(0,0)
        self.goalVelocity = Vector2(0,0)
        self.number = number
        self.team = team
        self.defending = isDefending
        self.hasFrisbee = hasFrisbee

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.number == other.number and self.team == other.team
        return False
    
    def turnover(self):
        self.defending = not self.defending

    def accelerate(self):
        if self.velocity != self.goalVelocity:
            differenceVelocity = self.goalVelocity.subtracted(self.velocity)
            clampedDifferenceVelocity = differenceVelocity.clamped(kMaxPlayerAcceleration)
            self.velocity.add(clampedDifferenceVelocity)

    def move(self):
        self.pos.add(self.velocity.multipliedBy(kMotionTimeFactor))

    def takeMotionStep(self):
        self.goalVelocity = self.calculateGoalVelocity()
        self.accelerate()
        self.move()

    def calculateGoalVelocity(self):
        goalVelocity = self.goalPos.subtracted(self.pos).clamped(kMaxPlayerSpeed)
        return goalVelocity


class Frisbee():
    def __init__(self, pos, direction, forwardSpeed, upSpeed, pitch, roll,):
        self.direction = direction.unitVector() # 2D UNIT VECTOR
        self.leftDirection = getLeftVector(direction)
        self.forwardSpeed = forwardSpeed # UNITS/STEP
        self.leftSpeed = 0.0 # UNITS/STEP
        self.downSpeed = upSpeed # UNITS/STEP
        self.pitch = pitch # DEGREES
        self.roll = roll # DEGREES
        self.trail = []
        self.inFlight = True
        self.x = pos[0]
        self.y = pos[1]
        self.z = pos[2]

    def stop(self):
        self.z = 0
        self.roll = 0
        self.pitch = 0
        self.forwardSpeed = 0
        self.leftSpeed = 0
        self.inFlight = False

    def updatePosition(self): # convert speeds from vector direction to 
        xSpeed, ySpeed = self.getConvertedSpeeds()
        self.x += xSpeed *  kMotionTimeFactor
        self.y += ySpeed *  kMotionTimeFactor
        self.z += self.downSpeed *  kMotionTimeFactor

    def getConvertedSpeeds(self):
        xMagnitude = self.direction.x * self.forwardSpeed + self.leftDirection.x * self.leftSpeed
        yMagnitude = self.direction.y * self.forwardSpeed + self.leftDirection.y * self.leftSpeed
        return xMagnitude, yMagnitude

    def getForwardResistance(self):
        # Some base loss of speed by default plus resistance if the frisbee is showing face
        return self.forwardSpeed * kSpeedResistance - self.pitch * kPitchResistance

    def getLeftRollAndSpeed(self):
        # If the frisbee has any roll, it will increase over time, especially at lower speeds, the more roll the more speed it will gain sideways
        # Frisbee side speed increase will be maximum at -45 degrees, no side speed increase at 0 and -90 (achieved with the sine of twice the angle)
        if abs(self.roll) <= 45:
            roll = self.roll * (1 + (kRollFactor * kMotionTimeFactor))
        else:
            roll = (kRollFactor*kRollFactorReduction*kMotionTimeFactor + 1) * self.roll
        
        # absolute value to first find the magnitude of the leftward speed
        leftSpeedIncrease = kleftSpeedFactor * math.sin(math.radians(abs(self.roll) * 2))
        leftSpeed = self.leftSpeed + math.copysign(leftSpeedIncrease, self.roll) * kMotionTimeFactor #apply roll direction to leftward speed (negative is rightward speed)
        return roll, leftSpeed
    
    def getDownSpeedChange(self):
        return kGravity - 3*abs(math.cos(math.radians(self.roll))) - max(self.forwardSpeed*(-self.pitch/50), -kGravity)

    def takeFlightStep(self):
        # print(f'Taking Flight Step...', end='')
        # startTime = time.time()
        if self.inFlight:
            self.updatePosition()
            if self.z <= 0:
                self.stop()
            else:
                self.downSpeed += self.getDownSpeedChange() *  kMotionTimeFactor
                self.roll, self.leftSpeed = self.getLeftRollAndSpeed()
                self.forwardSpeed -= self.getForwardResistance() *  kMotionTimeFactor
            self.trail.append((self.x, self.y))
        if (len(self.trail) > (kTrailLength * (kStepsPerSecond / 20)) or not self.inFlight) and self.trail != []:
            self.trail.pop(0)
        # endTime = time.time()
        # print(f'Done: Time= {endTime-startTime}s')

    def getLabel(self):
        return f'z={int(self.z)}|Roll={int(self.roll)}|leftSpeed={int(self.leftSpeed)}|leftDirection={self.leftDirection}'

def makeRandomFrisbee(app, x, y):
    app.frisbees.append(Frisbee((x, y, 5), (random.randint(-10, 10), random.randint(-10, 10)), random.randint(30, 100), random.randint(5, 15), random.randint(-10, 10), random.randint(-30,30)))

def getLeftVector(vector):
    return Vector2(-vector.y, vector.x)

def getAngle(vector):
    if vector.x == 0:
        return 90
    if vector.y == 0:
        return 0
    return math.degrees(math.atan(vector.y / vector.x)) # vector angle in radians

def getDistance(vector0, vector1):
    return ((vector0.x-vector1.x)**2 + (vector0.y - vector1.y)**2)**.5

def onAppStart(app):
    app.width, app.height = kAppWidth, kAppHeight
    app.frisbees = []
    app.teams = [[],[]]
    app.paused = kAppInitPauseState
    app.stepsPerSecond = kStepsPerSecond
    app.drawLabels = False
    app.frisbeeInitPoint = (kFrisbeeSize*2, app.height/2)
    app.upSpeed = 5
    app.initPitch = 10
    app.mousePos = None
    app.throwing = True
    app.goalPos = Vector2(app.width - kFrisbeeSize*2, app.height/2)
    app.settingPitch = False
    app.currTeamIndex = 0
    app.throwPoint = None
    app.curvePoint = None

def onStep(app):
    if not app.paused:
        takeStep(app)

def takeStep(app):
    for frisbee in app.frisbees:
        frisbee.takeFlightStep()
    for team in app.teams:
        for player in team:
            player.takeMotionStep()

def onKeyPress(app, key):
    match key:
        case 's':
            takeStep(app)
        case 'r':
            app.frisbees = []
            app.teams = [[],[]]
        case 'space':
            app.paused = not app.paused
        case 'l':
            app.drawLabels = not app.drawLabels
        case 'n':
            app.frisbees.append(Frisbee((200,200,0), Vector2(1,1), 50, 15, 20, 45))
        case 'p':
            app.settingPitch = not app.settingPitch
        case 't':
            app.currTeamIndex = (app.currTeamIndex + 1) % len(kTeamColors)
        case 'f':
            app.throwing = not app.throwing
        case 'g':
            spawnPlayerOnMouse(app)
        case 'up':
            if app.settingPitch: app.initPitch += 5
            else: app.upSpeed += 1
        case 'down':
            if app.settingPitch: app.initPitch -= 5
            else: app.upSpeed -= 1
        case 'escape':
            app.quit()

def onMousePress(app, mouseX, mouseY):
    if app.throwing:
        app.throwPoint = (mouseX, mouseY)
    else:
        app.goalPos = Vector2(mouseX, mouseY)
        if app.teams[app.currTeamIndex] != []:
            playerNumber = getClosestOffensivePlayer(app)
            app.teams[app.currTeamIndex][playerNumber-1].goalPos = app.goalPos

def onMouseMove(app, mouseX, mouseY):
    app.mousePos = Vector2(mouseX, mouseY)

def getClosestOffensivePlayer(app):
    if app.teams[app.currTeamIndex] == []:
        return None
    closestPlayer = None
    closestDistance = None
    for player in app.teams[app.currTeamIndex]:
        dis = player.pos.subtracted(app.goalPos).magnitude()
        if closestDistance == None or dis < closestDistance:
            closestDistance = dis
            closestPlayer = player.number
    return closestPlayer

def spawnPlayerOnMouse(app):
    if app.mousePos:
        app.teams[app.currTeamIndex].append(Player(Vector2(*app.mousePos.tup()), len(app.teams[app.currTeamIndex])+1, app.currTeamIndex, bool(app.currTeamIndex%2), False))

def formVertStack(app):
    formationGoalPositions = [] #TODO
    pass

def formOffense(app, style):
    match style:
        case 'vert':
            formVertStack(app)

def onMouseDrag(app, mouseX, mouseY):
    app.curvePoint = (mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    if app.throwing:
        aimVector = Vector2(app.throwPoint[0]-app.frisbeeInitPoint[0], app.throwPoint[1]-app.frisbeeInitPoint[1])
        rollVector = Vector2(app.throwPoint[0]-mouseX, app.throwPoint[1]-mouseY)
        rollDirection = rollVector.dotProduct(getLeftVector(aimVector))
        roll = -kRollControlMultiplier * math.copysign(rollVector.magnitude(), rollDirection)
        newFrisbee = Frisbee((*app.frisbeeInitPoint, 5), aimVector.unitVector(), aimVector.magnitude() * kAimControlMultiplier, app.upSpeed, app.initPitch, roll)
        app.frisbees.append(newFrisbee)
        app.throwPoint = None
        app.curvePoint = None

def drawFrisbeeTopDown(app, frisbee):
    # print(f'Drawing Frisbee...', end='')
    # startTime = time.time()
    sizeMultiplier = max(1, (frisbee.z/40 + 1))
    width = max(kFrisbeeSize * math.cos(math.radians(frisbee.pitch)), 1)
    height = max(kFrisbeeSize * math.cos(math.radians(frisbee.roll)), 1)
    rotAngle = getAngle(frisbee.direction)

    ## FRISBEE TRAIL ##
    drawTrail(frisbee, height)
    
    ## SHADOW ##
    drawOval(frisbee.x + frisbee.z, frisbee.y + frisbee.z, width, height, fill=kShadowColor, rotateAngle=rotAngle, opacity=50)
    
    ## FRISBEE
    #adding gradient color to imitate shadow as the disc adjusts angles
    if abs(frisbee.roll) > 5: fill = gradient('lightCyan', *[kFrisbeeColor]*int(60//abs(frisbee.roll)), 'skyBlue', 'steelBlue', start=('top' if frisbee.roll>0 else 'bottom'))
    else: fill = kDiscGradient
    drawOval(frisbee.x, frisbee.y, width * sizeMultiplier, height * sizeMultiplier, fill=fill, rotateAngle=rotAngle, borderWidth=kDiscBorderWidth, border=kDiscGradient)
    
    ## LABEL ##
    if app.drawLabels:
        drawLine(frisbee.x, frisbee.y, frisbee.x + 100*frisbee.direction.x, frisbee.y + 100*frisbee.direction.y, arrowEnd=True,fill='red', opacity=30)
        drawLine(frisbee.x, frisbee.y, frisbee.x + 100*frisbee.leftDirection.x, frisbee.y + 100*frisbee.leftDirection.y, arrowEnd=True,fill='lime', opacity=30)
        drawLabel(frisbee.getLabel(), frisbee.x, frisbee.y+20) # draws frisbee label if labels are on
    # endTime = time.time()
    # print(f'Done: Time= {endTime-startTime}s')

def drawTrail(frisbee, frisbeeWidth):
    # print(f'Drawing Trail...', end='')
    # startTime = time.time()
    if len(frisbee.trail) >= 2:
        prevPoint = frisbee.trail[0]
        for i in range(len(frisbee.trail)-1):
            currPoint = frisbee.trail[i+1]
            width = kTrailWidth*(i+1)*((frisbee.z+1) / 30) * (frisbeeWidth / kFrisbeeSize)
            drawLine(*prevPoint, *currPoint, lineWidth=width, fill=kTrailColor, opacity=kTrailOpacity, dashes=True)
            prevPoint = frisbee.trail[i+1]
    # endTime = time.time()
    # print(f'Done: Time= {endTime-startTime}s')

def drawPlayer(app, player):
    drawRect(player.pos.x, player.pos.y, 20, 30, fill=kTeamColors[player.team], align='center')
    drawLabel(str(player.number), player.pos.x, player.pos.y, fill=kTeamColors[(player.team+1)%2], size=16)
    if app.drawLabels:
        drawLine(*player.pos.tup(), *player.goalPos.tup(), arrowEnd=True, lineWidth=5, opacity=5, fill='cyan')
        drawLine(*player.pos.tup(), *player.pos.added(player.velocity).tup(), arrowEnd=True, lineWidth=3, opacity=30, fill='cyan')

def drawBackground(app):
    # print(f'Drawing Background...', end='')
    # startTime = time.time()
    drawRect(0,0, app.width, app.height, fill=kBackgroundGradient0)
    # drawRect(0,0, app.width, app.height, fill=kBackgroundGradient1, opacity=10)
    now = time.time()
    offset = 40
    width = app.width + 2*offset
    height = app.height + 2*offset
    drawRect(-offset+10*math.cos(.2*now),-offset+10*math.sin(now), width, height, fill=kBackgroundGradient2, opacity=30)
    drawRect(-offset+10*math.cos(.5*now),-offset+40*math.sin(.5*now), width, height, fill=kBackgroundGradient3, opacity=30)
    drawRect(-offset+30*math.cos(.8*now),-offset-20*math.sin(.5*now), width, height, fill=kBackgroundGradient4, opacity=30)
    # drawImage(floorTexture, 0,0)
    # endTime = time.time()
    # print(f'Done: Time= {endTime-startTime}s')

def drawThrowVisualization(app):
    drawFrisbeeTopDown(app, Frisbee((*app.frisbeeInitPoint, 5), Vector2(1,0), 0, 0, app.initPitch, 0))
    drawLabel(f'Pitch = {app.initPitch}', app.frisbeeInitPoint[0], app.frisbeeInitPoint[1]+30)
    drawLabel(f'Up Speed = {app.upSpeed}', app.frisbeeInitPoint[0], app.frisbeeInitPoint[1]+40)
    drawLabel(f'Changing: {"Pitch" if app.settingPitch else "Up Speed"}', app.frisbeeInitPoint[0], app.frisbeeInitPoint[1]+50)
    if app.throwPoint:
        drawLine(*app.frisbeeInitPoint, *app.throwPoint, fill=kFrisbeeColor, arrowEnd=True, opacity=40)
        if app.curvePoint:
            drawLine(*app.throwPoint, *app.curvePoint, fill=kFrisbeeColor, arrowEnd=True, opacity=40)

def drawPlayers(app):
    for team in app.teams:
        for player in team:
            drawPlayer(app, player)

def redrawAll(app):
    # print(f'Drawing All...', end='')
    # startTime = time.time()
    drawBackground(app)
    if app.mousePos: drawCircle(*app.mousePos.tup(), 5, fill='red', border='black', borderWidth=2)
    drawPlayers(app)
    if app.throwing: drawThrowVisualization(app)
    for frisbee in app.frisbees: drawFrisbeeTopDown(app, frisbee)

    # endTime = time.time()
    # print(f'Done: Time= {endTime-startTime}s')


def main():
    runApp()



main()