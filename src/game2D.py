from cmu_graphics import *
from constants import *
from classes import Frisbee, Vector2, Player
import math, time

kBackgroundGradient0 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='left')
kBackgroundGradient1 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='center')
kBackgroundGradient2 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//200), start='top')
kBackgroundGradient3 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//150), start='left-top')
kBackgroundGradient4 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//300), start='right-top')

def drawFrisbee(app, frisbee):
    # print(f'Drawing Frisbee...', end='')
    # startTime = time.time()
    sizeMultiplier = max(1, (frisbee.z/40 + 1))
    width = max(kFrisbeeSize * math.cos(math.radians(frisbee.pitch)), 1)
    height = max(kFrisbeeSize * math.cos(math.radians(frisbee.roll)), 1)
    rotAngle = frisbee.direction.getAngle()

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

def drawPlayerRoute(player):
    drawLine(*player.pos.tup(), *player.goalPos.tup(), arrowEnd=True, lineWidth=5, opacity=5, fill='cyan')
    for index in range(len(player.futureGoalPositions)):
        if index == 0:
            drawLine(*player.goalPos.tup(), *player.futureGoalPositions[index].tup(), arrowEnd=True, lineWidth=5, opacity=5, fill='cyan')
        else:
            drawLine(*player.futureGoalPositions[index-1].tup(), *player.futureGoalPositions[index].tup(), arrowEnd=True, lineWidth=5, opacity=5, fill='cyan')

def drawPlayer(app, player):
    drawRect(player.pos.x, player.pos.y, 20, 30, fill=kTeamColors[player.team], align='center')
    drawLabel(str(player.number), player.pos.x, player.pos.y, fill=kTeamColors[(player.team+1)%2], size=16)
    if app.drawLabels:
        drawPlayerRoute(player)
        drawLine(*player.pos.tup(), *player.pos.added(player.velocity).tup(), arrowEnd=True, lineWidth=3, opacity=30, fill='cyan')

def drawBackground(app):
    drawRect(0,0, app.width, app.height, fill=kBackgroundGradient0)
    offset = 40
    width = app.width + 2*offset
    height = app.height + 2*offset
    now = time.time()
    drawRect(-offset+10*math.cos(.2*now),-offset+10*math.sin(now), width, height, fill=kBackgroundGradient2, opacity=30)
    drawRect(-offset+10*math.cos(.5*now),-offset+40*math.sin(.5*now), width, height, fill=kBackgroundGradient3, opacity=30)
    drawRect(-offset+30*math.cos(.8*now),-offset-20*math.sin(.5*now), width, height, fill=kBackgroundGradient4, opacity=30)

def drawThrowVisualization(app):
    drawFrisbee(app, Frisbee((*app.frisbeeInitPoint, 5), Vector2(1,0), 0, 0, app.initPitch, 0))
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

def drawGame(app):
    drawBackground(app)
    if app.mousePos: drawCircle(*app.mousePos.tup(), 5, fill='red', border='black', borderWidth=2)
    drawPlayers(app)
    if app.throwing: drawThrowVisualization(app)
    for frisbee in app.frisbees: drawFrisbee(app, frisbee)