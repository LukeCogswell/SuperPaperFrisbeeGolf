from cmu_graphics import gradient, rgb, Sound
import os
kAppWidth, kAppHeight = 1600, 1000
kAppInitPauseState = False

## FRISBEE FLIGHT
kSpeedResistance = 0.1     # resistance to speed based on current speed - PERCENTAGE
kPitchResistance = 0.1     # resistance to speed based on current pitch - PERCENTAGE
kRollFactor      = 0.05    # roll increase based on current roll - PERCENTAGE 
kRollFactorReduction = 1/5 # roll increase reduction based on current roll - RATIO
kleftSpeedFactor = 10.0     # side speed increase factor based on current roll - PERCENTAGE
kGravity = -.4              # downward acceleration due to gravity - UNITS / STEP / STEP

## TO BE REMOVED - PLAYER CONTROL
kMaxPlayerAcceleration = 10
kMaxPlayerSpeed = 50
kPositionAccuracy = 20
kTeamColors = ['black', 'white']

# AIM AND FIRE
kRollControlMultiplier = 1 / 10
kAimControlMultiplier = 1 / 4
kFrisbeeThrowHeight = 11
kShotLineLength = 200

# APP SPEED
kStepsPerSecond = 60 
kMotionStepsPerSecond = 5
kMotionTimeFactor = kMotionStepsPerSecond / kStepsPerSecond


# FRISBEE AESTHETICS
kTrailLength = 5
kTrailOpacity = 40
kTrailWidth = 3
kDiscBorderWidth = 3
kPowerWidthRatio = 1 / 20
kFrisbeeSize = 30
kFloatFactor = 5 / 100
kFrisbee3DSize = 2 * kFrisbeeSize
kFrisbeeColor = 'lightBlue'
kTrailColor = kFrisbeeColor
kShadowColor = 'black'
kDiscGradient = gradient(*[kFrisbeeColor]*4, 'skyBlue', 'steelBlue', start='center')

# GENERAL CONSTANTS
kZHeightFactor = 10
kCameraRenderBuffer = 100
kMinSize = 0.05
kOpeningScreenTimeFactor = 1
kFrisbeeInitPos = (kFrisbeeSize*2, kAppHeight/2)

# BACKGROUND COLORS
kGrassLight, kGrassMedium, kGrassDark = rgb(20, 150, 50), rgb(30, 125, 30), rgb(20, 100, 10)
kSkyDark, kSkyMedium, kSkyLight = rgb(90, 130, 255), rgb(100, 150, 200), rgb(180, 220, 255)
kHorizonHeight = 220
kOSFilePath = os.path.dirname(__file__)
kTrailPath = kOSFilePath + '/Images/FrisbeeTrail.png'
kMountainPath = kOSFilePath+'/Images/Mountains.png'
kWaterSize = 50
kWaterPath = kOSFilePath+'/Images/Water.png'
kWaterCornerPath = kOSFilePath+'/Images/WaterCorner.png'

# CLOUDS
kMinCloudHeight = kAppHeight - (kHorizonHeight + 330)
kCloudVariantCount = 5
kCloudFrequency = 1 / 40 # 1 every 40 steps
kCloudSize = (100, 50)
kMinCloudScale = .7
kMaxCloudScale = 3
kWindSpeed = .2
kMaxCloudCount = 20

#Scoring Constants
kScorableHeight = kFrisbeeThrowHeight
kScorableTolerance = 5
kScoreTextBuffer = 15
kScoreTextSize = 20

#Sliders
kSliderWidth = 50
kSliderHeight = 500
kSliderOpacity = 100
kSliderSpacing = 40
kSliderBorderWidth = 10
kSliderTextSize = 20
#Power min, max, default
kPwrSettings = [0, 300, 100]
#Roll
kRollSettings = [-90, 90, 0]
#Pitch
kPitchSettings = [-45, 45, 10]
#Up Power
kUPPwrSettings = [0, 15, 6]

# OBSTACLES
kObstacleTypes = ['wall', 'tree', 'geyser']
kSideBuffer = 100
kVerticalBuffer = 0
kTreeVariantCount = 1
kWallVariantCount = 1
kTreeBaseSizeMultiplier = 4
kDefaultObstaclePeriod = 150
kWallSizeMultiplier = 2
kWallImageWidth = 100
kWallImageHeight = 50
kObstacleThickness = 30
kMinObstacleHeight = 10
kMaxObstacleHeight = 30
kMaxGeyserFrequencey = 100/2
kMinGeyserFrequency = 100/10
kMaxGeyserPower = 10
kMinGeyserPower = 5
kTreeTopPath = kOSFilePath + '/Images/TreeTopDown.png'
kGoalPath = kOSFilePath + '/Images/Goal.png'
kGoalTopDownPath = kOSFilePath + '/Images/GoalTopdown.png'
kWallPath = kOSFilePath + '/Images/WoodWall.png'
kBouncyWallPath = kOSFilePath + '/Images/BouncyWall.png'
kGeyserPath3D = kOSFilePath + '/Images/Geyser3D.png'
kGeyserTopDownPath = kOSFilePath + '/Images/GeyserTopDown.png'
kGeyserSprayTopDownPath = kOSFilePath + '/Images/GeyserSprayTopDown.png'
kGeyserSpray3DPath = kOSFilePath + '/Images/GeyserSpray.png'

# OBSTACLE AESTHETICS
kBouncyColor = 'orange'
kWallColor = rgb(255 * .396, 255 * .298, 255 * .227)

#SOUND EFFECTS WOO! - All voiced by yours truly ;)
kBonkPath = kOSFilePath + '/Sounds/Bonk.mp3'
kBoingPath = kOSFilePath + '/Sounds/Boing'
kWhooshPath = kOSFilePath + '/Sounds/Whoosh'
# number of each sound effect
kBonks = 1
kBoings = 2
kWhooshes = 5
BonkSound = Sound(kBonkPath)
Boing0 = Sound(kBoingPath+'0.mp3')
Boing1 = Sound(kBoingPath+'1.mp3')
BoingSounds = [Sound(kBoingPath+str(i)+'.mp3') for i in range(kBoings)]
WhooshSounds = [Sound(kWhooshPath+str(i)+'.mp3') for i in range(kWhooshes)]