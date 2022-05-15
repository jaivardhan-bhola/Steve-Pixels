from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# hide pygame message
import pygame
import copy
import random
import sys
from win32gui import SetWindowPos
from pygame.locals import *
from PIL import Image, ImageFilter

# Code made by:
# ..\ Ishan Jindal
# ..\ Jaivardhan Bhola

# GitHub Repo Link:
# https://github.com/jaivardhan-bhola/Steve-Pixels

# This project is MIT Licensed
# It is open-source under fair usage
# Kindly mention Authors' names if you copy this code

assets_folder = 'assets'
# !!! very important. all assets placed here
# leave empty string to disable if root folder

cheatcode = 'helpme'
# Don't tell anyone!
# leave empty string to disable

pygame.init()

screen_w = pygame.display.Info().current_w
screen_h = pygame.display.Info().current_h

color = {
    'black': (50, 50, 50),
    'blacker': (20, 20, 20),
    'white': (240, 240, 240),
    'gray': (150, 150, 150),
    'red': (255, 50, 50),
    'orange': (255, 150, 0),
    'yellow': (255, 200, 0),
    'green': (100, 200, 50),
    'blue': (0, 220, 220),
    'purple': (150, 100, 255),
}

image_dict = {'uncovered goal': pygame.image.load(f'{assets_folder}\\orange_pad.png'),
              'covered goal': pygame.image.load(f'{assets_folder}\\green_pad.png'),

              'pixel': pygame.image.load(f'{assets_folder}\\pixels.png'),
              'wall': pygame.image.load(f'{assets_folder}\\wood.png'),
              'inside floor': pygame.image.load(f'{assets_folder}\\sand.png'),
              'outside floor': pygame.image.load(f'{assets_folder}\\grass.png'),

              'title': pygame.image.load(f'{assets_folder}\\title.png'),
              'solved': pygame.image.load(f'{assets_folder}\\solved.png'),

              'p_front': pygame.image.load(f'{assets_folder}\\steve_front.png'),
              'p_back': pygame.image.load(f'{assets_folder}\\steve_back.png'),
              'p_left': pygame.image.load(f'{assets_folder}\\steve_left.png'),
              'p_right': pygame.image.load(f'{assets_folder}\\steve_right.png'),

              'rock': pygame.image.load(f'{assets_folder}\\rock.png'),
              'tall tree': pygame.image.load(f'{assets_folder}\\bush.png'),
              'cursor': pygame.image.load(f'{assets_folder}\\cursor.png'),

              'cut_in': pygame.image.load(f'{assets_folder}\\start.png'),
              'cut_out': pygame.image.load(f'{assets_folder}\\over.png'),
              'creds': pygame.image.load(f'{assets_folder}\\credits.png')}

sound_dict = {'pause': f'{assets_folder}\\pause.mp3',
              'resume': f'{assets_folder}\\resume.mp3',
              'level_complete': f'{assets_folder}\\level.mp3',
              'theme': f'{assets_folder}\\theme.mp3'}

##################################################
##################################################
############# EDITABLE  PARAMETERS ###############
##################################################
##################################################


fullscreen = True

win_w = 1500
win_h = 800
# ignored if fullscreen
window_y_offset = 0.6
# offset y position of window by -60%


music_during_levels = True

tile_w = 50
tile_h = 85
tile_floor_height = 40

scale_map_int: int = 2
# choose among 1, 2, 3;   2 is optimal in fullscreen;   Ignored if auto_scale is True

scale_map: int
auto_scale = True

title_transform = [[60, 75], 3]
# min and max percentage of title image wrt window size
# slowness wrt 60 fps

pause_blur = 25
pause_opacity = 150
# out of 255

lvl_complete_blur = 5

grass_decoration_percentage = 40

bg_color = color['black']
txt_color = color['white']
font_size = round(win_h / 25 * 0.75)

music_volume = [0.4, 0.08, 0.16]
# max, min, levels
if not music_during_levels:
    music_volume[2] = 0

##################################################
##################################################
############# STANDARD  DEFINITIONS ##############
##################################################
##################################################

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

fps_clock = pygame.time.Clock()

if not fullscreen:
    screen = pygame.display.set_mode((win_w, win_h))
    SetWindowPos(pygame.display.get_wm_info()['window'], -1,
                 round(screen_w / 2 - win_w / 2), round((screen_h / 2 - win_h / 2) * window_y_offset), 0, 0, 1)


else:
    win_w = screen_w
    win_h = screen_h
    screen = pygame.display.set_mode((win_w, win_h), pygame.FULLSCREEN)

if not auto_scale:
    scale_map = scale_map_int
else:
    map_size_chunk = tile_w * tile_w * 100
    window_area = win_w * win_h
    tile_screen_percent = round(map_size_chunk / window_area * 100)
    if tile_screen_percent <= 10:
        scale_map = 3
    elif tile_screen_percent <= 30:
        scale_map = 2
    else:
        scale_map = 1

CAM_MOVE_SPEED = scale_map / 3

win_w_half = int(win_w / 2)
win_h_half = int(win_h / 2)

cursor_img = pygame.transform.scale(image_dict['cursor'], (32, 32))
pygame.mouse.set_visible(False)

pause_sound = pygame.mixer.Sound(sound_dict['pause'])
resume_sound = pygame.mixer.Sound(sound_dict['resume'])
level_sound = pygame.mixer.Sound(sound_dict['level_complete'])
music = pygame.mixer.music.load(sound_dict['theme'])

pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(music_volume[0])


##################################################
##################################################
##################################################


def main():
    global tile_mapping, grass_deco_mapping, basic_font, player_images, currentImage

    tile_w *= scale_map
    tile_h *= scale_map
    tile_floor_height *= scale_map

    pygame.display.set_caption('Steve\'s Pixels')
    pygame.display.set_icon(image_dict['cursor'])
    basic_font = pygame.font.Font(f'{assets_folder}\\AccordAlternate-Bold.ttf', font_size)

    for i in image_dict:
        if i not in ('title', 'solved', 'cursor', 'cut_in', 'cut_out', 'creds'):
            image_dict[i] = pygame.transform.scale(image_dict[i], (tile_w, tile_h))

    tile_mapping = {'#': image_dict['wall'],
                    'o': image_dict['inside floor'],
                    ' ': image_dict['outside floor']}

    grass_deco_mapping = {'0': image_dict['rock'],
                          '1': image_dict['tall tree']}

    currentImage = 0
    player_images = [image_dict['p_front'],
                     image_dict['p_back'],
                     image_dict['p_left'],
                     image_dict['p_right']]

    startScreen()
    cutscene('start')

    levels = readLevelsFile()
    currentLevelIndex = 0

    while True:

        result = runLevel(levels, currentLevelIndex)

        if result in ('solved', 'next'):

            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                break

    pygame.mixer.music.set_volume(music_volume[0])
    cutscene('over')
    creds()


def runLevel(levels, levelNum):
    pygame.mixer.music.set_volume(music_volume[2])

    global currentImage
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True
    levelSurf = basic_font.render(f'Level {levelNum + 1} of {len(levels)}', 1, txt_color)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, round(win_h - 2 * font_size * 4 / 3))
    mapWidth = len(mapObj) * tile_w
    mapHeight = (len(mapObj[0]) - 1) * tile_floor_height + tile_h
    MAX_CAM_X_PAN = abs(win_h_half - int(mapHeight / 2)) + tile_w
    MAX_CAM_Y_PAN = abs(win_w_half - int(mapWidth / 2)) + tile_h

    levelIsComplete = False

    cameraOffsetX = 0
    cameraOffsetY = 0

    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    solved_shown = False

    cheat_entered = ''

    alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
                 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                 'o', 'p', 'q', 'r', 's', 't', 'u',
                 'v', 'w', 'x', 'y', 'z']

    while True:
        playerMoveTo = None

        for event in pygame.event.get():
            if event.type == QUIT:

                pause_screen()

            elif event.type == KEYDOWN:

                current_key = pygame.key.name(event.key)
                if current_key in alphabets and len(cheat_entered) < len(cheatcode):
                    if current_key == cheatcode[len(cheat_entered)]:
                        cheat_entered += current_key
                    else:
                        cheat_entered = ''

                if solved_shown:
                    currentImage = 0
                    return 'solved'

                if event.key == K_j:
                    cameraLeft = True
                elif event.key == K_l:
                    cameraRight = True
                elif event.key == K_i:
                    cameraUp = True
                elif event.key == K_k:
                    cameraDown = True


                elif event.key in (K_a, K_LEFT):
                    currentImage = 2
                    playerMoveTo = LEFT
                    mapNeedsRedraw = True
                elif event.key in (K_d, K_RIGHT):
                    currentImage = 3
                    playerMoveTo = RIGHT
                    mapNeedsRedraw = True
                elif event.key in (K_w, K_UP):
                    currentImage = 1
                    playerMoveTo = UP
                    mapNeedsRedraw = True
                elif event.key in (K_s, K_DOWN):
                    currentImage = 0
                    playerMoveTo = DOWN
                    mapNeedsRedraw = True


                elif event.key == K_ESCAPE:
                    pause_screen()
                elif event.key == K_BACKSPACE:
                    currentImage = 0
                    mapNeedsRedraw = True
                    return 'reset'


            elif event.type == KEYUP:

                if event.key == K_j:
                    cameraLeft = False
                elif event.key == K_l:
                    cameraRight = False
                elif event.key == K_i:
                    cameraUp = False
                elif event.key == K_k:
                    cameraDown = False

        if playerMoveTo is not None and not levelIsComplete:

            moved = makeMove(mapObj, gameStateObj, playerMoveTo)

            if moved:
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj):
                levelIsComplete = True

        screen.fill(bg_color)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += CAM_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= CAM_MOVE_SPEED
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += CAM_MOVE_SPEED
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= CAM_MOVE_SPEED

        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (win_w_half + cameraOffsetX, win_h_half + cameraOffsetY)

        screen.blit(mapSurf, mapSurfRect)

        screen.blit(levelSurf, levelRect)
        stepSurf = basic_font.render('Steps: %s' % (gameStateObj['stepCounter']), 1, txt_color)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, round(win_h - font_size * 4 / 3))
        screen.blit(stepSurf, stepRect)

        if cheat_entered == cheatcode != '':
            levelIsComplete = True

        if levelIsComplete:

            old_w = image_dict['solved'].get_width()
            old_h = image_dict['solved'].get_height()

            new_w = round(win_w / 2)
            new_h = round(old_h * new_w / old_w)

            solved_img = pygame.transform.scale(image_dict['solved'], (new_w, new_h))

            solvedRect = solved_img.get_rect()
            solvedRect.x = round(win_w / 12)
            solvedRect.y = round(win_h / 10)

            solved_overlay = lvl_complete_blurry(solved_img, solvedRect)

            if not solved_shown:

                level_sound.play()

                for i in range(0, 256, 4):

                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pause_screen()

                        elif event.type == KEYDOWN:

                            if event.key == K_ESCAPE:
                                pause_screen()

                            currentImage = 0
                            return 'solved'

                    solved_overlay.set_alpha(i)
                    screen.blit(solved_overlay, (0, 0))
                    pygame.display.update()
                    fps_clock.tick(64)

                solved_shown = True
            else:
                screen.blit(solved_overlay, (0, 0))

        pygame.display.update()
        fps_clock.tick()


def isWall(mapObj, x, y):
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False
    elif mapObj[x][y] in ('#', 'x'):
        return True
    return False


def decorateMap(mapObj, start_xy):
    start_x, start_y = start_xy

    mapObjCopy = copy.deepcopy(mapObj)

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '

    floodFill(mapObjCopy, start_x, start_y, ' ', 'o')

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] == ' ' and random.randint(0, 99) < grass_decoration_percentage:
                mapObjCopy[x][y] = random.choice(list(grass_deco_mapping.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):
    if isWall(mapObj, x, y):
        return True

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True

    elif (x, y) in gameStateObj['pixels']:
        return True

    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):
    player_x, player_y = gameStateObj['player']

    pixels = gameStateObj['pixels']

    if playerMoveTo == UP:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0

    if isWall(mapObj, player_x + xOffset, player_y + yOffset):
        return False
    else:
        if (player_x + xOffset, player_y + yOffset) in pixels:

            if not isBlocked(mapObj, gameStateObj, player_x + (xOffset * 2), player_y + (yOffset * 2)):

                ind = pixels.index((player_x + xOffset, player_y + yOffset))
                pixels[ind] = (pixels[ind][0] + xOffset, pixels[ind][1] + yOffset)
            else:
                return False

        gameStateObj['player'] = (player_x + xOffset, player_y + yOffset)
        return True


def startScreen():
    title_img = image_dict['title']

    title_w = title_img.get_width()
    title_h = title_img.get_height()

    upper_limit = title_transform[0][1]
    lower_limit = title_transform[0][0]

    fps = 60

    counter = title_transform[1]
    counter_limit = 100
    check_divisibilty_of = counter

    title_image_size_factor = lower_limit
    size_change_factor = +1

    new_title_w = round(win_w * lower_limit / 100)
    new_title_h = round(title_h * new_title_w / title_w)

    title_x = round((win_w - new_title_w) / 2)
    title_yy = round(win_h * 2 / 7)

    instructionText = ['Push all the Pixel-Crystals in the portals!',
                       '',
                       'Movement: WASD/Arrow keys',
                       'Camera control: I-J-K-L',
                       'Exit game: Escape',
                       'Reset level: Backspace',
                       'Continue: Enter']

    while True:

        if counter % check_divisibilty_of == 0:

            if title_image_size_factor <= lower_limit:
                size_change_factor = +1

            if title_image_size_factor >= upper_limit:
                size_change_factor = -1

            title_image_size_factor += size_change_factor

            new_title_w = win_w * title_image_size_factor / 100
            new_title_h = title_h * new_title_w / title_w

            title_x = round((win_w - new_title_w) / 2)
            title_y = title_yy - round(new_title_h / 2)

            screen.fill(bg_color)
            screen.blit(pygame.transform.scale(title_img, (new_title_w, new_title_h)),
                        (title_x, title_y - round(new_title_h / 2)))

            topCoord = round(win_h * 4 / 9)

            for i in range(len(instructionText)):
                instSurf = basic_font.render(instructionText[i], 1, txt_color)
                instRect = instSurf.get_rect()
                topCoord += 10
                instRect.top = topCoord
                instRect.centerx = win_w_half
                topCoord += instRect.height
                screen.blit(instSurf, instRect)

        cur_func()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_RETURN:
                    return

        fps_clock.tick(fps)
        counter += 1
        if counter > counter_limit:
            counter = 2


def cutscene(state: str):
    if state == 'start':
        img = image_dict['cut_in']
    elif state == 'over':
        img = image_dict['cut_out']
    else:
        return

    img_w_old = img.get_width()
    img_h_old = img.get_height()
    img_rect = img.get_rect()

    img_rect.w = win_w
    img_rect.h = round(img_h_old * img_rect.w / img_w_old, 2)
    img_rect.x = 0
    img_rect.y = round(win_h / 2 - img_rect.h / 2)

    if win_w / win_h <= img_w_old / img_h_old:
        img_rect.w = win_w
        img_rect.h = round(img_h_old * img_rect.w / img_w_old, 2)
        img_rect.x = 0
        img_rect.y = round(win_h / 2 - img_rect.h / 2)
    elif win_w / win_h > img_w_old / img_h_old:

        img_rect.h = win_h
        img_rect.w = round(img_w_old * img_rect.h / img_h_old)
        img_rect.x = round(win_w / 2 - img_rect.w / 2)
        img_rect.y = 0

    alpha = 0
    img = pygame.transform.scale(img, (img_rect.w, img_rect.h))

    for alpha in range(0, 256, 8):

        for event in pygame.event.get():
            if event.type == QUIT:
                pause_screen()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pause_screen()
                else:
                    done = True

        img.set_alpha(alpha)
        pygame.draw.rect(screen, color['blacker'], pygame.Rect(0, 0, win_w, win_h))
        screen.blit(img, img_rect)
        pygame.display.update()
        fps_clock.tick(32)

    img.set_alpha(255)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == QUIT:
                pause_screen()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pause_screen()
                else:
                    done = True

        pygame.draw.rect(screen, color['blacker'], pygame.Rect(0, 0, win_w, win_h))

        screen.blit(img, img_rect)

        pygame.display.update()

        fps_clock.tick(60)

    return


def creds():
    img = image_dict['creds']

    img_w_old = img.get_width()
    img_h_old = img.get_height()
    img_rect = img.get_rect()

    img_rect.w = win_w
    img_rect.h = round(img_h_old * img_rect.w / img_w_old, 2)
    img_rect.x = 0
    img_rect.y = round(win_h / 2 - img_rect.h / 2)

    if win_w / win_h <= img_w_old / img_h_old:
        img_rect.w = win_w
        img_rect.h = round(img_h_old * img_rect.w / img_w_old, 2)
        img_rect.x = 0
        img_rect.y = round(win_h / 2 - img_rect.h / 2)
    elif win_w / win_h > img_w_old / img_h_old:

        img_rect.h = win_h
        img_rect.w = round(img_w_old * img_rect.h / img_h_old)
        img_rect.x = round(win_w / 2 - img_rect.w / 2)
        img_rect.y = 0

    alpha = 0
    img = pygame.transform.scale(img, (img_rect.w, img_rect.h))

    for alpha in range(0, 256, 8):

        for event in pygame.event.get():
            if event.type == QUIT:
                pass

        img.set_alpha(alpha)
        pygame.draw.rect(screen, color['blacker'], pygame.Rect(0, 0, win_w, win_h))
        screen.blit(img, img_rect)
        pygame.display.update()
        fps_clock.tick(32)

    img.set_alpha(255)

    done = False
    while not done:

        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:
                done = True

        pygame.draw.rect(screen, color['blacker'], pygame.Rect(0, 0, win_w, win_h))

        screen.blit(img, img_rect)

        pygame.display.update()

        fps_clock.tick(60)


def cur_func():
    cur_x, cur_y = pygame.mouse.get_pos()
    cur_rect = cursor_img.get_rect()
    cur_rect.x = round(cur_x - cur_rect.w / 2)
    cur_rect.y = round(cur_y - cur_rect.h / 2)
    screen.blit(cursor_img, cur_rect)


def readLevelsFile():
    # FORMAT:',
    #    @ - Steve
    #    $ - Pixel
    #    . - Goal
    #    # - Wall
    #    <space> -  space

    content = [

        ' ',
        ' ######',
        ' #  $.#',
        ' #@   #',
        ' ######',
        '        ',
        '',

        ' ',
        ' #########',
        ' #       #',
        ' # .  $  #',
        ' #   @   #',
        ' #  $  . #',
        ' #       #',
        ' #########',
        '           ',
        '',

        '#########',
        '#       #',
        '# ##### #',
        '#     # #',
        '##### # #',
        '#     # #',
        '#  #### #',
        ' # @#.$ #',
        '  ###   #',
        '     ####',
        '',

        ' ',
        '  ####### ',
        ' #@#     #',
        ' # #   $ #',
        ' #   ## ## ',
        ' ##   .#  ',
        '  ###  #  ',
        '     ##   ',
        '           ',
        '',

        ' ',
        ' ###########',
        ' #         #',
        ' #  . . .  #',
        ' ## ##### ##',
        '  # $ $ $ #',
        '  #   @   #',
        '  #########',
        '             ',
        ''
    ]

    levels = []
    levelNum = 0
    mapTextLines = []
    mapObj = []

    for lineNum in range(len(content)):

        line = content[lineNum].rstrip('\r\n')

        if line != '':
            mapTextLines.append(line)

        elif line == '' and len(mapTextLines) > 0:
            maxWidth = -1

            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])

            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            for x in range(len(mapTextLines[0])):
                mapObj.append([])

            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            start_x = None
            start_y = None
            goals = []
            pixels = []

            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] == '@':
                        start_x = x
                        start_y = y
                    if mapObj[x][y] == '.':
                        goals.append((x, y))
                    if mapObj[x][y] == '$':
                        pixels.append((x, y))

            gameStateObj = {'player': (start_x, start_y),
                            'stepCounter': 0,
                            'pixels': pixels}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)

            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x + 1][y] == oldCharacter:
        floodFill(mapObj, x + 1, y, oldCharacter, newCharacter)
    if x > 0 and mapObj[x - 1][y] == oldCharacter:
        floodFill(mapObj, x - 1, y, oldCharacter, newCharacter)
    if y < len(mapObj[x]) - 1 and mapObj[x][y + 1] == oldCharacter:
        floodFill(mapObj, x, y + 1, oldCharacter, newCharacter)
    if y > 0 and mapObj[x][y - 1] == oldCharacter:
        floodFill(mapObj, x, y - 1, oldCharacter, newCharacter)


def drawMap(mapObj, gameStateObj, goals):
    mapSurfWidth = len(mapObj) * tile_w
    mapSurfHeight = (len(mapObj[0]) - 1) * tile_floor_height + tile_h
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(bg_color)
    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * tile_w, y * tile_floor_height, tile_w, tile_h))
            if mapObj[x][y] in tile_mapping:
                baseTile = tile_mapping[mapObj[x][y]]
            elif mapObj[x][y] in grass_deco_mapping:
                baseTile = tile_mapping[' ']

            mapSurf.blit(baseTile, spaceRect)

            if mapObj[x][y] in grass_deco_mapping:

                mapSurf.blit(grass_deco_mapping[mapObj[x][y]], spaceRect)
            elif (x, y) in gameStateObj['pixels']:
                if (x, y) in goals:
                    mapSurf.blit(image_dict['covered goal'], spaceRect)

                mapSurf.blit(image_dict['pixel'], spaceRect)
            elif (x, y) in goals:

                mapSurf.blit(image_dict['uncovered goal'], spaceRect)

            if (x, y) == gameStateObj['player']:
                mapSurf.blit(player_images[currentImage], spaceRect)

    return mapSurf


def isLevelFinished(levelObj, gameStateObj):
    return all(not goal not in gameStateObj['pixels'] for goal in levelObj['goals'])


def pause_screen():

    exit_lines = [
        'PAUSE MENU',
        '',
        'ESCAPE to resume game',
        'ENTER to exit the game'
    ]

    blurry = generate_blurry()

    done = False

    pygame.mixer.music.set_volume(music_volume[1])
    pause_sound.play()

    while not done:

        screen.blit(blurry, (0, 0))

        topCoord = round(win_h * 0.25)

        for i in range(len(exit_lines)):
            instSurf = basic_font.render(exit_lines[i], 1, txt_color)
            instRect = instSurf.get_rect()
            topCoord += round(font_size * 2 / 3)
            instRect.top = topCoord
            instRect.centerx = win_w_half
            topCoord += instRect.height
            screen.blit(instSurf, instRect)

        cur_func()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    done = True
                elif event.key == K_RETURN:
                    terminate()

        fps_clock.tick(60)

    resume_sound.play()
    pygame.mixer.music.set_volume(music_volume[0])


def generate_blurry():

    rect = pygame.Rect(0, 0, win_w, win_h)
    sub = screen.subsurface(rect)
    screenshot = pygame.Surface((win_w, win_h))
    screenshot.blit(sub, (0, 0))

    pil_string_image = pygame.image.tostring(screenshot, "RGBA", False)
    pil_image = Image.frombytes("RGBA", (win_w, win_h), pil_string_image)
    pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=pause_blur))
    overlay = Image.new('RGBA', (win_w, win_h), color['black'])
    overlay.putalpha(pause_opacity)

    pil_image = Image.alpha_composite(pil_image, overlay)

    return pygame.image.fromstring(pil_image.tobytes(), pil_image.size, 'RGBA')


def lvl_complete_blurry(img, img_rect):

    rect = pygame.Rect(0, 0, win_w, win_h)
    sub = screen.subsurface(rect)
    screenshot = pygame.Surface((win_w, win_h))
    screenshot.blit(sub, (0, 0))

    pil_string_image = pygame.image.tostring(screenshot, "RGBA", False)
    pil_image = Image.frombytes("RGBA", (win_w, win_h), pil_string_image)
    pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=lvl_complete_blur))

    glass = pygame.image.fromstring(pil_image.tobytes(), pil_image.size, 'RGBA')
    glass.blit(img, img_rect)

    return glass


def terminate():
    pygame.quit()
    sys.exit()


main()
