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
    app.isStarting = True
    app.isTutorial = True
    app.tutorialStep = 0

    #Scoring
    app.holeScore = 0
    app.courseScore = 0

    # COURSE
    app.course = None
    resetCourse(app)
    app.scored = False
    app.cameraX = 0

    #Environment
    app.clouds = []
    app.trees = []

    #FRISBEE SETTINGS
    app.frisbees = []
    app.newFrisbee = None
    app.frisbeeInitPoint = Vector2(kFrisbeeSize*2, kAppHeight/2)
    app.upSpeed = 5
    app.initPitch = 10
    app.mousePos = None
    app.throwPoint = None
    app.curvePoint = None

    #SLIDERS
    app.sliders2D = [Slider('Power', *kPwrSettings), Slider('Roll', *kRollSettings)]
    app.sliders3D = [Slider('Pitch', *kPitchSettings), Slider('Up Power', *kUPPwrSettings)]
    app.isSliding = False
    app.sliderIndex = 0

    #PLAYER SETTINGS
    app.goalPos = Vector2(kAppWidth - kFrisbeeSize*2, kAppHeight/2)
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
            app.courseScore += app.holeScore-app.course.calculatePar()
            app.frisbees = []
        else:
            frisbee.checkCollisions(app.course)
        if not frisbee.inFlight:
            if 0 > frisbee.x or frisbee.x > kAppWidth or 0 > frisbee.y or frisbee.y > kAppHeight:
                app.frisbeeInitPoint = Vector2(*kFrisbeeInitPos)
            else:
                app.frisbeeInitPoint = Vector2(frisbee.x, frisbee.y)
            app.frisbees = []
        if app.course:
            if frisbee.x < app.course.goal.x:
                app.cameraX = frisbee.x-kCameraRenderBuffer
            else:
                app.cameraX = app.course.goal.x-kCameraRenderBuffer
    for obstacle in app.course.obstacles:
        if obstacle.type == 'geyser':
            obstacle.checkActivation(time.time())
    for cloud in app.clouds:
        cloud.move()
    for team in app.teams:
        for player in team:
            player.takeMotionStep()
    if not bool(random.randint(0, int(1 / kCloudFrequency))):
        path = (kOSFilePath+'/Images/Cloud'+str(random.randint(0, kCloudVariantCount-1))+'.png')
        newCloud = Cloud(path, random.randint(kMinCloudScale*10, kMaxCloudScale*10)/10)
        if len(app.clouds) < kMaxCloudCount:
            app.clouds.append(newCloud)

def getAbsolutePath(relativeFilePath):
    absolutePath = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(absolutePath, relativeFilePath)

def resetCourse(app):
    app.frisbees = []
    app.teams = [[],[]]
    app.course = None
    initCourse(app, kAppWidth-400)
    app.frisbeeInitPoint = Vector2(kFrisbeeSize*2, kAppHeight/2)
    app.cameraX = 0
    app.scored=False
    app.holeScore = 0

def onKeyPress(app, key):
    if key == 'escape':
        app.quit()
    elif app.isStarting:
        app.isStarting = False
    elif app.isTutorial:
        advanceTutorial(app)
    else:   
        match key:
            case 'space':
                if app.newFrisbee:
                    app.frisbees.append(\
                        Frisbee(\
                            (app.frisbeeInitPoint.tup()[0], app.frisbeeInitPoint.tup()[1], kFrisbeeThrowHeight),\
                            app.newFrisbee.direction,\
                            app.sliders2D[0].value(), \
                            app.sliders3D[1].value(), \
                            app.sliders3D[0].value(), \
                            app.sliders2D[1].value()))
                    app.newFrisbee = None
                    app.holeScore += 1
                    WhooshSounds[random.randint(0, kWhooshes-1)].play()
                    if len(app.frisbees) > 1:
                        app.frisbees.pop(0)
            case 's':
                takeStep(app)
            case 'r':
                app.frisbeeInitPoint = Vector2(*kFrisbeeInitPos)
                app.frisbees = []
                app.holeScore += 1
            case 'n':
                resetCourse(app)
            case 't':
                app.isTutorial = True
            case 'l':
                app.drawLabels = not app.drawLabels
            case 'n':
                app.frisbees.append(Frisbee((200,200,0), Vector2(1,1), 50, 15, 20, 45))
            case 'backspace':
                if app.frisbees != []:
                    app.frisbees.pop(0)
            case 'tab':
                app.isTopDown = not app.isTopDown
            case _:
                if app.isTopDown:
                    game2D.keyPressed(app, key)
                else:
                    game3D.keyPressed(app, key)

def advanceTutorial(app):
    app.tutorialStep += 1
    if app.tutorialStep >= kTutorialSteps:
        app.isTutorial = False
        app.tutorialStep = 0

def onMousePress(app, mouseX, mouseY):
    if app.isStarting:
        app.isStarting = False
    elif app.scored:
        app.scored = False
        resetCourse(app)
    else:
        if clickedInSlider1(mouseX, mouseY):
            app.isSliding = True
            app.sliderIndex = 0
        elif clickedInSlider2(mouseX, mouseY):
            app.isSliding = True
            app.sliderIndex = 1
        else:
            app.isSliding = False
            if app.isTopDown:
                if app.throwing:
                    app.throwPoint = Vector2(mouseX, mouseY)
                else:
                    app.goalPos = Vector2(mouseX, mouseY)
                    if app.selectedPlayer:
                        # playerNumber = getClosestOffensivePlayer(app)
                        app.selectedPlayer.futureGoalPositions.append(app.goalPos)

def onMouseMove(app, mouseX, mouseY):
    app.mousePos = Vector2(mouseX, mouseY)

def clickedInSlider1(x, y):
    return kAppWidth - 2*kSliderSpacing - kSliderWidth > x > kAppWidth - 2*kSliderSpacing - 2*kSliderWidth and kAppHeight-kSliderSpacing > y > kAppHeight-kSliderSpacing-kSliderHeight

def clickedInSlider2(x, y):
    return kAppWidth-kSliderSpacing > x > kAppWidth-kSliderSpacing-kSliderWidth and kAppHeight-kSliderSpacing > y > kAppHeight-kSliderSpacing-kSliderHeight

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
                z = 0
                width = random.choice([i*kWallSizeMultiplier*kWallImageWidth/(kAppWidth / (kAppHeight-kVerticalBuffer)) for i in range(1,4)])
                height = random.choice([i*kWallSizeMultiplier*kWallImageHeight/kZHeightFactor for i in range(1,5)])
                newObstacle = Wall(x, y, z, width, height, random.choice([True, False, False]))
            case 'tree':
                newObstacle = Tree(x,y,height*100*kTreeBaseSizeMultiplier/kZHeightFactor)
            case 'geyser':
                newObstacle = Geyser(x, y, random.random() * (kMaxGeyserFrequencey-kMinGeyserFrequency) + kMinGeyserFrequency)
            case _:
                raise SillyException(f'Silly Goof! {obstacleChoice} is not in the match cases!')
        course.obstacles.append(newObstacle)
    

def onMouseDrag(app, mouseX, mouseY):
    
    if app.isSliding:
        relativeMouseHeight = (mouseY-kSliderSpacing-(kAppHeight-kSliderSpacing-kSliderHeight)) / kSliderHeight
        if app.isTopDown:
            app.sliders2D[app.sliderIndex].percentage = max(0, min(1-relativeMouseHeight, 1))
        else:
            app.sliders3D[app.sliderIndex].percentage = max(0, min(1-relativeMouseHeight, 1))
    app.curvePoint = (mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    if app.throwing and not app.scored and app.throwPoint:
        aimVector = app.throwPoint.subtracted(app.frisbeeInitPoint)
        rollVector = Vector2(app.throwPoint.x-mouseX, app.throwPoint.y-mouseY)
        rollDirection = rollVector.dotProduct(aimVector.leftVector())
        roll = -kRollControlMultiplier * math.copysign(rollVector.magnitude(), rollDirection)
        newFrisbee = Frisbee((*app.frisbeeInitPoint.tup(), kFrisbeeThrowHeight), aimVector.unitVector(), aimVector.magnitude() * kAimControlMultiplier, app.upSpeed, app.initPitch, roll)
        app.newFrisbee=newFrisbee
        app.curvePoint = None

def drawFPS(app, timeStart):
    now = time.time()
    if now == timeStart:
        fps = 'Unlimited'
    else: 
        fps = int(1 / (now - timeStart))
    drawLabel(fps, kAppWidth, 0, align='right-top')

def drawSliders(slider1, slider2):
    yPos = kAppHeight - kSliderSpacing

    #slider 1
    xPos = kAppWidth - 2*kSliderWidth - 2*kSliderSpacing
    fill1 = game2D.getColorForPercentage(slider1.percentage)
    drawRect(xPos, yPos, kSliderWidth, kSliderHeight, opacity=kSliderOpacity, borderWidth=kSliderBorderWidth, fill=None, align='left-bottom')
    drawRect(xPos, yPos, kSliderWidth, kSliderHeight*max(0.001, slider1.percentage), align='left-bottom', opacity=kSliderOpacity, fill=fill1)
    xPos += kSliderWidth/2
    if slider1.label == 'Power':
        drawLabel(f'{int(100*slider1.percentage)}%', xPos, yPos-kSliderTextSize/2, size=kSliderTextSize)
    else:
        drawLabel(int(slider1.value()), xPos, yPos-kSliderTextSize/2, size=kSliderTextSize)
    drawLabel(slider1.label, xPos, yPos+kSliderTextSize/2, size=kSliderTextSize)


    #slider 2
    xPos = kAppWidth - kSliderWidth - kSliderSpacing
    fill2 = game2D.getColorForPercentage(slider2.percentage)
    drawRect(xPos, yPos, kSliderWidth, kSliderHeight, opacity=kSliderOpacity, borderWidth=kSliderBorderWidth, align='left-bottom', fill=None)
    drawRect(xPos, yPos, kSliderWidth, kSliderHeight*max(0.001, slider2.percentage), align='left-bottom', opacity=kSliderOpacity, fill=fill2)
    xPos += kSliderWidth/2
    drawLabel(int(slider2.value()), xPos, yPos-kSliderTextSize/2, size=kSliderTextSize)
    drawLabel(slider2.label, xPos, yPos+kSliderTextSize/2, size=kSliderTextSize)

def drawScore(app):
    drawLabel(f'Score: {app.courseScore}', kScoreTextBuffer, kScoreTextBuffer, align='left-top', size=kScoreTextSize)
    drawLabel(f'Hole Par: {app.course.calculatePar()}', kScoreTextBuffer, 2*kScoreTextBuffer+kScoreTextSize, align='left-top', size=kScoreTextSize)
    drawLabel(f'Hole Throws: {app.holeScore}', kScoreTextBuffer, 3*kScoreTextBuffer+2*kScoreTextSize, align='left-top', size=kScoreTextSize)

def drawSplash(app):
    game3D.drawBackground(app)
    drawRect(0,0,kAppWidth, kAppHeight, fill=None, border='darkGray', borderWidth=10)
    drawRect(10,10,kAppWidth-20, kAppHeight-20, fill=None, border='silver', borderWidth=10)
    labelRot = math.sin(time.time()*kOpeningScreenTimeFactor) * 20
    drawImage(kGoalPath, 2*kAppWidth/3, 3*kAppHeight/4, align='center', width=200, height=400)
    fill = gradient('lightCyan', *[kFrisbeeColor]*int(60//30), 'skyBlue', 'steelBlue', start='top')
    drawLabel('SUPER PAPER FRISBEE GOLF', kAppWidth/2, kAppHeight/4, rotateAngle = labelRot, size=60, fill='red', border='dimGray', borderWidth=3, bold=True)
    drawOval(kAppWidth/3, 3*kAppHeight/5, 100, 300, fill=fill, rotateAngle=-40,border=kDiscGradient, borderWidth=kDiscBorderWidth)
    drawLabel('click anywhere to start', kAppWidth/2, kAppHeight-100, rotateAngle = -labelRot, size=20, fill='red', border='dimGray', borderWidth=1)

def drawTutorialStep(app):
    match app.tutorialStep:
        case 0:
            game2D.drawGame(app)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/8,  fill=kTutorialColor, border='darkGray', borderWidth=10, opacity=kTutorialOpacity, align='top')
            drawLabel('Welcome to Super Paper Frisbee Golf! Your goal is to throw the frisbee across the field', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('into the red goal on the right in fewer throws than the par. Be careful of the obstacles!', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('Press any key to continue.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
        case 1:
            game2D.drawGame(app)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/4,  fill=kTutorialColor, border='darkGray', borderWidth=10, opacity=kTutorialOpacity, align='top')
            drawLabel('The following are the obstacles to avoid, each with different properties.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('walls and trees will stop your frisbee, while orange bouncy walls will reflect the frisbee.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('Geysers will not impede your frisbee, but will shoot it upwards if the geyser is active.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawRect(4*kAppWidth/12, 2*kAppHeight/5+20, kObstacleThickness, 100, align='center', border=kBouncyColor, borderWidth = 5)
            drawImage(kTreeTopPath, 5*kAppWidth/12, 2*kAppHeight/5+20, align='center', borderWidth=2)
            drawRect(7*kAppWidth/12, 2*kAppHeight/5+20, kObstacleThickness, 100, align='center', fill=kWallColor)
            drawImage(kGeyserTopDownPath, 8*kAppWidth/12, 2*kAppHeight/5+20, align='center')
            
        case 2:
            game2D.drawGame(app)
            drawSliders(*app.sliders2D)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/8,  fill=kTutorialColor, border='darkGray', borderWidth=10, opacity=kTutorialOpacity, align='top')
            drawLabel('Click to change the direction of your throw.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('In the bottom right you have sliders to control the power and roll of your throw. Adjusting', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('the roll will cause the frisbee to curve left or right. To adjust, click and drag the bar.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            

        case 3:
            game3D.drawGame(app)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/8,  fill=kTutorialColor, border='darkGray', borderWidth=10, opacity=kTutorialOpacity, align='top')
            drawLabel('Welcome to the 3D view! Here you can see how high obstacles are (some walls are', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('short enough to throw over). ', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('To switch between views press \'tab\'. Every course is completely randomly generated.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            
        case 4:
            game3D.drawGame(app)
            drawSliders(*app.sliders3D)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, 3*kAppHeight/16,  fill=kTutorialColor, border='darkGray', borderWidth=10, opacity=kTutorialOpacity, align='top')
            drawLabel('In the bottom right you have sliders to control the upwards power of your throw and', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('pitch of the frisbee. Positive pitch will let the frisbee float better as it flies,', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('negative will quickly bring it down. Press \'space\' to throw. Good Luck!', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('Feel free to listen to the sound effects!', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+4*kScoreTextBuffer+3*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            


def redrawAll(app):
    if app.isStarting:
        drawSplash(app)
    elif app.isTutorial:
        drawTutorialStep(app)
    else:
        startTime = time.time()
        if app.isTopDown:
            game2D.drawGame(app)
            drawSliders(*app.sliders2D)
        else:
            game3D.drawGame(app)
            drawSliders(*app.sliders3D)
        drawFPS(app, startTime)
        drawScore(app)
        if app.scored:
            drawLabel('GOAL!', kAppWidth/2, kAppHeight/2, size=100, border='white', borderWidth=4)
            holeScore = app.holeScore-app.course.calculatePar()
            drawLabel(f'Hole Score: {holeScore if holeScore != 0 else "Par!"}', kAppWidth/2, kAppHeight/2 + 100, size=100, border='white', borderWidth=4)

def main():
    runApp()

main()