from constants import *
import math, random

class Frisbee():
    def __init__(self, pos, direction, forwardSpeed, upSpeed, pitch, roll,):
        self.direction = direction.unitVector() # 2D UNIT VECTOR
        self.leftDirection = direction.leftVector()
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
        if self.downSpeed > 0:
            return kGravity - 3*abs(math.cos(math.radians(self.roll))) - max(self.forwardSpeed*(-self.pitch/50), -kGravity)
        else:
            return (kFloatFactor * kGravity) - 3*abs(math.cos(math.radians(self.roll))) - max(self.forwardSpeed*(-self.pitch/50), -kGravity * kFloatFactor)

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
    
class Vector2():
    #Custom 2D Vector Class

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
        
    # represents x and y values
    def __repr__(self):
        return(f'Vector2({int(self.x)},{int(self.y)})')
    
    # Hashing for potential usage in sets
    def __hash__(self):
        return hash(str(self))
    
    # multiplies self by another vector or integer
    #  - if integer, treats it as scaling the magnitude, not each piece individually
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

    def leftVector(self):
        # gets vector of equal magnitude 90 degrees to the left of input 2D vector
        # used for frisbee curve
        return Vector2(-self.y, self.x)
    
    def getAngle(self):
        if self.magnitude() == 0: return 0 #Defaults to return 0 degrees for a magnitude of zero
        if self.x == 0:
            return 90
        return math.degrees(math.atan(self.y / self.x)) # vector angle in radians

    def distanceTo(self, other):
        if isinstance(other, Vector2):
            return ((self.x-other.x)**2 + (self.y - other.y)**2)**.5
        else:
            print(f'ERROR: cannot compute distance between Vector 2 and {type(other)}')

class Vector3():
    #Custom 3d Vector class
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
    
    def distanceTo(self, other):
        if isinstance(other, Vector3):
            return ((self.x-other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)**.5
        else:
            print(f'ERROR: cannot compute distance between Vector 2 and {type(other)}')

class Player():
    def __init__(self, vec2, number, team, isDefending, hasFrisbee):
        self.pos = vec2
        self.goalPos = vec2
        self.futureGoalPositions = []
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
        if self.pos.subtracted(self.goalPos).magnitude() <= kPositionAccuracy:
            if self.futureGoalPositions != []:
                self.goalPos = self.futureGoalPositions.pop(0)
        self.goalVelocity = self.calculateGoalVelocity()
        self.accelerate()
        self.move()

    def calculateGoalVelocity(self):
        goalVelocity = self.goalPos.subtracted(self.pos).clamped(kMaxPlayerSpeed)
        return goalVelocity

class Cloud():
    windSpeed = kWindSpeed
    def __init__(self, path, scale):
        self.x = -50 * scale
        self.y = (1-random.random()**2) * (kMinCloudHeight - 50)
        self.filePath = path
        self.scale = scale

    def move(self):
        self.x += Cloud.windSpeed * kMotionStepsPerSecond * self.scale
        if self.x > (self.scale * 200) + kAppWidth:
            self.remove()

    def remove(self):
        del(self)

class Tree():
    pass