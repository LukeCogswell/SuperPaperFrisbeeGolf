import cmu_graphics
import math

#CONSTANTS
kSpeedResistance = 0.1     # resistance to speed based on current speed - PERCENTAGE
kPitchResistance = 1.0     # resistance to speed based on current pitch - PERCENTAGE
kRollFactor      = 1.2     # roll increase based on current roll - PERCENTAGE 
kSideSpeedFactor = 1.2     # side speed increase factor based on current roll - PERCENTAGE

class Frisbee():
    def __init__(self, x, y, z, direction, speed, pitch, roll,):
        self.direction = direction # 
        self.forwardSpeed = speed
        self.sideSpeed = 0.0
        self.pitch = pitch # DEGREES
        self.roll = roll # DEGREES
        self.x = x
        self.y = y
        self.z = z

    def updatePosition(self): # convert speeds from vector direction to 
        forwardSpeed =

    def getForwardResistance(self):
        # Some base loss of speed by default plus resistance if the frisbee is showing face
        return self.forwardSpeed * kSpeedResistance + self.pitch * kPitchResistance

    def getSideRollAndSpeed(self):
        # If the frisbee has any roll, it will increase over time, especially at lower speeds, the more roll the more speed it will gain sideways
        # Frisbee side speed increase will be maximum at -45 degrees, no side speed increase at 0 and -90 (achieved with the sine of twice the angle)
        roll  =  kRollFactor * self.roll
        sideSpeedIncrease = math.sin(math.radians(math.abs(self.roll) * 2)) # absolute value to first find the magnitude of the side speed
        sideSpeed = math.copysign(sideSpeedIncrease, self.roll) + self.sideSpeed
        return roll, sideSpeed
    
    def takeFlightStep(self):

        self.roll, self.sideSpeed = self.getSideRollAndSpeed()
        self.forwardSpeed -= self.getForwardResistance()