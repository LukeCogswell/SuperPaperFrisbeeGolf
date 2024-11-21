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

    #Environment
    app.clouds = []

    #FRISBEE SETTINGS
    app.frisbees = []
    app.frisbeeInitPoint = (kFrisbeeSize*2, app.height/2)
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
    for cloud in app.clouds:
        cloud.move()
    for team in app.teams:
        for player in team:
            player.takeMotionStep()
    app.clouds.sort(key=lambda cloud:cloud.scale)
    if not bool(random.randint(0, int(1 / kCloudFrequency))):
        path = ('D://Coding/CMU Classes/15112/SuperPaperFrisbeeGolf/src/Images/Cloud'+str(random.randint(0, kCloudVariantCount-1))+'.png')
        newCloud = Cloud(path, random.randint(kMinCloudScale*10, kMaxCloudScale*10)/10)
        app.clouds.append(newCloud)

def getAbsolutePath(relativeFilePath):
    absolutePath = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(absolutePath, relativeFilePath)

def onKeyPress(app, key):
    if key.isnumeric():
        if int(key)-1 <= len(app.teams[app.currTeamIndex]):
            app.selectedPlayer = app.teams[app.currTeamIndex][int(key)-1]
    else:    
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
            case 'v':
                if app.frisbees != []:
                    formOffense(app, 'vert')
            case 'g':
                spawnPlayerOnPoint(app, app.mousePos)
            case 'up':
                if app.settingPitch: app.initPitch += 5
                else: app.upSpeed += 1
            case 'backspace':
                if app.frisbees != []:
                    app.frisbees.pop(0)
            case 'down':
                if app.settingPitch: app.initPitch -= 5
                else: app.upSpeed -= 1
            case 'm':
                app.isTopDown = not app.isTopDown
            case 'escape':
                app.quit()

def onMousePress(app, mouseX, mouseY):
    if app.throwing:
        app.throwPoint = (mouseX, mouseY)
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

def onMouseDrag(app, mouseX, mouseY):
    app.curvePoint = (mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    if app.throwing:
        aimVector = Vector2(app.throwPoint[0]-app.frisbeeInitPoint[0], app.throwPoint[1]-app.frisbeeInitPoint[1])
        rollVector = Vector2(app.throwPoint[0]-mouseX, app.throwPoint[1]-mouseY)
        rollDirection = rollVector.dotProduct(aimVector.leftVector())
        roll = -kRollControlMultiplier * math.copysign(rollVector.magnitude(), rollDirection)
        newFrisbee = Frisbee((*app.frisbeeInitPoint, 5), aimVector.unitVector(), aimVector.magnitude() * kAimControlMultiplier, app.upSpeed, app.initPitch, roll)
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

def main():
    runApp()

main()