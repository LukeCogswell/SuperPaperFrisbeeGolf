from cmu_graphics import gradient, rgb
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
kFrisbeeThrowHeight = 5

# APP SPEED
kStepsPerSecond = 60 
kMotionStepsPerSecond = 5
kMotionTimeFactor = kMotionStepsPerSecond / kStepsPerSecond

# GENERAL CONSTANTS
kZHeightFactor = 10

# FRISBEE AESTHETICS
kTrailLength = 5
kTrailOpacity = 40
kTrailWidth = 3
kDiscBorderWidth = 10
kFrisbeeSize = 30
kFloatFactor = 5 / 100
kFrisbee3DSize = 2 * kFrisbeeSize
kFrisbeeColor = 'lightBlue'
kTrailColor = kFrisbeeColor
kShadowColor = 'black'
kDiscGradient = gradient(*[kFrisbeeColor]*4, 'skyBlue', 'steelBlue', start='center')

# BACKGROUND COLORS
kGrassLight, kGrassMedium, kGrassDark = rgb(20, 150, 50), rgb(30, 125, 30), rgb(20, 100, 10)
kSkyDark, kSkyMedium, kSkyLight = rgb(90, 130, 255), rgb(100, 150, 200), rgb(180, 220, 255)
kHorizonHeight = 220
kMountainPath = 'D://Coding/CMU Classes/15112/SuperPaperFrisbeeGolf/src/Images/Mountains.png'

# CLOUDS
kMinCloudHeight = kAppHeight - (kHorizonHeight + 330)
kCloudVariantCount = 5
kCloudFrequency = 1 / 60 # 1 every 40 steps
kCloudSize = (100, 50)
kMinCloudScale = .7
kMaxCloudScale = 3
kWindSpeed = .2

#Scoring Constants
kScorableHeight = kFrisbeeThrowHeight
kScorableTolerance = 2

# OBSTACLES
kObstacleTypes = ['wall', 'tree']
kSideBuffer = 100
kTreeVariantCount = 2
kWallVariantCount = 1
kTreeBaseSizeMultiplier = 4
kDefaultObstaclePeriod = 200
kMaxWallGap = 2
kMinWallWidth = 100
kMaxWallWidth = kAppHeight / 2
kObstacleThickness = 30
kMinObstacleHeight = 10
kMaxObstacleHeight = 30

# OBSTACLE AESTHETICS
kWallGradientColors = ['peru','sienna','saddleBrown']
kBouncyColor = 'orange'
kBrickTexturePath = 'D://Coding/CMU Classes/15112/SuperPaperFrisbeeGolf/src/Images/Brick.png'