import pygame as pg
from dataclasses import dataclass
import random
from copy import deepcopy

pg.init()
pg.font.init()

gameOverFont = pg.font.Font(pg.font.get_default_font(), 24)
scoreFont = pg.font.Font(pg.font.get_default_font(), 18)

windowWidth = 1200
windowHeight = 650

cellSize = 25
maxCellX = windowWidth // cellSize - 1
maxCellY = windowHeight // cellSize - 1

screen = pg.display.set_mode((windowWidth, windowHeight))
pg.display.set_caption('Snake')
clock = pg.time.Clock()

# https://html-color.codes/
@dataclass(frozen=True)
class Colours:
    black: tuple = (27,27,27)
    white: tuple = (245,245,245)
    green: tuple = (50,205,50)
    crimson: tuple = (220,20,60)
    blue: tuple = (65,105,225)
colours = Colours()

def cellPixelPosition(cellX, cellY):
    # Keep cells within grid on screen
    # If out of bounds clamp to either 0 or the final 
    cellX = max(0, min(cellX, maxCellX))
    cellY = max(0, min(cellY, maxCellY))

    # Convert cell co-ordinates to pixel co-ordinates
    pixelX = cellX * cellSize
    pixelY = cellY * cellSize

    return pixelX, pixelY

snakeDimension = cellSize
snakeDirection = None
snakeBodyCell = [
    [3, maxCellY // 2]
]
snakeBodyPixel = [
    list(cellPixelPosition(snakeBodyCell[0][0], snakeBodyCell[0][1]))
]
snakeBodyCurrentPixel = [
    list(snakeBodyPixel[0])
]
snakeBodyTargetPixel = [
    list(snakeBodyPixel[0])
]

# print('snakeBodyCell: ' + str(snakeBodyCell))
# print('snakeBodyPixel: ' + str(snakeBodyPixel))
# print('snakeBodyCurrentPixel: ' + str(snakeBodyCurrentPixel))
# print('snakeBodyTargetPixel: ' + str(snakeBodyTargetPixel))

appleDimnension = cellSize
applePadding = 100

def generateApplePos():
    regenerate = True
    while regenerate:
        # Generate random cell to put apple in
        appleCellX = random.randint(0, (maxCellX))
        appleCellY = random.randint(0, (maxCellY))

        applePixelX, applePixelY = cellPixelPosition(appleCellX, appleCellY)

        # Check if new apple generates inside snake
        if [appleCellX, appleCellY] in snakeBodyCell:
            continue
        else:
            regenerate = False
            print('Apple X: ' + str(applePixelX) + ' Apple Y: ' + str(applePixelY) + ' Apple Cell X: ' + str(appleCellX) + ' Apple Cell Y: ' + str(appleCellY))

    return applePixelX, applePixelY, appleCellX, appleCellY

applePixelX, applePixelY, appleCellX, appleCellY = generateApplePos()

score = 0

runGameLogic = True

lastMoveTime = 0
moveInterval = 100 #In milliseconds
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT and snakeDirection != 'RIGHT':
                     snakeDirection = 'LEFT'
                elif event.key == pg.K_UP and snakeDirection != 'DOWN':
                     snakeDirection = 'UP'
                elif event.key == pg.K_RIGHT and snakeDirection != 'LEFT':
                     snakeDirection = 'RIGHT'
                elif event.key == pg.K_DOWN and snakeDirection != 'UP':
                     snakeDirection = 'DOWN'

                if event.key == pg.K_SPACE and runGameLogic == False:
                    # Completely ignoring DRY for now
                    snakeDirection = None
                    snakeBodyCell = [
                        [3, maxCellY // 2]
                    ]
                    snakeBodyPixel = [
                        list(cellPixelPosition(snakeBodyCell[0][0], snakeBodyCell[0][1]))
                    ]
                    snakeBodyCurrentPixel = [
                        list(snakeBodyPixel[0])
                    ]
                    snakeBodyTargetPixel = [
                        list(snakeBodyPixel[0])
                    ]

                    applePixelX, applePixelY, appleCellX, appleCellY = generateApplePos()
                    score = 0
                    runGameLogic = True
                    continue

    if runGameLogic:
        # Game playing
        screen.fill(colours.black)

        # Detatch snake movement from frame rate
        currentTime = pg.time.get_ticks()
        if currentTime - lastMoveTime >= moveInterval:
            for currentBodyPixel, targetBodyPixel in zip(snakeBodyCurrentPixel, snakeBodyTargetPixel):
                    currentBodyPixel[0] = targetBodyPixel[0] # x
                    currentBodyPixel[1] = targetBodyPixel[1] # y

            # Change direction
            if snakeDirection == 'LEFT':
                # Clone snakeBodyCell so we have a list to copy old values from
                snakeBodyCellCopy = deepcopy(snakeBodyCell)

                # Update the head
                snakeBodyCell[0][0] -= 1

                # Update the body
                for i in range(1, len(snakeBodyCell)):
                    snakeBodyCell[i] = snakeBodyCellCopy[i - 1].copy()

                # print('snakeBodyCell: ' + str(snakeBodyCell) + ' snakeBodyCellCopy: ' + str(snakeBodyCellCopy))
            elif snakeDirection == 'UP':
                snakeBodyCellCopy = deepcopy(snakeBodyCell)
                snakeBodyCell[0][1] -= 1
                for i in range(1, len(snakeBodyCell)):
                    snakeBodyCell[i] = snakeBodyCellCopy[i - 1].copy()
            elif snakeDirection == 'RIGHT':
                snakeBodyCellCopy = deepcopy(snakeBodyCell)
                snakeBodyCell[0][0] += 1
                for i in range(1, len(snakeBodyCell)):
                    snakeBodyCell[i] = snakeBodyCellCopy[i - 1].copy()
            elif snakeDirection == 'DOWN':
                snakeBodyCellCopy = deepcopy(snakeBodyCell)
                snakeBodyCell[0][1] += 1
                for i in range(1, len(snakeBodyCell)):
                    snakeBodyCell[i] = snakeBodyCellCopy[i - 1].copy()

            # Check if snake collides with borders
            if snakeBodyCell[0][0] < 0 or snakeBodyCell[0][0] > maxCellX or \
            snakeBodyCell[0][1] < 0 or snakeBodyCell[0][1] > maxCellY:
                runGameLogic = False
                continue

            # Check if snake collides with its body
            if len(snakeBodyCell) >= 2:
                snakeHeadCell = snakeBodyCell[0]
                if snakeHeadCell in snakeBodyCell[1:len(snakeBodyCell)]:
                    runGameLogic = False
                    continue

            # Calculate new location of snake
            for bodyPart, targetPixel in zip(snakeBodyCell, snakeBodyTargetPixel):
                targetPixel[0], targetPixel[1] = cellPixelPosition(bodyPart[0], bodyPart[1])

            # Check if snake eats apple
            if snakeBodyCell[0][0] == appleCellX and snakeBodyCell[0][1] == appleCellY:
                score += 1
                print("Score: " + str(score))

                # Get base value for new body part
                positionCell = snakeBodyCell[-1].copy()
                positionPixel = snakeBodyPixel[-1].copy()
                positionCurrentPixel = snakeBodyCurrentPixel[-1].copy()
                positionTargetPixel = snakeBodyTargetPixel[-1].copy()

                # Calculate cell and pixels for new body part and account for direction
                if snakeDirection == 'LEFT' and len(snakeBodyCell)  == 1:
                    positionCell[0] += 1
                    positionPixel[0] += cellSize
                    positionCurrentPixel[0] += cellSize                     
                elif snakeDirection == 'UP' and len(snakeBodyCell)  == 1:
                    positionCell[1] -= 1
                    positionPixel[1] -= cellSize
                    positionCurrentPixel[1] -= cellSize 
                elif snakeDirection == 'RIGHT' and len(snakeBodyCell)  == 1:
                    positionCell[0] -= 1
                    positionPixel[0] -= cellSize
                    positionCurrentPixel[0] -= cellSize  
                elif snakeDirection == 'DOWN' and len(snakeBodyCell)  == 1:
                    positionCell[1] += 1
                    positionPixel[1] += cellSize
                    positionCurrentPixel[1] += cellSize
                else:
                    # Snake has body components to compare direction
                    travelRefBodyCell = snakeBodyCell[-2].copy()
                    deltaX = travelRefBodyCell[0] - positionCell[0]
                    deltaY = travelRefBodyCell[1] - positionCell[1]

                    if deltaY == -1:
                        # Up
                        positionCell[1] -= 1
                        positionPixel[1] -= cellSize
                        positionCurrentPixel[1] -= cellSize
                    elif deltaY == 1:
                        # Down
                        positionCell[1] += 1
                        positionPixel[1] += cellSize
                        positionCurrentPixel[1] += cellSize
                    elif deltaX == 1:
                        # Left
                        positionCell[0] += 1
                        positionPixel[0] += cellSize
                        positionCurrentPixel[0] += cellSize     
                    elif deltaX == -1:
                        # Right
                        positionCell[0] -= 1
                        positionPixel[0] -= cellSize
                        positionCurrentPixel[0] -= cellSize  
                        
                # Attach new body part to snake
                snakeBodyCell.insert(len(snakeBodyCell), positionCell)
                snakeBodyPixel.insert(len(snakeBodyPixel), positionPixel)
                snakeBodyCurrentPixel.insert(len(snakeBodyCurrentPixel), positionCurrentPixel)
                snakeBodyTargetPixel.insert(len(snakeBodyTargetPixel), positionTargetPixel)

                applePixelX, applePixelY, appleCellX, appleCellY = generateApplePos()

            lastMoveTime = currentTime

        # Calculate how complete the animation is
        animationProgress = (currentTime - lastMoveTime) / moveInterval
        animationProgress = min(1.0, animationProgress)

        # Calculate new pixel position using linear interpolation
        for bodyPixel, targetPixel, currentPixel in zip(snakeBodyPixel, snakeBodyTargetPixel, snakeBodyCurrentPixel):
            bodyPixel[0] = currentPixel[0] + (targetPixel[0] - currentPixel[0]) * animationProgress
            bodyPixel[1] = currentPixel[1] + (targetPixel[1] - currentPixel[1]) * animationProgress

        pg.draw.rect(screen, colours.crimson, (applePixelX, applePixelY, appleDimnension, appleDimnension)) # Render apple

        for bodyPixels in snakeBodyPixel:
            pg.draw.rect(screen, colours.green, (bodyPixels[0], bodyPixels[1], snakeDimension, snakeDimension)) # Render snake

        # Score text
        scoreMarginPixelX, scoreMarginPixelY = 15, 15

        # Render 'Score: '
        scoreTextSurface = scoreFont.render('Score: ', True, colours.white)
        screen.blit(scoreTextSurface, (scoreMarginPixelX, scoreMarginPixelY))

        # Render score number
        scoreNumTextSurface = scoreFont.render(str(score), True, colours.blue)
        scoreNumPixelX = scoreMarginPixelX + scoreTextSurface.get_width()
        scoreNumPixelY = scoreMarginPixelY
        screen.blit(scoreNumTextSurface, (scoreNumPixelX, scoreNumPixelY))
    
    if not runGameLogic:
        # Game over
        screen.fill(colours.black)

        # Render 'Game Over' 
        gameOverTextSurface = gameOverFont.render('Game Over', True, colours.white)
        gameOverTextPixelX = windowWidth // 2 - gameOverTextSurface.get_width() // 2
        gameOverTextPixelY = 0 + windowHeight * 0.15 
        screen.blit(gameOverTextSurface, (gameOverTextPixelX, gameOverTextPixelY))

        # Render press INPUT to replay with INPUT in crimson
        pressTextSurface = gameOverFont.render('Press ', True, colours.white)
        spaceTextSurface = gameOverFont.render('space ', True, colours.crimson)
        replayTextSurface = gameOverFont.render('to replay...', True, colours.white)

        pressToReplayTextPixelY = windowHeight // 2 - pressTextSurface.get_height() // 2

        pressTextPixelX = windowWidth // 2 - (pressTextSurface.get_width() + spaceTextSurface.get_width() + replayTextSurface.get_width()) // 2
        spaceTextPixelX = windowWidth // 2 - ((pressTextSurface.get_width() + spaceTextSurface.get_width() + replayTextSurface.get_width()) // 2) \
                                                + pressTextSurface.get_width()
        replayTextPixelX = windowWidth // 2 - ((pressTextSurface.get_width() + spaceTextSurface.get_width() + replayTextSurface.get_width()) // 2) \
                                                + pressTextSurface.get_width() + spaceTextSurface.get_width()

        screen.blit(pressTextSurface, (pressTextPixelX, pressToReplayTextPixelY))
        screen.blit(spaceTextSurface, (spaceTextPixelX, pressToReplayTextPixelY))
        screen.blit(replayTextSurface, (replayTextPixelX, pressToReplayTextPixelY))

        # Render score
        scoreTextSurface = gameOverFont.render('Your Score: ', True, colours.white)
        scoreNumTextSurface = gameOverFont.render(str(score), True, colours.blue)

        scoreTextPixelY = 0 + windowHeight * 0.75

        scoreTextPixelX = windowWidth // 2 - (scoreTextSurface.get_width() + scoreNumTextSurface.get_width()) // 2
        scoreNumTextPixelX = windowWidth // 2 - ((scoreTextSurface.get_width() + scoreNumTextSurface.get_width()) // 2) \
                                                + scoreTextSurface.get_width()
        
        screen.blit(scoreTextSurface, (scoreTextPixelX, scoreTextPixelY))
        screen.blit(scoreNumTextSurface, (scoreNumTextPixelX, scoreTextPixelY))
    
    pg.display.update()
    clock.tick(100)

pg.font.quit()
pg.quit()