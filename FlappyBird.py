"""
The classic game of flappy bird. Make with python and pygame.
Date Modified:  Nov 27, 2021
"""
import os
import sys
import pygame
import logging
from random import randrange
from pygame import mixer


# initialize pygame
pygame.init()

# Font
score_font = pygame.font.SysFont("Arial", 30)
gameover_font = pygame.font.SysFont("Arial", 1000, bold=True)

# set window size
# To the Left (x-axis) of windows is negative
# To the Bottom (y-axis) of windows is positive
X_WIDTH = 500
Y_HEIGHT = 800
COLORBLACK = (0, 0, 0)
COLORWHITE = (255, 255, 255)

# frames per second setting
FPS = 30

# velocity / speed of movement
VEL = 5

# create the display surface object
screen = pygame.display.set_mode((X_WIDTH, Y_HEIGHT))
# set the pygame window name
pygame.display.set_caption("Testing Flappy Bird")

# create a surface object, image is drawn on it. Transform to scale it to Window size
bkgnd_img = pygame.image.load("imgs/bkgnd_img.png")
bkgnd_img = pygame.transform.scale(bkgnd_img, (X_WIDTH, Y_HEIGHT))
platform_img = pygame.image.load("imgs/platform_img.png").convert_alpha()
platform_img = pygame.transform.scale(platform_img, (X_WIDTH, 100))
pipe_img = pygame.image.load("imgs/pipe_img.png")
pipe_img = pygame.transform.scale2x(pipe_img)
pipe_img_flip = pygame.transform.flip(pipe_img, False, True)
bird_imgs = [pygame.image.load("imgs/bird1_img.png"), pygame.image.load("imgs/bird2_img.png"), pygame.image.load("imgs/bird2_img.png")]

# Music
pygame.mixer.init()

# Logging level
logging.basicConfig(level=logging.DEBUG)
#logging.debug("draw {}, {}".format(self.x, self.y))


class Bird():
    def __init__(self):
        self.x = 200
        self.y = 200
        self.y_change = 0
        self.angle = 45
        self.bird_img = bird_imgs[0]
        self.bird_tiltup_img = bird_imgs[0]
        self.masking = pygame.mask.from_surface(self.bird_img)

    def jump(self):
        ''' Tilt up and jump, y towards negative value
        :return: None
        '''
        self.y_change = self.y
        self.y = self.y - 100

        add_sound = pygame.mixer.Sound('sound/jump.wav')
        add_sound.play()

    def gravity(self):
        ''' tilt down, object is going down by y-value
        :return: None
        '''
        self.y_change = self.y
        self.y = self.y + 5

    def draw(self):
        ''' Draw the bird on the window
        :return: None
        '''
        # Animate the bird's flying
        if self.bird_img == bird_imgs[0]:
            self.bird_img = bird_imgs[1]
        elif self.bird_img == bird_imgs[1]:
            self.bird_img = bird_imgs[2]
        elif self.bird_img == bird_imgs[2]:
            self.bird_img = bird_imgs[0]

        # if y axis go up, tilt up and jump, else tilt down
        if self.y_change > self.y:      # tilt up
            self.bird_tiltup_img = pygame.transform.rotate(self.bird_img, self.angle)
            screen.blit(self.bird_tiltup_img, (self.x, self.y))
        elif self.y_change < self.y:      # tilt down
            screen.blit(self.bird_img, (self.x, self.y))

    def bird_masking(self):
        ''' Get masking of the bird
        :return: mask data
        '''
        self.masking = pygame.mask.from_surface(self.bird_img)
        return self.masking

    def bird_collide(self, state):
        ''' if collide, bird will keep rotate
        :return: None
        '''
        # if collide, bird will rotate 90 deg and falling down
        if state:
            self.bird_img = pygame.transform.rotate(self.bird_img, -90)
            self.y = self.y + 5

class Pipe():
    # distance between pipe
    GAP = 200
    BETWEENPIPE = 400

    def __init__(self):
        self.x = []
        self.y = []
        self.x.append(500)
        self.x.append(self.x[0] + self.BETWEENPIPE)
        self.x.append(self.x[1] + self.BETWEENPIPE)
        self.y.append(randrange(-500,-300))
        self.y.append(randrange(-500,-300))
        self.y.append(randrange(-500,-300))
        self.height = 0

    def move(self):
        ''' Move the pipe with constant velocity
        :return: None
        '''
        # Move pipe to the left
        self.x[0] -= VEL
        self.x[1] -= VEL
        self.x[2] -= VEL

        # get the height of the pipe [bottom = height]
        pipe_img_rect = pipe_img.get_rect()
        self.height = pipe_img_rect.bottom

        # if pipe goes off from the window, it will alternate between 3 pipes to display
        if self.x[0] < -pipe_img_rect.right:
            self.x[0] = self.x[2] + self.BETWEENPIPE
            self.y[0] = randrange(-500, -300)
        elif self.x[1] < -pipe_img_rect.right:
            self.x[1] = self.x[0] + self.BETWEENPIPE
            self.y[1] = randrange(-500, -300)
        elif self.x[2] < -pipe_img_rect.right:
            self.x[2] = self.x[1] + self.BETWEENPIPE
            self.y[2] = randrange(-500, -300)

    def draw(self):
        ''' Draw the pipe on the window
        :return: None
        '''
        # Draw new pipe based on the distance between pipe
        screen.blit(pipe_img, (self.x[0], self.y[0] + self.height + self.GAP))  # bottom
        pipe_img_flip = pygame.transform.flip(pipe_img, False, True)            # top
        screen.blit(pipe_img_flip, (self.x[0], self.y[0]))                      # top
        screen.blit(pipe_img, (self.x[1], self.y[1] + self.height + self.GAP))
        pipe_img_flip = pygame.transform.flip(pipe_img, False, True)
        screen.blit(pipe_img_flip, (self.x[1], self.y[1]))
        screen.blit(pipe_img, (self.x[2], self.y[2] + self.height + self.GAP))
        pipe_img_flip = pygame.transform.flip(pipe_img, False, True)
        screen.blit(pipe_img_flip, (self.x[2], self.y[2]))

    def collision(self, number):
        ''' Masking of the pipe and check collision with the bird
        number: pipe number to check collision
        :return: bool
        '''
        top_pipe_masking = pygame.mask.from_surface(pipe_img)
        bottom_pipe_masking = pygame.mask.from_surface(pipe_img_flip)
        i = number

        # offset is the distance between top pipe and top bird, also between bottom pipe and bottom bird
        # top is top pipe y coordinate
        # bottom is bottom pipe y coordinate
        top = self.y[i]
        bottom = self.y[i] + self.height + self.GAP
        top_offset = (self.x[i] - cBird.x, top - round(cBird.y))
        bottom_offset = (self.x[i] - cBird.x, bottom - round(cBird.y))

        if cBird.bird_masking().overlap(top_pipe_masking, top_offset):
            return True
        if cBird.bird_masking().overlap(bottom_pipe_masking, bottom_offset):
            return True
        return False

class Platform():
    def __init__(self):
        self.x = 0
        self.y = 700

    def move(self):
        ''' Move the platform with constant velocity
        :return: None
        '''
        # move to the left
        self.x -= VEL

    def draw(self):
        ''' Draw platform on the window
        :return: None
        '''
        platform_img_rect = platform_img.get_rect()
        screen.blit(platform_img, (self.x, self.y))

        # check if platform out of window and add new platform
        if self.x < 0 and self.x < -X_WIDTH:
            screen.blit(platform_img, ((platform_img_rect.right + self.x), self.y))
            self.x = 0
        elif self.x < 0:
            screen.blit(platform_img, ((platform_img_rect.right + self.x), self.y))

    def bird_on_plaform(self):
        ''' Check if bird is on platform (for game over)
        :return: bool
        '''
        platform_masking = pygame.mask.from_surface(platform_img)
        # top platform
        top = self.y
        top_offset = (self.x - cBird.x, top - round(cBird.y))
        if cBird.bird_masking().overlap(platform_masking, top_offset):
            return True
        return False

class Background():
    def __init__(self):
        self.x = 0
        self.y = 0

    def draw(self):
        ''' Draw background image
        :return: None
        '''
        # fill the surface objeact with black color
        #screen.fill(COLORBLACK)
        # copying the image surface object to the display surface object at coordinate (0, 0)
        screen.blit(bkgnd_img, (self.x, self.y))


def main():
    cBackground.draw()
    cPipe.draw()
    cPlatform.draw()
    cBird.draw()

def restart_game():
    cBackground = Background()
    cPipe = Pipe()
    cPlatform = Platform()
    cBird = Bird()

if __name__ == "__main__":
    print("Flappy Bird Starting...")

    fpsClock = pygame.time.Clock()
    score = 0

    # scale 2x the bird images
    for x, bird in enumerate(bird_imgs):
        bird_imgs[x] = pygame.transform.scale2x(bird_imgs[x])

    cBackground = Background()
    cPipe = Pipe()
    cPlatform = Platform()
    cBird = Bird()

    pipe_img_rect = pipe_img.get_rect()
    pipe_num = 0

    scoreFlag0 = False
    scoreFlag1 = False
    scoreFlag2 = False
    collide_sound = False
    game_over = False
    runFlag = True
    while runFlag:
        fpsClock.tick(FPS)

        # iterate over the list of Event objects that was returned by pygame.event.get() method.
        for event in pygame.event.get():
            # if event object type is QUIT
            if event.type == pygame.QUIT:
                runFlag = False
                # deactivate pygame library
                pygame.quit()
                # quit the program
                quit()
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    cBird.jump()
                    cBird.bird_masking()

        # Check collision
        if cPipe.collision(pipe_num) == False and game_over == False:
            # No collision #
            game_over = False
            # Bird, platform, pipe movement
            cBird.gravity()
            cPlatform.move()
            cPipe.move()
            main()

            # Scoring Descriptions #
            # score if (pipe.x + pipe.right(width)" equals to bird.x
            # flag1 turns True for pipe1 [flag2, flag3 False], add one score
            # flag2 turns True for pipe2 [flag1, flag3 False], add one score, repeat
            if cPipe.x[0] + pipe_img_rect.right < cBird.x and scoreFlag0 == False:
                score += 1
                scoreFlag0 = True
                scoreFlag1 = False
                scoreFlag2 = False
                pipe_num = 1
            elif cPipe.x[1] + pipe_img_rect.right < cBird.x and scoreFlag1 == False:
                score += 1
                scoreFlag0 = False
                scoreFlag1 = True
                scoreFlag2 = False
                pipe_num = 2
            elif cPipe.x[2] + pipe_img_rect.right < cBird.x and scoreFlag2 == False:
                score += 1
                scoreFlag0 = False
                scoreFlag1 = False
                scoreFlag2 = True
                pipe_num = 0
        else:
            # collision detected #
            game_over = True
            if collide_sound ==  False:
                add_sound = pygame.mixer.Sound('sound/bump.wav')
                add_sound.play()
                collide_sound = True

            if game_over:
                if cPlatform.bird_on_plaform():
                    cBird.bird_collide(False)
                    main()
                else:
                    cBird.bird_collide(True)
                    main()

            # Show the game over
            gameover_msg = score_font.render("GAME OVER", True, COLORBLACK)
            screen.blit(gameover_msg, (X_WIDTH/3, Y_HEIGHT/2.2))

        # Show the score
        score_msg = score_font.render("Score: {}".format(score), True, (255, 0, 0))
        screen.blit(score_msg, (10, 10))

        # Draws the surface object to the screen.
        pygame.display.update()
