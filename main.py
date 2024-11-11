from cmu_graphics import *
import math
import random

#CONSTANTS
kAppWidth, kAppHeight = 1000, 1000
kAppInitPauseState = True

kSpeedResistance = 0.1     # resistance to speed based on current speed - PERCENTAGE
kPitchResistance = 0.1     # resistance to speed based on current pitch - PERCENTAGE
kRollFactor      = 1.05    # roll increase based on current roll - PERCENTAGE 
kRollFactorReduction = 1/5 # roll increase reduction based on current roll - RATIO
kleftSpeedFactor = 2.0     # side speed increase factor based on current roll - PERCENTAGE
kGravity = -1              # downward acceleration due to gravity - UNITS / STEP / STEP
kStepsPerSecond = 10 
 
class Frisbee():
    def __init__(self, pos, direction, forwardSpeed, upSpeed, pitch, roll,):
        magnitude = (direction[0]**2 + direction[1]**2)**0.5
        direction = direction[0] / magnitude, direction[1] / magnitude
        self.direction = direction # 2D UNIT VECTOR
        self.leftDirection = getPerpendicularVector(direction)
        self.forwardSpeed = forwardSpeed # UNITS/STEP
        self.leftSpeed = 0.0 # UNITS/STEP
        self.downSpeed = upSpeed # UNITS/STEP
        self.pitch = pitch # DEGREES
        self.roll = roll # DEGREES
        self.x = pos[0]
        self.y = pos[1]
        self.z = pos[2]

    def stop(self):
        self.z = 0
        self.roll = 0
        self.pitch = 0
        self.forwardSpeed = 0
        self.leftSpeed = 0

    def updatePosition(self): # convert speeds from vector direction to 
        xSpeed, ySpeed = self.getConvertedSpeeds()
        self.x += xSpeed
        self.y += ySpeed
        self.z += self.downSpeed

    def getConvertedSpeeds(self):
        xMagnitude = self.direction[0] * self.forwardSpeed + self.leftDirection[0] * self.leftSpeed
        yMagnitude = self.direction[1] * self.forwardSpeed + self.leftDirection[1] * self.leftSpeed
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
        leftSpeedIncrease = math.sin(math.radians(abs(self.roll) * 2)) # absolute value to first find the magnitude of the side speed
        leftSpeed = self.leftSpeed + math.copysign(leftSpeedIncrease, self.roll)
        return roll, leftSpeed
    
    def takeFlightStep(self):
        oldPos = self.x, self.y, self.z
        self.updatePosition()
        if self.z <= 0:
            self.stop()
        else:
            self.downSpeed += kGravity - abs(math.cos(math.radians(self.roll)))
            self.roll, self.leftSpeed = self.getSideRollAndSpeed()
            self.forwardSpeed -= self.getForwardResistance()
        newPos = self.x, self.y, self.z
        # print(f'{oldPos} --> {newPos}')

def getPerpendicularVector(vector):
    if vector[0] == 0:
        return (1, 0)
    if vector[1] == 0:
        return (0, 1)
    angle = math.atan(vector[1] / vector[0]) # Initial angle in radians
    angle += math.pi / 2 # angle + 90 degrees to get perpindicular direction
    return (math.cos(angle), math.sin(angle))

def getAngle(vector):
    if vector[0] == 0:
        return 90
    if vector[1] == 0:
        return 0
    return math.degrees(math.atan(vector[1] / vector[0])) # vector angle in radians

def onAppStart(app):
    app.width, app.height = kAppWidth, kAppHeight
    app.frisbees = []
    app.paused = kAppInitPauseState
    app.stepsPerSecond = kStepsPerSecond
    app.labelDiscs = False


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
            app.frisbees.append(Frisbee((200,200,0), (1,1), 50, 15, 20, 45))
        case 'escape':
            app.quit()

def onMousePress(app, mouseX, mouseY):
    app.frisbees.append(Frisbee((mouseX, mouseY, 5), (random.randint(-10, 10), random.randint(-10, 10)), random.randint(30, 100), random.randint(5, 15), random.randint(-10, 10), random.randint(-30,30)))

def redrawAll(app):
    for frisbee in app.frisbees:
        drawFrisbee(app, frisbee)

def drawFrisbee(app, frisbee):
    sizeMultiplier = max(20, (frisbee.z/20 + 1) * 20)
    drawOval(frisbee.x, frisbee.y, math.cos(math.radians(frisbee.pitch)) * sizeMultiplier, math.cos(math.radians(frisbee.roll)) * sizeMultiplier, fill='cyan', rotateAngle=getAngle(frisbee.direction), borderWidth=4, border='black')
    if app.labelDiscs:
        drawLabel(f'Height = {int(frisbee.z)}, Roll = {int(frisbee.roll)}, Pitch = {int(frisbee.pitch)}', frisbee.x, frisbee.y)


def main():
    runApp()



main()