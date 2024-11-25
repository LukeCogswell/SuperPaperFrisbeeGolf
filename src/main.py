from cmu_graphics import *
from constants import *
from classes import *
import game2D, game3D, math, time, os

def onAppStart(app):
    #DEFAULT SETTINGS
    app.width, app.height = kAppWidth, kAppHeight
    app.paused = kAppInitPauseState
    app.stepsPerSecond = kStepsPerSecond
    app.isTopDown = True

    # COURSE
    app.course = None
    initCourse(app, 1000)
    app.scored = False

    #Environment
    app.clouds = []
    app.trees = []

    #FRISBEE SETTINGS
    app.frisbees = []
    app.frisbeeInitPoint = Vector2(kFrisbeeSize*2, app.height/2)
    app.upSpeed = 5
    app.initPitch = 10
    app.mousePos = None
    app.throwPoint = None
    app.curvePoint = None

    #PLAYER SETTINGS
    app.goalPos = Vector2(app.width - kFrisbeeSize*2, app.height/2)
    app.teams = [[],[]]
    app.currTeamIndex = 0
    
    # DEBUG SETTINGS
    app.throwing = True
    app.selectedPlayer = None
    app.settingPitch = False
    app.drawLabels = False

def onStep(app):
    if not app.paused:
        takeStep(app)

def takeStep(app):  
    for frisbee in app.frisbees:
        frisbee.takeFlightStep()
        if frisbee.checkScored(app.course.goal):
            frisbee.stop()
            app.scored = True
            #TODO store score and exit course
        else:
            frisbee.checkCollisions(app.course)
        if not frisbee.inFlight:
            app.frisbeeInitPoint = Vector2(frisbee.x, frisbee.y)
    for cloud in app.clouds:
        cloud.move()
    for team in app.teams:
        for player in team:
            player.takeMotionStep()
    if not bool(random.randint(0, int(1 / kCloudFrequency))):
        path = ('D://Coding/CMU Classes/15112/SuperPaperFrisbeeGolf/src/Images/Cloud'+str(random.randint(0, kCloudVariantCount-1))+'.png')
        newCloud = Cloud(path, random.randint(kMinCloudScale*10, kMaxCloudScale*10)/10)
        app.clouds.append(newCloud)

def getAbsolutePath(relativeFilePath):
    absolutePath = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(absolutePath, relativeFilePath)

def resetCourse(app):
    app.frisbees = []
    app.teams = [[],[]]
    app.course = None
    initCourse(app, app.width-400)
    app.frisbeeInitPoint = Vector2(kFrisbeeSize*2, app.height/2)

def onKeyPress(app, key):
    match key:
        case 's':
            takeStep(app)
        case 'r':
            resetCourse(app)
        case 'space':
            app.paused = not app.paused
        case 'l':
            app.drawLabels = not app.drawLabels
        case 'n':
            app.frisbees.append(Frisbee((200,200,0), Vector2(1,1), 50, 15, 20, 45))
        case 'backspace':
            if app.frisbees != []:
                app.frisbees.pop(0)
        case 'm':
            app.isTopDown = not app.isTopDown
        case 'escape':
            app.quit()
        case _:
            if app.isTopDown:
                game2D.keyPressed(app, key)
            else:
                game3D.keyPressed(app, key)

def onMousePress(app, mouseX, mouseY):
    if app.scored:
        app.scored = False
        resetCourse(app)
    else:
        if app.throwing:
            app.throwPoint = Vector2(mouseX, mouseY)
        else:
            app.goalPos = Vector2(mouseX, mouseY)
            if app.selectedPlayer:
                # playerNumber = getClosestOffensivePlayer(app)
                app.selectedPlayer.futureGoalPositions.append(app.goalPos)

def onMouseMove(app, mouseX, mouseY):
    app.mousePos = Vector2(mouseX, mouseY)

###############################################################################
# The following functions will all be removed.
# They are remnants of Ultimate frisbee simulator which was my initial idea.
# They are still here because it is kinda fun and might have use in the future for code reuse.
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

def spawnPlayerOnPoint(app, point):
    if point:
        app.teams[app.currTeamIndex].append(Player(Vector2(*point.tup()), len(app.teams[app.currTeamIndex])+1, app.currTeamIndex, bool(app.currTeamIndex%2), False))

def formVertStack(app):
    frontStackPos = Vector2(app.frisbees[0].x + 50, app.height/2)
    handlerPos = Vector2(app.frisbees[0].x, app.frisbees[0].y)
    resetPos = Vector2(handlerPos.x - 60, handlerPos.y + 60)
    formationGoalPositions = [handlerPos, resetPos]
    for i in range(5):
        formationGoalPositions.append(frontStackPos.added(Vector2(80*i + (40 if i==6 else 0), 0)))
    for j in range(len(app.teams[app.currTeamIndex])):
        if not (j >= len(app.teams[app.currTeamIndex]) or j >= len(formationGoalPositions)):
            app.teams[app.currTeamIndex][j].goalPos = formationGoalPositions[j]

def formOffense(app, style):
    match style:
        case 'vert':
            formVertStack(app)
# end removal code
###############################################################################

def initCourse(app, length):
    app.course = Course(length, kDefaultObstaclePeriod)
    addObstacles(app.course)

def addObstacles(course):
    if course.obstacles != []: return
    for i in range(course.numObstacles):
        x = (i+1) * course.obstaclePeriod
        y = random.random() * (kAppHeight - 2*kSideBuffer) + kSideBuffer
        height = random.randint(0, kMaxObstacleHeight)
        obstacleChoice = random.choice(kObstacleTypes)
        match obstacleChoice:
            case 'wall':
                z = int(random.random() * kMaxWallGap)
                width = random.randint(kMinWallWidth, kMaxWallWidth)
                height = random.randint(kMinObstacleHeight, kMaxObstacleHeight-z)
                newObstacle = Wall(x, y, z, width, height, random.choice([True, False, False]))
            case 'tree':
                newObstacle = Tree(x,y,height*100*kTreeBaseSizeMultiplier/kZHeightFactor)
            case _:
                raise SillyException(f'Silly Goof! {obstacleChoice} is not in the match cases!')
        course.obstacles.append(newObstacle)

def onMouseDrag(app, mouseX, mouseY):
    app.curvePoint = (mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    if app.throwing and not app.scored and app.throwPoint:
        aimVector = app.throwPoint.subtracted(app.frisbeeInitPoint)
        rollVector = Vector2(app.throwPoint.x-mouseX, app.throwPoint.y-mouseY)
        rollDirection = rollVector.dotProduct(aimVector.leftVector())
        roll = -kRollControlMultiplier * math.copysign(rollVector.magnitude(), rollDirection)
        newFrisbee = Frisbee((*app.frisbeeInitPoint.tup(), kFrisbeeThrowHeight), aimVector.unitVector(), aimVector.magnitude() * kAimControlMultiplier, app.upSpeed, app.initPitch, roll)
        app.frisbees.append(newFrisbee)
        app.throwPoint = None
        app.curvePoint = None
        if len(app.frisbees) > 1:
            app.frisbees.pop(0)

def drawFPS(app, timeStart):
    now = time.time()
    if now == timeStart:
        fps = 'Unlimited'
    else: 
        fps = int(1 / (now - timeStart))
    drawLabel(fps, app.width, 0, align='right-top')

def redrawAll(app):
    startTime = time.time()
    if app.isTopDown:
        game2D.drawGame(app)
    else:
        game3D.drawGame(app)
    drawFPS(app, startTime)
    if app.scored:
        drawLabel('GOAL!', app.width/2, app.height/2, size=100, border='white', borderWidth=4)

def main():
    runApp()

main()