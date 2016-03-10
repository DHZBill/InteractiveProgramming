import pygame
from pygame.locals import QUIT, KEYDOWN
import time
import random
import math
from multiprocessing import Process, Pipe
import track

""" Questions/Commentary Section """
# weird bug in scoring system that makes the first bounce count for 2 pts
# haven't looked into it yet ...

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

        # left_score = text_init.render(str(self.model.score.left), 1, (255,255,255))
        # self.screen.blit(left_score, (size[0]/2 + 100, 15))

        # right_score = text_init.render(str(self.model.score.right), 1, (255,255,255))
        # self.screen.blit(right_score, (size[0]/2 - 150, 15))

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

        if center_parent.recv() != None:

            self.model.paddle1.top = (center_parent.recv()[1]-240) * 2 +240 +100
            self.model.paddle2.top = (center_parent.recv()[3]-240) * 2 +240 +100


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


        left_score = text_init.render(str(self.model.score.left), 1, (255,255,255))
        self.screen.blit(left_score, (size[0]/2 + 100, 15))

        right_score = text_init.render(str(self.model.score.right), 1, (255,255,255))
        self.screen.blit(right_score, (size[0]/2 - 150, 15))

        # if self.ball.center_x <=1 or self.ball.center_x >= self.paddle2.left + 10:
        #     self.score.right += 1 



        
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
        self.paddle1 = Paddle(5, (height/2 + self.WALL1_TOP/2))
        self.paddle2 = Paddle(width - 15, (height/2 + self.WALL1_TOP/2))

    def collision(self):

        if self.ball.center_x <= self.paddle1.left + self.paddle1.width and self.ball.center_x >= self.paddle1.left + self.paddle1.width/2 - 10:
            if self.ball.center_y >= self.paddle1.top - self.paddle1.height/2 and self.ball.center_y <= self.paddle1.top + self.paddle1.height/2:
                n = 180 - (self.ball.center_y - (self.paddle1.top))/self.paddle1.height*180
                self.bounce(n)
                if self.ball.velocity_x <= 5:
                    self.ball.velocity_x = 5
                print 'panel1 hit'
                self.ball.center_x = self.paddle1.left + self.paddle1.width +1

                self.score.right += 1

        elif self.ball.center_x >= self.paddle2.left and self.ball.center_x <= self.paddle2.left + self.paddle2.width/2 + 10:
            if self.ball.center_y >= self.paddle2.top - self.paddle2.height/2  and self.ball.center_y <= self.paddle2.top + self.paddle2.height/2:
                n = 180 - (self.ball.center_y - (self.paddle2.top))/self.paddle2.height*180
                self.bounce(n)
                if self.ball.velocity_x <= 5:
                    self.ball.velocity_x = 5
                self.ball.velocity_x = -self.ball.velocity_x
                print self.score.left
                print 'panel2 hit', self.ball.center_y, (self.paddle2.top)
                self.ball.center_x = self.paddle2.left-1
                self.score.left += 1



        if self.ball.center_y <= (self.WALL1_TOP + self.WALL_HEIGHT) or self.ball.center_y >= self.WALL2_TOP:
            self.ball.velocity_y = -self.ball.velocity_y


    def bounce(self, n):
        
        self.ball.velocity_x = abs(math.cos(math.radians(n)) * self.ball.speed)
        self.ball.velocity_y = abs(math.sin(math.radians(n)) * self.ball.speed)

    def update(self):
        """ Update the model state """
        self.collision()
        self.ball.update()


class Paddle(object):
    """ Represents the paddle in the game """
    def __init__(self, left, top):
        self.left = left
        self.top = top
        self.width = 10
        self.height = 100



class Ball(object):
    """ Represents a ball in my pong game """
    def __init__(self, center_x, center_y, radius):
        """ Create a ball object with the specified geometry """
        self.center_x = center_x
        self.center_y = center_y

        self.radius = radius
        self.velocity_x = random.choice([10,-10])         # pixels / frame
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
        #self.color = color

class Dash(object):
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
        self.right = right

class PyGameKeyboardController(object):
    def __init__(self, model, size):
        self.model = model



    
    def handle_event(self,event):
        keystate = pygame.key.get_pressed()
        jump = 20
        margin = 50
        upper_wall = 110

        """ Looks for w & s keypresses to move the y position of Paddle 1
        if Paddle is in range of board""" 
        if event.type != KEYDOWN:
            return
        if event.key == pygame.K_w:
            if jump+margin + upper_wall < self.model.paddle1.top:
                self.model.paddle1.top -= jump
            else:
                return
        if event.key == pygame.K_s:
            if self.model.paddle1.top < size[1] - (jump + margin + 10):
                self.model.paddle1.top -= -jump
            else:
                return


        """ Looks for UP & DOWN keypresses to move the y position of Paddle 2
        if Paddle is in range of board"""
        if event.type != KEYDOWN:
            return
        if event.key == pygame.K_UP:
            if jump + margin + upper_wall < self.model.paddle2.top:
                self.model.paddle2.top -= jump
            else:
                return
        if event.key == pygame.K_DOWN:
            if self.model.paddle2.top < size[1] - (jump + margin + 10):
                self.model.paddle2.top -= -jump
            else:
                return
def run(center_parent):
    pygame.init()
    model = BrickBreakerModel(size[0], size[1])
    view = PyGameBrickBreakerView(model, size)
    controller = PyGameKeyboardController(model, size)
    running = True
    while running:
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                controller.handle_event(event)
        model.update()
        view.draw()
        # print center_parent.recv()
        # print model.paddle2.top
        # print model.ball.center_y
        # print model.ball.velocity_x
        # time.sleep(0.001)
if __name__ == '__main__':
    # pygame.init()
    # size = (1080, 720)

    # model = BrickBreakerModel(size[0], size[1])
    # view = PyGameBrickBreakerView(model, size)
    # controller = PyGameKeyboardController(model, size)
    center_parent, center_child = Pipe()
    q = Process(target=track.Tracking, args=(center_child,))
    p = Process(target=run, args=(center_parent,))
    
    q.start()
    p.start()
    q.join()
    p.join()

    
