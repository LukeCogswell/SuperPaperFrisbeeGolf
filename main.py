from cmu_graphics import *
import math
import random

#CONSTANTS
kAppWidth, kAppHeight = 1000, 1000
kAppInitPauseState = False

kSpeedResistance = 0.1     # resistance to speed based on current speed - PERCENTAGE
kPitchResistance = 0.1     # resistance to speed based on current pitch - PERCENTAGE
kRollFactor      = 1.05    # roll increase based on current roll - PERCENTAGE 
kRollFactorReduction = 1/5 # roll increase reduction based on current roll - RATIO
kleftSpeedFactor = 2.0     # side speed increase factor based on current roll - PERCENTAGE
kGravity = -.4              # downward acceleration due to gravity - UNITS / STEP / STEP

kRollControlMultiplier = 1 / 10
kAimControlMultiplier = 1 / 4

kStepsPerSecond = 10 

kTrailOpacity = 40
kTrailWidth = 5
kDiscBorderWidth = 4
kFrisbeeSize = 30
kFrisbeeColor = 'lightBlue'
kTrailColor = kFrisbeeColor
kShadowColor = 'black'
kDiscGradient = gradient(*[kFrisbeeColor]*4, 'skyBlue', 'steelBlue', start='center')

floorTexture = './CMU Classes/15112/FrisbeeFlight_15112_TP/Images/GrassMirror.png'
 
class Vector2():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def unitVector(self):
        if self.magnitude() == 0: return (0,0)
        return Vector2(self.x / self.magnitude(), self.y / self.magnitude())
        
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
    
    def dotProduct(self, other):
        if isinstance(other, Vector2):
            return self.x * other.x + self.y * other.y
        return None

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
        self.x += xSpeed
        self.y += ySpeed
        self.z += self.downSpeed

    def getConvertedSpeeds(self):
        xMagnitude = self.direction.x * self.forwardSpeed + self.leftDirection.x * self.leftSpeed
        yMagnitude = self.direction.y * self.forwardSpeed + self.leftDirection.y * self.leftSpeed
        return xMagnitude, yMagnitude

    def getForwardResistance(self):
        # Some base loss of speed by default plus resistance if the frisbee is showing face
        return self.forwardSpeed * kSpeedResistance + self.pitch * kPitchResistance

    def getSideRollAndSpeed(self):
        # If the frisbee has any roll, it will increase over time, especially at lower speeds, the more roll the more speed it will gain sideways
        # Frisbee side speed increase will be maximum at -45 degrees, no side speed increase at 0 and -90 (achieved with the sine of twice the angle)
        if self.roll <= 45:
            roll = kRollFactor * self.roll
        else:
            roll = ((kRollFactor-1)*kRollFactorReduction + 1) * self.roll
        leftSpeedIncrease = kleftSpeedFactor * math.sin(math.radians(abs(self.roll) * 2)) # absolute value to first find the magnitude of the side speed
        leftSpeed = self.leftSpeed + math.copysign(leftSpeedIncrease, self.roll)
        return roll, leftSpeed
    
    def takeFlightStep(self):
        oldPos = self.x, self.y, self.z
        if self.inFlight:
            # self.trail.append((self.x, self.y, self.z, self.pitch, self.roll))
            self.updatePosition()
            if self.z <= 0:
                self.stop()
            else:
                self.downSpeed += kGravity - abs(math.cos(math.radians(self.roll)))
                self.roll, self.leftSpeed = self.getSideRollAndSpeed()
                self.forwardSpeed -= self.getForwardResistance()
            self.trail.append((self.x, self.y))
            newPos = self.x, self.y, self.z
            # print(newPos)
            # print(f'{oldPos} --> {newPos}')
        if (len(self.trail) > 5 or not self.inFlight) and self.trail != []:
            self.trail.pop(0)

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

def onAppStart(app):
    app.width, app.height = kAppWidth, kAppHeight
    app.frisbees = []
    app.paused = kAppInitPauseState
    app.stepsPerSecond = kStepsPerSecond
    app.labelDiscs = False
    app.frisbeeInitPoint = (app.width/2, app.height-kFrisbeeSize)
    app.throwPoint = None
    app.curvePoint = None

def onStep(app):
    if not app.paused:
        takeStep(app)

def takeStep(app):
    for frisbee in app.frisbees:
        frisbee.takeFlightStep()

def onKeyPress(app, key):
    match key:
        case 's':
            takeStep(app)
        case 'r':
            app.frisbees = []
        case 'space':
            app.paused = not app.paused
        case 'l':
            app.labelDiscs = not app.labelDiscs
        case 'n':
            app.frisbees.append(Frisbee((200,200,0), Vector2(1,1), 50, 15, 20, 45))
        case 'escape':
            app.quit()

def onMousePress(app, mouseX, mouseY):
    app.throwPoint = (mouseX, mouseY)

def onMouseDrag(app, mouseX, mouseY):
    app.curvePoint = (mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    aimVector = Vector2(app.throwPoint[0]-app.frisbeeInitPoint[0], app.throwPoint[1]-app.frisbeeInitPoint[1])
    rollVector = Vector2(app.throwPoint[0]-mouseX, app.throwPoint[1]-mouseY)
    rollDirection = rollVector.dotProduct(getLeftVector(aimVector))
    roll = -kRollControlMultiplier * math.copysign(rollVector.magnitude(), rollDirection)
    newFrisbee = Frisbee((*app.frisbeeInitPoint, 5), aimVector.unitVector(), aimVector.magnitude() * kAimControlMultiplier, 10, 5, roll)
    app.frisbees.append(newFrisbee)
    app.throwPoint = None
    app.curvePoint = None

def drawFrisbee(app, frisbee):
    sizeMultiplier = max(1, (frisbee.z/40 + 1))
    width = max(kFrisbeeSize * math.cos(math.radians(frisbee.pitch)), 1)
    height = max(kFrisbeeSize * math.cos(math.radians(frisbee.roll)), 1)
    rotAngle = getAngle(frisbee.direction)

    ## FRISBEE TRAIL ##
    drawTrail(frisbee)
    
    ## SHADOW ##
    drawOval(frisbee.x + frisbee.z, frisbee.y + frisbee.z, width, height, fill=kShadowColor, rotateAngle=rotAngle, opacity=50)
    
    ## FRISBEE
    #adding gradient color to imitate shadow as the disc adjusts angles
    if abs(frisbee.roll) > 5: fill = gradient('lightCyan', *[kFrisbeeColor]*int(60//abs(frisbee.roll)), 'skyBlue', 'steelBlue', start=('top' if frisbee.roll>0 else 'bottom'))
    else: fill = kDiscGradient
    drawOval(frisbee.x, frisbee.y, width * sizeMultiplier, height * sizeMultiplier, fill=fill, rotateAngle=rotAngle, borderWidth=kDiscBorderWidth, border=kDiscGradient)
    
    ## LABEL ##
    if app.labelDiscs:
        drawLine(frisbee.x, frisbee.y, frisbee.x + 100*frisbee.direction.x, frisbee.y + 100*frisbee.direction.y, arrowEnd=True,fill='red', opacity=30)
        drawLine(frisbee.x, frisbee.y, frisbee.x + 100*frisbee.leftDirection.x, frisbee.y + 100*frisbee.leftDirection.y, arrowEnd=True,fill='lime', opacity=30)
        drawLabel(frisbee.getLabel(), frisbee.x, frisbee.y+20) # draws frisbee label if labels are on

def drawTrail(frisbee):
    if len(frisbee.trail) >= 2:
        prevPoint = frisbee.trail[0]
        for i in range(len(frisbee.trail)-1):
            currPoint = frisbee.trail[i+1]
            drawLine(*prevPoint, *currPoint, lineWidth=kTrailWidth*(i+1)*((frisbee.z+1) / 30), fill=kTrailColor, opacity=kTrailOpacity, dashes=True)
            prevPoint = frisbee.trail[i+1]

def drawBackground(app):
    for col in range(app.width//200):
        for row in range(app.height//200):
            drawImage(floorTexture, 200*col, 200*row, rotateAngle=180*(col+row))

def drawThrowVisualization(app):
    drawCircle(*app.frisbeeInitPoint, kFrisbeeSize, fill=kFrisbeeColor, border=kDiscGradient, borderWidth=kDiscBorderWidth)
    if app.throwPoint:
        drawLine(*app.frisbeeInitPoint, *app.throwPoint, fill='red', arrowEnd=True, opacity=40)
        if app.curvePoint:
            drawLine(*app.throwPoint, *app.curvePoint, fill='red', opacity=40)

def redrawAll(app):
    drawBackground(app)
    drawThrowVisualization(app)
    for frisbee in app.frisbees:
        drawFrisbee(app, frisbee)


def main():
    runApp()



main()