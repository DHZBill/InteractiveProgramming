import pygame
from pygame.locals import QUIT, KEYDOWN
import time
import random
import math
from multiprocessing import Process, Pipe
import track

size = (1080, 720)

class PyGameBrickBreakerView(object):
    """ Provides a view of the brick breaker model in a pygame
        window """
    def __init__(self, model, size):
        """ Initialize with the specified model """
        self.model = model
        self.screen = pygame.display.set_mode(size)


    def draw(self):
        """ Draw the game to the pygame window """
        # draw all the bricks to the screen
        self.screen.fill(pygame.Color('black'))

        text_init = pygame.font.SysFont("UbuntuBold", 100)

        for wall in self.model.walls:
            r = pygame.Rect(wall.left,
                            wall.top,
                            wall.width,
                            wall.height)
            pygame.draw.rect(self.screen, pygame.Color('white'), r)

        for dash in self.model.centerline:
            r = pygame.Rect(dash.left,
                            dash.top,
                            dash.width,
                            dash.height)
            pygame.draw.rect(self.screen, pygame.Color('white'), r)

        pygame.draw.circle(self.screen,
                           pygame.Color('white'),
                           (int(self.model.ball.center_x + 0.5), int(self.model.ball.center_y + 0.5)),
                           self.model.ball.radius)

        if center_parent.recv():

            # get the vertical positions of paddles
            position_1 = center_parent.recv()[1]
            position_2 = center_parent.recv()[3]

            # adjust the position of paddles on pygame window
            self.model.paddle1.top = (position_1-240) * 2 + 350
            self.model.paddle2.top = (position_2-240) * 2 + 350

        # draw paddles at the right positions
        r1 = pygame.Rect(self.model.paddle1.left,
                        self.model.paddle1.top - self.model.paddle1.height/2,
                        self.model.paddle1.width,
                        self.model.paddle1.height)
        r2 = pygame.Rect(self.model.paddle2.left,
                        self.model.paddle2.top - self.model.paddle2.height/2,
                        self.model.paddle2.width,
                        self.model.paddle2.height)
        pygame.draw.rect(self.screen, pygame.Color('orange'), r1)
        pygame.draw.rect(self.screen, pygame.Color('blue'), r2)

        # add scores
        left_score = text_init.render(str(self.model.score.left), 1, (255,255,255))
        self.screen.blit(left_score, (size[0]/2 + 100, 15))

        right_score = text_init.render(str(self.model.score.right), 1, (255,255,255))
        self.screen.blit(right_score, (size[0]/2 - 150, 15))
        
        pygame.display.update()


class BrickBreakerModel(object):
    """ Represents the game state for brick breaker """
    def __init__(self, width, height):
        self.height = height
        self.width = width

        self.MARGIN = 5
        self.WALL_WIDTH = width - self.MARGIN*2
        self.WALL_HEIGHT = 10
        self.GRID_BOTTOM = height/2
        self.BALL_RADIUS = 10
        self.WALL1_TOP = self.MARGIN + 100
        self.WALL2_TOP = height - (self.MARGIN + self.WALL_HEIGHT)
        self.DASH_WIDTH = 10
        self.DASH_HEIGHT = 10

        self.walls = [Wall(self.MARGIN, self.WALL1_TOP, self.WALL_WIDTH, self.WALL_HEIGHT),
                      Wall(self.MARGIN, self.WALL2_TOP, self.WALL_WIDTH, self.WALL_HEIGHT)]

        self.centerline = []
        for top in range(self.WALL1_TOP,
                          self.WALL2_TOP,
                          self.DASH_WIDTH + self.MARGIN):
            self.centerline.append(Dash(width/2-(self.DASH_WIDTH/2), top, self.DASH_WIDTH, self.DASH_HEIGHT))

        self.score = Score(0, 0)

        self.ball = Ball(width/2, (height/2 + self.WALL1_TOP/2), self.BALL_RADIUS)
        self.paddle1 = Paddle(0)
        self.paddle2 = Paddle(width - 15)

    def bounce(self, paddle):
        """ Determine the velocity of ball after collision happens """

        angle = 180 - (self.ball.center_y - paddle.top)/self.paddle1.height*180
        self.ball.velocity_x = abs(math.cos(math.radians(angle)) * self.ball.speed)
        self.ball.velocity_y = abs(math.sin(math.radians(angle)) * self.ball.speed)
        
        # set the minimum speed on x direction
        speed_limit_x = 5
        if self.ball.velocity_x <= speed_limit_x:
            self.ball.velocity_x = speed_limit_x

        if paddle == self.paddle1:
            self.ball.center_x = self.paddle1.left + self.paddle1.width +1
            self.score.right += 1
            print 'paddle1 hit'

        else:
            self.ball.velocity_x = -self.ball.velocity_x
            self.ball.center_x = self.paddle2.left-1
            self.score.left += 1
            print 'paddle2 hit'



    def collision(self):
        """ Detect collisions """
        # set the boundaries in which the ball should bounce back
        boundaryX_1 = (self.paddle1.left + self.paddle1.width/2 - 10, 
                      self.paddle1.left + self.paddle1.width)        
        boundaryX_2 = (self.paddle2.left, 
                      self.paddle2.left + self.paddle2.width/2 + 10)        
        boundaryY_1 = (self.paddle1.top - self.paddle1.height/2, 
                      self.paddle1.top + self.paddle1.height/2)        
        boundaryY_2 = (self.paddle2.top - self.paddle2.height/2, 
                      self.paddle2.top + self.paddle2.height/2)        
        boundary_Wall = (self.WALL1_TOP + self.WALL_HEIGHT, 
                        self.WALL2_TOP - self.WALL_HEIGHT)

        # detect collision between ball and paddles
        if self.ball.center_x >= boundaryX_1[0] and self.ball.center_x <= boundaryX_1[1]:
            if self.ball.center_y >= boundaryY_1[0] and self.ball.center_y <= boundaryY_1[1]:
                self.bounce(self.paddle1)

        elif self.ball.center_x >= boundaryX_2[0] and self.ball.center_x <= boundaryX_2[1]:
            if self.ball.center_y >= boundaryY_2[0]  and self.ball.center_y <= boundaryY_2[1]:
                self.bounce(self.paddle2)
        
        # detect collision between ball and wall
        if self.ball.center_y <= boundary_Wall[0] or self.ball.center_y >= boundary_Wall[1]:
            self.ball.velocity_y = -self.ball.velocity_y

    def update(self):
        """ Update the model state """
        self.collision()
        self.ball.update()


class Paddle(object):
    """ Represents the paddle in the game """
    def __init__(self,left):
        self.left = left
        self.top = 0
        self.width = 10
        self.height = 100


class Ball(object):
    """ Represents a ball in my pong game """
    def __init__(self, center_x, center_y, radius):
        """ Create a ball object with the specified geometry """
        self.center_x = center_x
        self.center_y = center_y

        self.radius = radius
        self.velocity_x = random.choice([20,-20])         # pixels / frame
        self.velocity_y = 0         # pixels / frame
        self.speed = math.sqrt(self.velocity_x **2 + self.velocity_y **2)

    def update(self):
        """ Update the position of the ball due to time passing """ 
        self.center_x += self.velocity_x
        self.center_y += self.velocity_y


class Wall(object):
    """ Represents a wall in my pong game """
    def __init__(self, left, top, width, height):
        """ Initializes a Wall object with the specified
            geometry and color """
        self.left = left
        self.top = top
        self.width = width
        self.height = height


class Dash(object):            # adjust the position of paddles on pygame window

    """ Represents a dash in my pong game """
    def __init__(self, left, top, width, height):
        """ Initializes a Dash object with the specified
            geometry and color """
        self.left = left
        self.top = top
        self.width = width
        self.height = height


class Score(object):
    """ Represents the score in my pong game """
    def __init__(self, left, right):
        """ Initializes a Score object with the specified
            left and right values """
        self.left = left
        self.right = right            # adjust the position of paddles on pygame window



def run(center_parent):
    pygame.init()
    model = BrickBreakerModel(size[0], size[1])
    view = PyGameBrickBreakerView(model, size)
    running = True
    while running:
        model.update()
        view.draw()

if __name__ == '__main__':
    
    size = (1080, 720)
    center_parent, center_child = Pipe()
    q = Process(target=track.Tracking, args=(center_child,))
    p = Process(target=run, args=(center_parent,))
    
    q.start()
    p.start()
    q.join()
    p.join()

    
