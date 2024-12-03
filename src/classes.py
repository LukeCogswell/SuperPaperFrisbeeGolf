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
        self.wind=None

    def __repr__(self):
        return f'Frisbee(pos=({self.x}, {self.y}, {self.z}))'

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

    def checkScored(self, goal):
        xCheck = abs(self.x-goal.x) <= kFrisbeeSize/2
        yCheck = abs(self.y-goal.y) <= kFrisbeeSize/2
        zCheck = abs(self.z-kScorableHeight) <= kScorableTolerance
        return xCheck and yCheck and zCheck

    def checkCollisions(self, course):
        # Returns true if frisbee is colliding, false if not
        for obstacle in course.obstacles:
            # Checks x y and z to see if the frisbee is colliding with the obstacle (all hitboxes are cubes)
            xCheck = abs(self.x - obstacle.x) <= kFrisbeeSize/2+obstacle.depth/2
            yCheck = abs(self.y - obstacle.y) <= kFrisbeeSize/2+obstacle.width/2
            if obstacle.type == 'geyser':
                zCheck = obstacle.isActive
            else:
                zCheck = obstacle.z < self.z < (obstacle.z+obstacle.height)
            
            if zCheck and xCheck and yCheck:
                self.collide(obstacle)
                return True
        return False

    def getReflectionVector(self, obstacle):
        # (2(N dot L) N - L) gives the reflected vector where L is the incident vector and N is the normal vector of the flat surface
        collidingNormal = obstacle.getCollisionNormal(self)
        incidentAngle = self.direction
        return collidingNormal.multipliedBy(2).multipliedBy(incidentAngle.dotProduct(collidingNormal)).subtracted(incidentAngle)

    def collide(self, obstacle):
        if obstacle.type == 'geyser':
            self.downSpeed += obstacle.power
            WhooshSounds[random.randint(0, kWhooshes-1)].play()
        elif obstacle.isBouncy:
            self.direction = self.getReflectionVector(obstacle)
            BoingSounds[random.randint(0, kBoings-1)].play()
        else: 
            BonkSound.play()
            self.forwardSpeed = -10
            self.upSpeed = -4

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
                self.applyWind()
            self.trail.append((self.x, self.y))
        if (len(self.trail) > (kTrailLength * (kStepsPerSecond / 20)) or not self.inFlight) and self.trail != []:
            self.trail.pop(0)
        # endTime = time.time()
        # print(f'Done: Time= {endTime-startTime}s')
    def applyWind(self):
        if self.wind:
            wind = self.wind.multipliedBy(self.z*kZWindFactor)
            forwardWindSpeed = wind.dotProduct(self.direction) * math.sin(self.pitch)
            leftWindSpeed = wind.dotProduct(self.leftDirection) * math.sin(self.roll)
            self.forwardSpeed += forwardWindSpeed
            leftWindSpeed += leftWindSpeed

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
    
    def tup(self):
        return (self.x, self.y, self.z)

    def in2D(self):
        return Vector2(self.x, self.y)

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
            self.x = -(self.scale * 200)

    def remove(self):
        del(self)

class Course():
    def __init__(self, length: int, obstaclePeriod:float):
        self.length = length # top-down pixels
        self.obstaclePeriod = obstaclePeriod # pixels between obstacles
        self.numObstacles = length//(self.obstaclePeriod) - 1
        self.goalPos = Vector2(length, random.random() * (kAppHeight-2*kSideBuffer)+kSideBuffer)
        self.goal = Goal(*self.goalPos.tup(), 0)
        self.obstacles = []

    def getVisibleObjects(self, playerPos: Vector2):
        visibleObjects = []
        for obstacle in self.obstacles:
            if obstacle.x > playerPos.x:
                visibleObjects.append(obstacle)
        return visibleObjects
    
    def hasStraightLineToGoal(self):
        def lineFunction(x):
            return (self.goalPos.y-kFrisbeeInitPos[1]) / (self.goalPos.x - kFrisbeeInitPos[0]) * (x) + kFrisbeeInitPos[1]
        for obstacle in self.obstacles:
            if abs(lineFunction(obstacle.x) - obstacle.y) <= obstacle.width+kFrisbeeSize:
                return False
        return True

    #Algorithm to calculate par for a course
    def calculatePar(self):
        if self.hasStraightLineToGoal(): return 1
        throwsRequired = 2
        for obstacle in self.obstacles:

            # if the obstacle isn't tall enough to impede a throw, ignore it in the calculation
            if obstacle.height <= kMinObstacleHeight:
                continue

            # if the obstacle is close to the disc starting position, add a shot to the counter
            elif obstacle.x <= self.obstaclePeriod and abs(obstacle.y-kFrisbeeInitPos[1]) <= obstacle.width:
                throwsRequired += 1
                continue

            # if the obstacle is close to the goal and directly in front of it, add a shot to the counter
            elif obstacle.x >= self.obstaclePeriod*(self.numObstacles) and abs(obstacle.y-self.goalPos.y) <= obstacle.width:
                throwsRequired += 1
                continue


        return throwsRequired


    def __repr__(self):
        return f'Course(len={self.length}, #obstacles={self.numObstacles})'

class Goal():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f'Goal(x, y, z = {self.x}, {self.y}, {self.z})'

class Obstacle():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = None
    
    def __repr__(self):
        return f'Obstacle({type(self)}, x={self.x}, y={self.y})'
    
    def getCollisionNormal(self, frisbee):
        if self.x-frisbee.x > kFrisbeeSize + self.depth/2:
            return Vector2(-1,0)
        elif self.x-frisbee.x < - kFrisbeeSize + self.depth+kFrisbeeSize/2:
            return Vector2(1, 0)
        elif self.y-frisbee.y < kFrisbeeSize + self.width/2:
            return Vector2(0, -1)
        else:
            return Vector2(0, 1)       
        
class Wall(Obstacle):
    def __init__(self, x, y, z, width, height, isBouncy):
        super().__init__(x, y)
        self.z = z
        self.width = width
        self.height = height
        self.depth = kObstacleThickness
        self.isBouncy = isBouncy
        if isBouncy: self.path3D = (kOSFilePath+'/Images/BouncyWall.png')
        else: self.path3D = (kOSFilePath+'/Images/WoodWall.png')
        self.type = 'wall'
    def __repr__(self):
        return f'Obstacle({type(self)}, x={int(self.x)}, y={int(self.y)}, z={int(self.z)}, height={int(self.height)}, width={int(self.width)})'

class Tree(Obstacle):
    def __init__(self, x, y, height):
        super().__init__(x, y)
        self.z = 0
        self.isBouncy = False
        self.height = height
        self.width = kObstacleThickness
        self.path3D = (kOSFilePath+'/Images/Tree'+str(random.randint(0, kTreeVariantCount-1))+'.png')
        self.type = 'tree'
        self.depth = 50

class Geyser(Obstacle):
    def __init__(self, x, y, frequency):
        super().__init__(x,y)
        self.frequency = frequency
        self.width = kObstacleThickness
        self.depth = kObstacleThickness
        self.height = 0
        self.spriteRotation = random.random() * 360
        self.isActive = False
        self.power = random.random() * (kMaxGeyserPower-kMinGeyserPower) + kMinGeyserPower
        self.type = 'geyser'
    
    def checkActivation(self, currTime):
        activeLength = (1 / 3) * (1 / self.frequency)
        if currTime % (1 / self.frequency) <= activeLength:
            self.isActive = True
            self.height = kMaxObstacleHeight * (math.sin( ((currTime) % activeLength) / activeLength * math.pi)) * 2
        else:
            self.height = 0
            self.isActive = False

    def getSize(self, currTime):
        return max(0.1,self.height/kMaxObstacleHeight) * 50 #* ((math.sin(currTime/100)**5)+2)

    def __repr__(self):
        return f'Obstacle({type(self)}, x={int(self.x)}, y={int(self.y)}, isActive={self.isActive}, height={int(self.height)})'

class Slider():
    def __init__(self, label, min, max, defaultValue):
        self.min = min
        self.max = max
        self.percentage = (defaultValue-self.min) / (self.max - self.min)
        self.label= label

    def value(self):
        return self.percentage * (self.max-self.min) + self.min

class SillyException(Exception):
    def __init__(self, message):
        super().__init__(message)
