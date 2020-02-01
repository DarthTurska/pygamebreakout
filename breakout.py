import pygame
import pygame_gui
import colorsys

pygame.init()

WIN_WIDTH = 500
WIN_HEIGHT = 700


run = True

win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

pygame.display.set_caption("BREAKOUT")

paddle = pygame.Rect((0, 0), (70, 8))
paddle.center = (WIN_WIDTH / 2, 680)
lastx = paddle.centerx

ballimg = pygame.image.load("ball.png")
ball = pygame.Rect((0, 0), (10, 10))
ball.midbottom = paddle.midtop


class Heart:
    def __init__(self, pos):
        hearts.append(self)
        self.img = pygame.transform.scale2x(pygame.image.load("heart.png"))
        self.rect = pygame.Rect((pos), (20, 18))

    def update(self):
        win.blit(self.img, self.rect)


class Brick:
    def __init__(self, pos, w, h, color):
        bricks.append(self)
        self.pos = pos
        self.rect = pygame.Rect(pos, (w, h))
        self.color = color
        self.update()

    def update(self):
        pygame.draw.rect(win, self.color, self.rect)


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def update():
    win.fill((0, 0, 0))

    for brick in bricks:
        brick.update()
    for heart in hearts:
        heart.update()

    pygame.draw.rect(win, (255, 255, 255), paddle)
    win.blit(ballimg, ball)


# 1 = Block
# - = Empty
# "--------------------",
# "11111111111111111111",

levels = [
    [
        "11111111111111111111",
        "11111111111111111111",
        "11111111111111111111",
        "11111111111111111111",
        "11111111111111111111"
    ],
    [
        "11111---1111---11111",
        "1---11111--11111---1",
        "1---1-1-1--1-1-1---1",
        "1---1-1-1--1-1-1---1",
        "1---1-1-1--1-1-1---1",
        "1---1-1-1--1-1-1---1",
        "1---1-1-1--1-1-1---1",
        "1---11111--11111---1",
        "11111---1111---11111"
    ],
    [
        "11111111111111111111",
        "1------------------1",
        "1-1111111111111111-1",
        "1-1--------------1-1",
        "1-1-111111111111-1-1",
        "1-1-1----------1-1-1",
        "1-1-1-1111111111-1-1",
        "1-1-1------------1-1",
        "1-1-11111111111111-1",
        "1-1----------------1",
        "1-111111111111111111",
    ]
]

bricks = []
hearts = []
hp = 2
clock = pygame.time.Clock()

manager = pygame_gui.UIManager((WIN_WIDTH, WIN_HEIGHT), "theme.json")

lvl1_rect = pygame.Rect((0, 0), (100, 50))
lvl1_rect.center = (WIN_WIDTH / 2, WIN_HEIGHT / 2 - lvl1_rect.width)
lvl1_button = pygame_gui.elements.UIButton(relative_rect=lvl1_rect,
                                           text='LEVEL 1',
                                           manager=manager)
lvl2_rect = pygame.Rect((0, 0), (100, 50))
lvl2_rect.center = (WIN_WIDTH / 2, WIN_HEIGHT / 2)
lvl2_button = pygame_gui.elements.UIButton(relative_rect=lvl2_rect,
                                           text='LEVEL 2',
                                           manager=manager)
lvl3_rect = pygame.Rect((0, 0), (100, 50))
lvl3_rect.center = (WIN_WIDTH / 2, WIN_HEIGHT / 2 + lvl1_rect.width)
lvl3_button = pygame_gui.elements.UIButton(relative_rect=lvl3_rect,
                                           text='LEVEL 3',
                                           manager=manager)

def lvlSelect():
    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.USEREVENT:
                if event.user_type == 'ui_button_pressed':
                    if event.ui_element == lvl1_button:
                        return 1

                    elif event.ui_element == lvl2_button:
                        return 2

                    elif event.ui_element == lvl3_button:
                        return 3

            manager.process_events(event)

        manager.update(time_delta)
        win.fill((0, 0, 0))
        manager.draw_ui(win)

        pygame.display.flip()

level = lvlSelect()

def createLevel(level):
    x = y = 0
    color = 0
    for row in levels[level - 1]:
        for col in row:
            if col == "1":
                Brick((x, y), WIN_WIDTH / len(row), 25, hsv2rgb(color / len(row), 1, 1))
            x += WIN_WIDTH / len(row)
            color += 1
        y += 25
        x = 0

    for i in range(hp+1):
        Heart((WIN_WIDTH-i*21-20, 5))

createLevel(level)
pygame.mouse.set_visible(False)
def shoot():
    while True:
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONUP:
                ballvel = pygame.math.Vector2()
                ballvel.x = mpos[0] - ball.centerx
                ballvel.y = mpos[1] - ball.centery
                ballvel.normalize_ip()
                ballvel.x *= 4
                ballvel.y *= 4
                return ballvel

        mpos = pygame.mouse.get_pos()
        update()
        pygame.draw.line(win, (255, 255, 255), mpos, ball.center)
        pygame.draw.rect(win, (255, 255, 255), (mpos[0] - 2, mpos[1] - 2, 4, 4))
        pygame.display.flip()

pygame.mouse.set_visible(True)

ballvel = shoot()
while run:
    clock.tick(120)

    mpos = pygame.mouse.get_pos()
    # collision checks
    for brick in bricks:
        if brick.rect.colliderect(ball):
            if ball.x < brick.rect.x or (ball.x + ball.width) > (brick.rect.x + brick.rect.width):
                ballvel.x = -ballvel.x
                bricks.remove(brick)
                del brick
            elif ball.x < (brick.rect.x + brick.rect.width):
                ballvel.y = -ballvel.y
                bricks.remove(brick)
                del brick

    if paddle.topleft <= ball.topright and paddle.topright >= ball.topleft and (ball.top + ballvel.y) >= paddle.y:
        ballvel.x += paddle_vel / 3
        ballvel.y = -ballvel.y
    elif ball.right + ballvel.x >= WIN_WIDTH or ball.left + ballvel.x <= 0:
        ballvel.x = -ballvel.x
    elif ball.top <= 0:
        ballvel.y = -ballvel.y
    elif ball.bottom >= WIN_HEIGHT:
        print(hp)
        if hp <= 0:
            run = False
        else:
            hp -= 1
            del hearts[-1]
            ballvel = shoot()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paddle.center = (WIN_WIDTH / 2, 680)
                ball.midbottom = paddle.midtop
                level = lvlSelect()
                hp = 2
                hearts = []
                bricks = []
                createLevel(level)
                ballvel = shoot()

    if not bricks:
        paddle.center = (WIN_WIDTH / 2, 680)
        ball.midbottom = paddle.midtop
        level = lvlSelect()
        hp = 2
        hearts = []
        bricks = []
        createLevel(level)
        ballvel = shoot()
    paddle.centerx = mpos[0]
    paddle_vel = mpos[0] - lastx
    ball.x += ballvel.x
    ball.y += ballvel.y
    update()

    pygame.display.flip()
    lastx = paddle.centerx
pygame.quit()
quit()
