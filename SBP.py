"""
TO DO:
* A̶d̶d̶ ̶a̶ ̶b̶a̶l̶l̶ ̶o̶b̶j̶e̶c̶t̶ ̶t̶h̶a̶t̶ ̶b̶o̶u̶n̶c̶e̶s̶ ̶o̶f̶f̶ ̶t̶h̶e̶ ̶p̶a̶d̶d̶l̶e̶s̶  COMPLETED* (Maybe make it better, but for now it's playable)
* EXTRA: Add Particle Effects to the ball* COMPLETED
* EXTRA: Add Pause Menu* COMPLETED
"""

# Seem to be an issue with the left paddle
# Ball very finicky when respawning, sometimes spawns with 0
import pygame, sys, os, random
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from src.windowClass import Window
from pygame.locals import *
pygame.init()
pygame.font.init()
pygame.mixer.init()

icon = pygame.image.load(os.path.join('src/icon.jpg'))
font = pygame.font.Font('src/Akko W01 Black Condensed.ttf', 120)

# Sounds ---------------------------------------------------- #
ball_sound = pygame.mixer.Sound(os.path.join('src/ball_bounce.wav'))
score_sound = pygame.mixer.Sound(os.path.join('src/score.wav'))
pause_sound = pygame.mixer.Sound(os.path.join('src/pause.wav'))

# Colors ---------------------------------------------------- #
White = (255,255,255)
Black = (0,0,0)
Red = (255,0,0)
Green = (0, 255, 0)

# Window ---------------------------------------------------- #
WINDOW = [800, 600]
window = Window("Super Broken Pong: Playing!", WINDOW, icon, pygame.DOUBLEBUF, 60)
NET = pygame.Rect(WINDOW[0]//2, 0, 10, WINDOW[1])
GOAL1 = pygame.Rect(window.size[0], 0, 20, window.size[1])
GOAL2 = pygame.Rect(-20, 0, 20, window.size[1])

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def pause(display):
    pause = True
    while pause:
        pygame.display.set_caption("Super Broken Pong: Paused!")
        pause_screen = pygame.Surface(WINDOW)
        pause_screen.fill(Black)
        draw_text("Paused", font, White, pause_screen, (WINDOW[0]//2), WINDOW[1]//2)
        #pause_screen.set_alpha(25)
        display.blit(pause_screen, (0,0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_p:
                    pause_sound.play()
                    pygame.display.set_caption("Super Broken Pong: Playing!")
                    pause = False
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        window.update()

# Paddle Class ---------------------------------------------- #
class Paddle:
    def __init__(self, borderW, borderH, location, movement, size, side):
        self.border = [borderW, borderH]
        self.side = side
        self.location = location
        self.movement = movement
        self.size = size
        self.MoveUp = False
        self.MoveDown = False
        self.MoveLeft = False
        self.MoveRight = False
        self.RotateRight = False
        self.RotateLeft = False
        self.moving = False
        self.paddle = pygame.Rect(self.location, self.size)

    def draw(self, surface, color):
        pygame.draw.rect(surface, color, self.paddle)

    def move(self, net):
        if self.MoveUp and self.paddle.y > self.movement > 0:
            self.paddle.y -= self.movement
        if self.MoveDown and self.paddle.y + self.movement + self.paddle.height < WINDOW[1]:
            self.paddle.y += self.movement

        if self.side == 'right':
            if self.MoveLeft and self.paddle.x > net.x + net.width: # Not on flipped equivilent side
                self.paddle.x -= self.movement
            if self.MoveRight and self.paddle.right < WINDOW[0] - self.paddle.width:
                self.paddle.x += self.movement

        if self.side == 'left':
            if self.MoveLeft and self.paddle.x > 0 + self.paddle.width:
                self.paddle.x -= self.movement
            if self.MoveRight and self.paddle.x < net.x - net.width - self.paddle.width:
                self.paddle.x += self.movement

        if self.MoveRight or self.MoveLeft:
            self.moving = True
        else:
            self.moving = not self.moving

# Ball Class ---------------------------------------------- #
# Calculate the paddle bounce trajectory fron the center y of the paddle rect

class Ball:
    def __init__(self, initial_momentum):
        isNegative = False
        self.momentum = initial_momentum # x velocity, y trajectory
        self.ball = pygame.Rect(WINDOW[0]//2, WINDOW[1]//2, 20, 20)
        self.border = WINDOW[1]
        self.particles = []

    def drawBall(self, display):
        pygame.draw.rect(display, White, self.ball)

    def drawParticles(self): # Particle system needs a bit more work,
        self.particles.append([[self.ball.centerx, self.ball.centery], [random.randint(0, 20) / 10 - 1, -2], [random.randint(0, 10), random.randint(0, 10)], -4])

        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += -1
            particle[3] += 0.3
            particle[1][1] += 0.5
            alpha = 190
            rect = pygame.Rect(*list(map(int, particle[0])), 5, 5)
            pygame.draw.rect(window.displayLayer, White, rect)
            if particle[3] >= 2:
                self.particles.remove(particle)

    # This is horrible, pls fix
    def ballBounce(self, paddle):
        acceleration = 1.2
        paddleCollide = False
        if self.ball.colliderect(paddle.paddle):
            ball_sound.play()

            self.momentum[0] = -self.momentum[0]
            self.momentum[0] *= acceleration

            if paddle.side == 'right':
                if paddle.MoveRight or paddle.MoveLeft:
                    self.ball.x = paddle.paddle.left - paddle.paddle.width - paddle.movement - 1
                else:
                    self.ball.x = paddle.paddle.left-paddle.paddle.width

            if paddle.side == 'left':
                if paddle.MoveRight or paddle.MoveLeft:
                    self.ball.x = paddle.paddle.left + paddle.paddle.width + paddle.movement + 1
                else:
                    self.ball.x = paddle.paddle.left+paddle.paddle.width

            # Trajectory calculate
            if self.ball.y > paddle.paddle.centery:
                self.momentum[1] = 1
            if self.ball.y < paddle.paddle.centery:
                self.momentum[1] = -1

        if self.ball.y > WINDOW[1]-10 or self.ball.y < 0:
            self.momentum[1] *= -1
            ball_sound.play()

        self.ball.x += self.momentum[0]
        self.ball.y += self.momentum[1]

    def respawn(self):
        launch = [2.5, -2.5]
        self.ball.x = WINDOW[0]/2
        self.ball.y = random.randint(250, 450)
        self.momentum[0] = random.choice(launch)
        self.momentum[1] = random.choice(launch)
        if self.momentum[0] == 0:
            self.momentum[0] = 1

# Score Class --------------------------------------------- #


class Score:
    def __init__(self, goal, player, increase = 1):
        self.player = player
        self.increase = increase
        self.score = 0
        self.score_sound = score_sound
        self.goal = goal

    def update(self, display):
        if self.player.side == 'left':
            draw_text(str(self.score), font, White, display, WINDOW[0]//2-120, 50)
        if self.player.side == 'right':
            draw_text(str(self.score), font, White, display, WINDOW[0]//2+120, 50)

    def scoring(self, ball):
        if self.goal.colliderect(ball.ball):
            ball.respawn()
            self.score += self.increase
            self.score_sound.play()

# Game Elements ------------------------------------ #
window_w = window.displayLayer.get_width()
window_h = window.displayLayer.get_height()
main = window.displayLayer

player_one = Paddle(window_w, window_h, [0,5], 9, [15, 100], 'left')
player_two = Paddle(window_w, window_h, [770,5], 9, [15, 100], 'right')
player_one_score = Score(GOAL1, player_one, 1)
player_two_score = Score(GOAL2, player_two, 1)
ball = Ball([3, 1])
border = pygame.Rect(window.size[0]//2, window.size[1]//2, 30, 30)

if __name__ == '__main__':
    while True:
        window.displayLayer.fill((0,0,40))
        pygame.draw.rect(window.displayLayer, Red, NET)
        pygame.draw.rect(window.displayLayer, Green, GOAL2)

        player_one.move(NET)
        player_two.move(NET)
        player_one_score.update(window.displayLayer)
        player_two_score.update(window.displayLayer)
        ball.drawBall(main)
        ball.drawParticles()

        ball.ballBounce(player_one)
        ball.ballBounce(player_two)
        # Event Loop -------------------------------- #
        for event in pygame.event.get():
            if event.type == QUIT:
                window.close()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    window.close()

                # Player One
                if event.key == K_w:
                    player_one.MoveUp = True
                if event.key == K_s:
                    player_one.MoveDown = True
                if event.key == K_a:
                    player_one.MoveLeft = True
                if event.key == K_d:
                    player_one.MoveRight = True

                # Player Two
                if event.key == K_UP:
                    player_two.MoveUp = True
                if event.key == K_DOWN:
                    player_two.MoveDown = True
                if event.key == K_LEFT:
                    player_two.MoveLeft = True
                if event.key == K_RIGHT:
                    player_two.MoveRight = True

                # Pause
                if event.key == K_p:
                    pause_sound.play()
                    pause(window.displayLayer)

                # Respawn Ball
                if event.key == K_r:
                    ball.respawn()

            if event.type == KEYUP:

                # Player One
                if event.key == K_w:
                    player_one.MoveUp = False
                if event.key == K_s:
                    player_one.MoveDown = False
                if event.key == K_a:
                    player_one.MoveLeft = False
                if event.key == K_d:
                    player_one.MoveRight = False

                # Player Two
                if event.key == K_UP:
                    player_two.MoveUp = False
                if event.key == K_DOWN:
                    player_two.MoveDown = False
                if event.key == K_LEFT:
                    player_two.MoveLeft = False
                if event.key == K_RIGHT:
                    player_two.MoveRight = False

        keys_pressed = pygame.key.get_pressed()
        player_one_score.scoring(ball)
        player_two_score.scoring(ball)
        player_one.draw(window.displayLayer, White)
        player_two.draw(window.displayLayer, White)
        window.update()
