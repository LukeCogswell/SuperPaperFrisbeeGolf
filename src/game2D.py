from cmu_graphics import *
from constants import *
from classes import Frisbee, Vector3, Vector2, Obstacle, Wall, Tree
import math, time

kBackgroundGradient0 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*((kAppWidth//80)+1), start='left')
kBackgroundGradient1 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='center')
kBackgroundGradient2 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//200), start='top')
kBackgroundGradient3 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//150), start='left-top')
kBackgroundGradient4 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//300), start='right-top')

# def keyPressed(app, key):   
    # match key: # Adjust camera position to see the whole course
    #     case 'up':
    #         app.cameraX += 10
    #     case 'down':
    #         app.cameraX -= 10
    #     case 'right':
    #         app.cameraX += 10
    #     case 'left':
    #         app.cameraX -= 10

def drawFrisbee(app, frisbee):
    sizeMultiplier = max(1, (frisbee.z/40 + 1))
    width = max(kFrisbeeSize * math.cos(math.radians(frisbee.pitch)), 1)
    height = max(kFrisbeeSize * math.cos(math.radians(frisbee.roll)), 1)
    rotAngle = frisbee.direction.getAngle()

    ## FRISBEE TRAIL ##
    drawTrail(app, frisbee, height)
    
    ## SHADOW ##
    drawOval(frisbee.x - app.cameraX + frisbee.z, frisbee.y + frisbee.z, width, height, fill=kShadowColor, rotateAngle=rotAngle, opacity=50)
    
    ## FRISBEE
    #adding gradient color to imitate shadow as the disc adjusts angles
    if abs(frisbee.roll) > 5: fill = gradient('lightCyan', *[kFrisbeeColor]*int(60//abs(frisbee.roll)), 'skyBlue', 'steelBlue', start=('top' if frisbee.roll>0 else 'bottom'))
    else: fill = kDiscGradient
    drawOval(frisbee.x - app.cameraX, frisbee.y, width * sizeMultiplier, height * sizeMultiplier, fill=fill, rotateAngle=rotAngle, borderWidth=kDiscBorderWidth, border=kDiscGradient)
    
    ## LABEL ##
    if app.drawLabels:
        drawLine(frisbee.x - app.cameraX, frisbee.y, frisbee.x - app.cameraX + 100*frisbee.direction.x, frisbee.y + 100*frisbee.direction.y, arrowEnd=True,fill='red', opacity=30)
        drawLine(frisbee.x - app.cameraX, frisbee.y, frisbee.x - app.cameraX + 100*frisbee.leftDirection.x, frisbee.y + 100*frisbee.leftDirection.y, arrowEnd=True,fill='lime', opacity=30)
        drawLabel(frisbee.getLabel(), frisbee.x - app.cameraX, frisbee.y+20) # draws frisbee label if labels are on
    # endTime = time.time()
    # print(f'Done: Time= {endTime-startTime}s')

## FRISBEE TRAIL ##
def drawTrail(app, frisbee, frisbeeWidth):
    if len(frisbee.trail) >= 2:
        prevPoint = frisbee.trail[0]
        prevPoint = prevPoint[0] - app.cameraX, prevPoint[1]
        for i in range(len(frisbee.trail)-1):
            currPoint = frisbee.trail[i+1]
            currPoint = currPoint[0] - app.cameraX, currPoint[1]
            width = kTrailWidth*(i+1)*((frisbee.z+1) / 30) * (frisbeeWidth / kFrisbeeSize)
            drawLine(*prevPoint, *currPoint, lineWidth=width, fill=kTrailColor, opacity=kTrailOpacity, dashes=True)
            prevPoint = frisbee.trail[i+1]
            prevPoint = prevPoint[0] - app.cameraX, prevPoint[1]

## OLD PLAYER CODE - REMOVE ##
# def drawPlayerRoute(player):
#     drawLine(*player.pos.tup(), *player.goalPos.tup(), arrowEnd=True, lineWidth=5, opacity=5, fill='cyan')
#     for index in range(len(player.futureGoalPositions)):
#         if index == 0:
#             drawLine(*player.goalPos.tup(), *player.futureGoalPositions[index].tup(), arrowEnd=True, lineWidth=5, opacity=5, fill='cyan')
#         else:
#             drawLine(*player.futureGoalPositions[index-1].tup(), *player.futureGoalPositions[index].tup(), arrowEnd=True, lineWidth=5, opacity=5, fill='cyan')

# def drawPlayer(app, player):
#     drawRect(player.pos.x, player.pos.y, 20, 30, fill=kTeamColors[player.team], align='center')
#     drawLabel(str(player.number), player.pos.x, player.pos.y, fill=kTeamColors[(player.team+1)%2], size=16)
#     if app.drawLabels:
#         drawPlayerRoute(player)
#         drawLine(*player.pos.tup(), *player.pos.added(player.velocity).tup(), arrowEnd=True, lineWidth=3, opacity=30, fill='cyan')

# def drawPlayers(app):
#     for team in app.teams:
#         for player in team:
#             drawPlayer(app, player)
## END OLD CODE ##

## GRASS ##
def drawBackground(app):
    cameraOffset = app.cameraX % 80
    drawRect(-cameraOffset,0, app.width+80, app.height, fill=kBackgroundGradient0)
    offset = 40
    width = app.width + 2*offset
    height = app.height + 2*offset
    now = time.time()
    drawRect(-offset+10*math.cos(.2*now),-offset+10*math.sin(now), width, height, fill=kBackgroundGradient2, opacity=30)
    drawRect(-offset+10*math.cos(.5*now),-offset+40*math.sin(.5*now), width, height, fill=kBackgroundGradient3, opacity=30)
    drawRect(-offset+30*math.cos(.8*now),-offset-20*math.sin(.5*now), width, height, fill=kBackgroundGradient4, opacity=30)

## FOR SLIDERS AND POWER VISUALIZATION ##
def getColorForPercentage(percentage):
    return rgb(percentage*255, (1-percentage)*255, 100)

## THROW VISUALIZATION ## 
def drawThrowVisualization(app):
    directionVector = Vector2(1,0)
    if app.throwPoint:
        directionVector = app.throwPoint.subtracted(app.frisbeeInitPoint).unitVector().multipliedBy(Vector2(kShotLineLength, kShotLineLength))
        power = app.sliders2D[0].value() * kPowerWidthRatio
        lineEnd = app.frisbeeInitPoint.added(directionVector).tup()
        lineEnd = lineEnd[0] - app.cameraX, lineEnd[1]
        drawLine(app.frisbeeInitPoint.tup()[0]-app.cameraX, app.frisbeeInitPoint.tup()[1], *lineEnd, lineWidth=max(power,1), fill=getColorForPercentage(app.sliders2D[0].percentage), arrowEnd=True)
    drawFrisbee(app, Frisbee((app.frisbeeInitPoint.x, app.frisbeeInitPoint.y, kFrisbeeThrowHeight), directionVector, 0, 0, app.sliders3D[0].value(), app.sliders2D[1].value()))

## COURSE ## 
def drawCourse(app):
    for obstacle in app.course.obstacles:
        match obstacle.type:
            case 'wall':
                if obstacle.isBouncy:
                    drawRect(obstacle.x - app.cameraX, obstacle.y, kObstacleThickness, obstacle.width, align='center', border=kBouncyColor, borderWidth = 5)
                else:
                    drawRect(obstacle.x - app.cameraX, obstacle.y, kObstacleThickness, obstacle.width, align='center', fill=kWallColor)
                if app.drawLabels:
                    drawLabel(obstacle, obstacle.x - app.cameraX, obstacle.y, fill='white')
            case 'tree':
                drawImage(kTreeTopPath, obstacle.x - app.cameraX, obstacle.y, align='center', borderWidth=2)
                if app.drawLabels:
                    drawLabel(obstacle, obstacle.x - app.cameraX, obstacle.y, fill='white')
            case 'geyser':
                drawImage(kGeyserTopDownPath, obstacle.x - app.cameraX, obstacle.y, align='center')
                if obstacle.isActive:
                    size = obstacle.getSize(time.time())
                    drawImage(kGeyserSprayTopDownPath, obstacle.x - app.cameraX, obstacle.y, width = size, height = size,align='center')
                if app.drawLabels:
                    drawLabel(obstacle, obstacle.x - app.cameraX, obstacle.y, fill='white')
    drawImage(kGoalTopDownPath, app.course.goal.x - app.cameraX, app.course.goal.y, align="center")

## BASE DRAW FUNCTION CALLED BY MAIN ##
def drawGame(app):
    drawBackground(app)
    if app.mousePos: drawCircle(*app.mousePos.tup(), 5, fill='red', border='black', borderWidth=2)
    if app.throwing: drawThrowVisualization(app)
    drawCourse(app)
    for frisbee in app.frisbees: drawFrisbee(app, frisbee)