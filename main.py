import pygame as pg
from dataclasses import dataclass, replace
import random

pg.init()
pg.font.init()

windowWidth = 1200
windowHeight = 650

cellSize = 25
maxCellX = windowWidth // cellSize - 1
maxCellY = windowHeight // cellSize - 1

screen = pg.display.set_mode((windowWidth, windowHeight))
pg.display.set_caption('Snake')
clock = pg.time.Clock()

gameOverFont = pg.font.Font(pg.font.get_default_font(), 24)
scoreFont = pg.font.Font(pg.font.get_default_font(), 18)

def cellPixelPosition(cellX, cellY):
    # Keep cells within grid on screen
    # If out of bounds clamp to either 0 or the final 
    cellX = max(0, min(cellX, maxCellX))
    cellY = max(0, min(cellY, maxCellY))

    # Convert cell co-ordinates to pixel co-ordinates
    pixelX = cellX * cellSize
    pixelY = cellY * cellSize

    return pixelX, pixelY

# https://html-color.codes/
@dataclass(frozen=True)
class Colours:
    black: tuple = (27,27,27)
    white: tuple = (245,245,245)
    green: tuple = (50,205,50)
    crimson: tuple = (220,20,60)
    blue: tuple = (65,105,225)

@dataclass
class Position:
    x: int
    y: int

@dataclass(frozen=True)
class Direction:
    cellX: int
    cellY: int
    pixelX: int
    pixelY: int

class Directions:
    LEFT = Direction(-1, 0, -cellSize, 0)
    UP = Direction(0, -1, 0, -cellSize)
    RIGHT = Direction(1, 0, cellSize, 0)
    DOWN = Direction(0, 1, 0, cellSize)

class Snake:
    def __init__(self, cellSize, maxCellX, maxCellY):
        self.cellSize = cellSize # Dimension
        self.direction = None

        self.maxCellX = maxCellX
        self.maxCellY = maxCellY

        startingCell = Position(20, self.maxCellY // 2)
        pixelX, pixelY = cellPixelPosition(startingCell.x, startingCell.y)

        self.cells = [startingCell] # Grid coordinates (snakeBodyCell)
        self.renderPositionPixels = [Position(pixelX, pixelY)] # Rendered position this frame (snakeBodyPixel)
        self.currentPositionPixels = [Position(pixelX, pixelY)] # Starting position (snakeBodyCurrentPixel)
        self.targetPositionPixels = [Position(pixelX, pixelY)] # Destination position (snakeBodyTargetPixel)

    def changeDirection(self, inputDirection):
        direction = getattr(Directions, inputDirection)

        # Calculate new position of the top of the snake
        oldheadCell = self.cells[0]
        newHeadCellX = oldheadCell.x + direction.cellX
        newHeadCellY = oldheadCell.y + direction.cellY
        newHeadCell = Position(newHeadCellX, newHeadCellY)

        # Update the cells the snake occupies to move it
        self.cells.insert(0, newHeadCell)
        self.cells.pop(-1)
        
        return

    def checkBodyCollision(self, snakeHead):
        # Checks if snake head collides with its body and returns True/False if a collission occurs
        if len(self.cells) > 1:
            snakeHead = self.cells[0]
            if snakeHead in self.cells[1:len(self.cells)]:
                return True
            else:
                return False
        return False

    def checkBorderCollision(self, snakeHead):
        # Check if the snake collides with the border and returns True/False if a collisison occurs
        if snakeHead.x < 0 or snakeHead.x > self.maxCellX or \
           snakeHead.y < 0 or snakeHead.y > self.maxCellY:
            return True
        else:
            return False

    def checkAppleCollision(self, snakeHead, appleCell):
        if snakeHead == appleCell:
            self.grow()
            return True
        return False

    def grow(self):
        print('the snake is growing :/')
        direction = getattr(Directions, self.direction)

        # Select the current tail of the snake to clone
        cell = replace(self.cells[-1])
        renderPositionPixel = replace(self.renderPositionPixels[-1])
        currentPositionPixel = replace(self.currentPositionPixels[-1])
        targetPositionPixel = replace(self.targetPositionPixels[-1])

        if len(self.cells) == 1:
            # Calculate where the tail should be placed relative to the head
            cell = Position(cell.x - direction.cellX, cell.y - direction.cellY)
            renderPositionPixel = Position(renderPositionPixel.x - direction.pixelX, renderPositionPixel.y - direction.pixelY)
            currentPositionPixel = Position(currentPositionPixel.x - direction.pixelX, currentPositionPixel.y - direction.pixelY)
            targetPositionPixel = Position(targetPositionPixel.x - direction.pixelX, targetPositionPixel.y - direction.pixelY)
        else:
            # Calculate the direction of the tail
            comparisonCell = self.cells[-2]
            deltaCellX = cell.x - comparisonCell.x
            deltaCellY = cell.y - comparisonCell.y
            deltaPixelX = deltaCellX * self.cellSize
            deltaPixelY = deltaCellY * self.cellSize

            # Calculate where the tail should be placed
            cell = Position(cell.x + deltaCellX, cell.y + deltaCellY)
            renderPositionPixel = Position(renderPositionPixel.x + deltaPixelX, renderPositionPixel.y + deltaPixelY)
            currentPositionPixel = Position(currentPositionPixel.x + deltaPixelX, currentPositionPixel.y + deltaPixelY)
            targetPositionPixel = Position(targetPositionPixel.x + deltaPixelX, targetPositionPixel.y + deltaPixelY)

        self.cells.append(cell)
        self.renderPositionPixels.append(renderPositionPixel)
        self.currentPositionPixels.append(currentPositionPixel)
        self.targetPositionPixels.append(targetPositionPixel)

    def mapTargetPixels(self):
        # Map cell grid coordinates to pixel coordinates
        for bodyPart, targetPixel in zip(self.cells, self.targetPositionPixels):
            targetPixel.x, targetPixel.y = cellPixelPosition(bodyPart.x, bodyPart.y)

    def lerp(self, currentTick, tickEpoch, tickRate):
        # Calculate frame delta
        frameDeltaTime = (currentTick - tickEpoch) / tickRate
        frameProgress = min(1.0, frameDeltaTime)

        # Calculate where to render pixels using linear interpolation/LERP
        for renderPositionPixel, targetPositionPixel, currentPositionPixel in zip(self.renderPositionPixels, self.targetPositionPixels, self.currentPositionPixels):
            renderPositionPixel.x = currentPositionPixel.x + (targetPositionPixel.x - currentPositionPixel.x) * frameProgress
            renderPositionPixel.y = currentPositionPixel.y + (targetPositionPixel.y - currentPositionPixel.y) * frameProgress

        return frameProgress

class Apple:
    def __init__(self, cellSize, maxCellX, maxCellY, snakeCells):
        self.maxCellX = maxCellX
        self.maxCellY = maxCellY

        self.cellSize = cellSize
        self.cell = None 
        self.pixel = None
        
        self.generateApple(snakeCells)

    def generateApple(self, snakeCells):
        # Keep generating random cells for apple until it's not inside of snakes current position
        while True:
            cellX = random.randint(0, (self.maxCellX))
            cellY = random.randint(0, (self.maxCellY))
            cell = Position(cellX, cellY)

            if cell not in snakeCells:
                break

        pixel = Position(*cellPixelPosition(cellX, cellY))

        self.cell, self.pixel = cell, pixel
        return cell, pixel

def initGame(cellSize, maxCellX, maxCellY):
    colours = Colours()
    snake = Snake(cellSize, maxCellX, maxCellY)
    apple = Apple(cellSize, maxCellX, maxCellY, snake.cells)

    score = 0
    runGameLogic = True

    return colours, snake, apple, score, runGameLogic

colours, snake, apple, score, runGameLogic = initGame(cellSize, maxCellX, maxCellY)

tickEpoch = 0
tickRate = 100
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT and snake.direction != 'RIGHT':
                     snake.direction = 'LEFT'
                elif event.key == pg.K_UP and snake.direction != 'DOWN':
                     snake.direction = 'UP'
                elif event.key == pg.K_RIGHT and snake.direction != 'LEFT':
                     snake.direction = 'RIGHT'
                elif event.key == pg.K_DOWN and snake.direction != 'UP':
                     snake.direction = 'DOWN'

                if event.key == pg.K_SPACE and runGameLogic == False:
                    # Restart game
                    colours, snake, apple, score, runGameLogic = initGame(cellSize, maxCellX, maxCellY)
                    continue

    if runGameLogic:
        # Game playing
        screen.fill(colours.black)

        # Detatch snake movement from frame rate
        currentTick = pg.time.get_ticks()
        deltaTime = currentTick - tickEpoch
        while deltaTime >= tickRate:
            # Update the current position
            for currentPixel, targetPixel in zip(snake.currentPositionPixels, snake.targetPositionPixels):
                    currentPixel.x, currentPixel.y = targetPixel.x, targetPixel.y

            # Change direction
            if snake.direction != None:
                snake.changeDirection(snake.direction)

            snakeHead = snake.cells[0]

            # Check for collisions & update game state
            if snake.checkBodyCollision(snakeHead):
                runGameLogic = False
                tickEpoch = 0
                deltaTime -= tickRate 
                break

            if snake.checkBorderCollision(snakeHead):
                runGameLogic = False
                tickEpoch = 0
                deltaTime -= tickRate 
                break

            if snake.checkAppleCollision(snakeHead, apple.cell):
                score += 1 
                apple.generateApple(snake.cells)

            # Update snake.targetPositionPixels
            snake.mapTargetPixels() 

            # Preserve time accuracy & update epoch
            tickEpoch += tickRate
            deltaTime -= tickRate 

        # Calculate how complete the animation is
        snake.lerp(currentTick, tickEpoch, tickRate)

        for renderPositionPixel in snake.renderPositionPixels:
            pg.draw.rect(screen, colours.green, (renderPositionPixel.x, renderPositionPixel.y, snake.cellSize, snake.cellSize)) # Render snake

        pg.draw.rect(screen, colours.crimson, (apple.pixel.x, apple.pixel.y, apple.cellSize, apple.cellSize)) # Render apple

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