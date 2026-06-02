import pygame
import sys
import os
import random
import math
from collections import deque
pygame.init()
pygame.mixer.init()

try:
    from kivy.utils import platform
except ImportError:
    platform = None

if platform is None:
    if hasattr(sys, 'getandroidapilevel') or 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_DATA' in os.environ:
        platform = 'android'
    elif sys.platform.startswith('win'):
        platform = 'win'
    elif sys.platform.startswith('darwin'):
        platform = 'macosx'
    elif sys.platform.startswith('linux'):
        platform = 'linux'
    else:
        platform = 'unknown'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def res(*path):
    p1 = os.path.join(SCRIPT_DIR, *path)
    p2 = os.path.join(SCRIPT_DIR, 'assets', *path)
    if os.path.exists(p1):
        return p1
    return p2


def get_save_dir():
    if platform == 'android':
        try:
            from android.storage import app_storage_path
            return app_storage_path()
        except ImportError:
            return os.environ.get('ANDROID_DATA', SCRIPT_DIR)
    else:
        return SCRIPT_DIR


def load_font_safe(name, size):
    try:
        return pygame.font.Font(res(name), size)
    except:
        return pygame.font.Font(None, size)


def draw_on_center(surface, image, x, y, w, h):
    rect = image.get_rect()
    rect.center = (x + w//2, y + h//2)
    surface.blit(image, rect)


pygame.display.set_caption("Snake")

if platform == "android":
    info = pygame.display.Info()
    if info.current_w > 0 and info.current_h > 0:
        WIDTH, HEIGHT = info.current_w, info.current_h
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WIDTH, HEIGHT = screen.get_size()
else:
    WIDTH = 393
    HEIGHT = 852
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

po_x_f = (10*WIDTH//12+1)//((HEIGHT-WIDTH)//16)
po_y_f = (8*HEIGHT//10+1)//((HEIGHT-WIDTH)//16)

eated = 0
running = True
Start = 1
menu = 1
stop = 1
animation = 1
for_body = 0
apple = 0
target = []
snake_bodycounter = 1
last_vector = "Right"
sound = 1
guide = 0
lose = 0
lose_timer = 0
score = 0
best_score = 0
second_guide = 1
restart_music = 1
blur = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
blur.fill((0, 0, 0, 100))

if platform == "android":
    snake_speedX = 4
else:
    snake_speedX = 10

swipe_start = None
swipe_min = WIDTH * 0.05

po_x = int(po_x_f)
po_y = int(po_y_f)

scale = (WIDTH/HEIGHT)/2

offset_x = math.ceil(10*WIDTH//12/po_x)
offset_y = math.ceil(8*HEIGHT//10/po_y)

snake_speed = offset_x//10

pole_x = po_x_f * offset_x
pole_y = po_y_f * offset_y

greh_x = pole_x % po_x_f
greh_y = pole_y % po_y_f

field = [[0 for _ in range(po_x)] for _ in range(po_y)]


class Snake():
    body_mass = []
    counter = 0
    vector = "Right"
    state = "Right"

    def __adc__(self):
        Snake.counter += 1
        return Snake.counter

    def spawnsnake():
        stroka = po_y - 3
        stolbec = po_x - 3
        return [stroka, stolbec]

    def setVector(self, vector):
        Snake.vector = vector


head_img = pygame.image.load(res("snake_head.png"))
head_img = pygame.transform.scale(
    head_img, (offset_x+offset_x*scale, offset_x+offset_x*scale))
body_img = pygame.image.load(res("snake_body_4.png"))
body_img = pygame.transform.scale(
    body_img, (offset_x+offset_x*scale, offset_x+offset_x*scale))

tail_img = pygame.image.load(res('snake_tail.png'))
tail_img = pygame.transform.scale(
    tail_img, (offset_x+offset_x*scale, offset_x+offset_x*scale))
apple_img = pygame.image.load(res('apple_img.png'))
apple_img = pygame.transform.scale(
    apple_img, (offset_x+offset_x*scale*2, offset_x+offset_x*scale*2))
angle_img = pygame.image.load(res('snake_angle.png'))
angle_img = pygame.transform.scale(
    angle_img, (offset_x+offset_x*scale, offset_x+offset_x*scale))
menu_img = pygame.image.load(res('menu.png'))
menu_img = pygame.transform.scale(menu_img, (WIDTH, HEIGHT))
blur_menu_img = pygame.image.load(res('blur_menu.png'))
blur_menu_img = pygame.transform.scale(blur_menu_img, (WIDTH, HEIGHT))
lose_img = pygame.image.load(res('lose.png'))
lose_img = pygame.transform.scale(lose_img, (WIDTH, HEIGHT))
start_button_img = pygame.image.load(res('start_button.png'))
start_button_img = pygame.transform.smoothscale(
    start_button_img, (WIDTH*4/6, HEIGHT*0.22))
guide_button_img = pygame.image.load(res('guide_button.png'))
guide_button_img = pygame.transform.smoothscale(
    guide_button_img, (WIDTH*1/5, WIDTH*1/5))
sound_button_img = pygame.image.load(res('sound_button.png'))
sound_button_img = pygame.transform.scale(
    sound_button_img, (WIDTH*1/5, WIDTH*1/5))
no_sound_button_img = pygame.image.load(res('no_sound_button.png'))
no_sound_button_img = pygame.transform.scale(
    no_sound_button_img, (WIDTH*1/5, WIDTH*1/5))
score_button_img = pygame.image.load(res('score_button.png'))
score_button_img = pygame.transform.scale(
    score_button_img, (WIDTH*1/5, WIDTH*1/5))
exit_button_img = pygame.image.load(res('exit_button.png'))
exit_button_img = pygame.transform.scale(
    exit_button_img, (WIDTH*1/5, WIDTH*1/5))
exit_game_button_img = pygame.transform.scale(
    exit_button_img, (WIDTH*1/7, WIDTH*1/7))
hand_img = pygame.image.load(res('hand.png'))
hand_img = pygame.transform.scale(hand_img, (WIDTH*1/3, WIDTH*1/3))
best_score_img = pygame.image.load(res('best_score.png'))
best_score_img = pygame.transform.scale(best_score_img, (WIDTH*1/3, WIDTH*1/3))
arrow_img = pygame.image.load(res('arrow2.png'))
arrow_img = pygame.transform.scale(arrow_img, (WIDTH*1/7, WIDTH*1/7))

guide_font = load_font_safe('RussoOne-Regular.ttf',
                            72 if platform == "android" else 36)
score_font = load_font_safe('RussoOne-Regular.ttf',
                            72 if platform == "android" else 36)

score_sound = pygame.mixer.Sound(res('score_sound.wav'))
apple_sound = pygame.mixer.Sound(res('apple_sound.wav'))
pygame.mixer.music.load(res('music.mp3'))
pygame.mixer.music.set_volume(0.02)


guide_wd = pygame.Surface((int(4/5*WIDTH), int(3/5*HEIGHT)), pygame.SRCALPHA)
guide_wd = guide_wd.convert_alpha()
guide_wd.fill((200, 195, 155))

bg_color = (86, 138, 53)

pole = pygame.Surface((pole_x, pole_y))


def docs():
    koord = [[[] for _ in range(po_x)] for _ in range(po_y)]
    counter_str = 0
    counter_stol = 0

    for j in range(po_y):
        greh_x = pole_x % po_x
        greh_y = pole_y % po_y
        if counter_stol == po_x:
            counter_str += 1
            counter_stol = 0

        for i in range(po_x):
            if greh_x != 0:
                kvadrat = pygame.Rect(
                    offset_x*i, offset_y*j, offset_x + 1, offset_y)
                greh_x -= 1
            elif greh_y != 0:
                kvadrat = pygame.Rect(
                    offset_x*i, offset_y*j, offset_x, offset_y+1)
                greh_y -= 1
            elif greh_y != 0 and greh_x != 0:
                kvadrat = pygame.Rect(
                    offset_x*i, offset_y*j, offset_x+1, offset_y+1)
                greh_x -= 1
                greh_y -= 1
            elif greh_y == 0 and greh_x == 0:
                kvadrat = pygame.Rect(
                    offset_x*i, offset_y*j, offset_x, offset_y)
            koord[counter_str][counter_stol] = [kvadrat.x, kvadrat.y,
                                                kvadrat.right-kvadrat.x, kvadrat.bottom - kvadrat.y]
            counter_stol += 1
    return koord


def perevod(str):
    if str == "Right":
        return 90
    if str == "Left":
        return -90
    if str == "Up":
        return 180
    if str == "Down":
        return 0


def angles(x, y):
    if x == 90 and y == 180:
        return -90
    if x == 90 and y == 0:
        return 0
    if x == -90 and y == 180:
        return 180
    if x == -90 and y == 0:
        return 90
    if x == 180 and y == 90:
        return 90
    if x == 180 and y == -90:
        return 0
    if x == 0 and y == 90:
        return 180
    if x == 0 and y == -90:
        return -90
    else:
        return None


images = {"head": head_img, "body": body_img,
          "tail": tail_img, "apple": apple_img, "angle": angle_img}

rotated = {name: {a: pygame.transform.rotate(img, a) for a in (
    0, 90, -90, 180)} for name, img in images.items()}


def smooth_rotate(arr):
    for i in range(len(arr)):
        if arr[i]["type"] != "head":
            if arr[i]["angle"] != arr[i-1]["angle"] and arr[i]["type"] == "body":
                arr[i]["type_img"] = rotated["angle"][arr[i-1]["angle"]]
            else:
                arr[i]["type_img"] = rotated[arr[i]["type"]][arr[i-1]["angle"]]


def smooth_insert(arr, snake_bodycounter):
    pred = arr[-1]
    arr[-1]["type"] = "body"
    arr[-1]["type_img"] = rotated["body"][arr[-1]["angle"]]

    vector = pred["vector"]

    if vector == "Right":
        new_row, new_col = pred["row"], pred["col"] - 1
    elif vector == "Left":
        new_row, new_col = pred["row"], pred["col"] + 1
    elif vector == "Down":
        new_row, new_col = pred["row"] - 1, pred["col"]
    elif vector == "Up":
        new_row, new_col = pred["row"] + 1, pred["col"]

    new_tail = {
        "type": "tail",
        "type_img": rotated["tail"][pred["angle"]],
        "row": new_row,
        "col": new_col,
        "angle": pred["angle"],
        "speed": snake_speed,
        "start_x": pred["current_x"],
        "start_y": pred["current_y"],
        "target_x": pred["current_x"],
        "target_y": pred["current_y"],
        "current_x": pred["current_x"],
        "current_y": pred["current_y"],
        "animation": 1,
        "vector": vector,
        "progress": 0
    }
    arr.append(new_tail)
    snake_bodycounter += 1


def spawn_apple(snake_arr):
    stroka = random.randint(1, po_y-1)
    stolbec = random.randint(1, po_x-1)
    while [stroka, stolbec] in snake_arr:
        stroka = random.randint(1, po_y-2)
        stolbec = random.randint(1, po_x-2)
    return (stroka, stolbec)


def smooth_angles(arr, images):
    for i in range(len(arr)-1, -1, -1):
        if i != 0:
            arr[i]["angle"] = arr[i-1]["angle"]
            arr[i]["vector"] = arr[i-1]["vector"]
            arr[i]["type_img"] = rotated[arr[i]["type"]][arr[i]["angle"]]
        else:
            if arr[i]["vector"] == "Right":
                arr[i]["angle"] = 90
            if arr[i]["vector"] == "Left":
                arr[i]["angle"] = -90
            if arr[i]["vector"] == "Up":
                arr[i]["angle"] = 180
            if arr[i]["vector"] == "Down":
                arr[i]["angle"] = 0
            arr[i]["type_img"] = rotated[arr[i]["type"]][arr[i]["angle"]]


def smooth_target(arr, path):
    hash = arr[0]
    row = hash["row"]
    col = hash["col"]
    if hash["type"] == "head":
        vector = hash["vector"]
        if vector == "Right":
            if col+1 < po_x:
                hash["target_x"] = koord[row][col+1][0]
                hash["target_y"] = koord[row][col+1][1]
            else:
                return 1
        if vector == "Left":
            if col-1 >= 0:
                hash["target_x"] = koord[row][col-1][0]
                hash["target_y"] = koord[row][col-1][1]
            else:
                return 1
        if vector == "Up":
            if row-1 >= 0:
                hash["target_x"] = koord[row-1][col][0]
                hash["target_y"] = koord[row-1][col][1]
            else:
                return 1
        if vector == "Down":
            if row+1 < po_y:
                hash["target_x"] = koord[row+1][col][0]
                hash["target_y"] = koord[row+1][col][1]
            else:
                return 1
    for i in range(len(arr)-1, 0, -1):
        arr[i]["target_x"] = arr[i-1]["current_x"]
        arr[i]["target_y"] = arr[i-1]["current_y"]


def smooth_movettg(hash, snake_speedX):
    vector = hash["vector"]

    if hash["animation"] == 1:
        hash["start_x"] = hash["current_x"]
        hash["start_y"] = hash["current_y"]
        hash["animation"] = 0
        hash["progress"] = 0

    if hash["animation"] == 0:
        hash["progress"] += 1
        t = hash["progress"] / snake_speedX
        hash["current_x"] = hash["start_x"] + \
            (hash["target_x"] - hash["start_x"]) * t
        hash["current_y"] = hash["start_y"] + \
            (hash["target_y"] - hash["start_y"]) * t

        if hash["progress"] >= snake_speedX:
            hash["current_x"] = hash["target_x"]
            hash["current_y"] = hash["target_y"]
            for r in range(po_y):
                for c in range(po_x):
                    if koord[r][c][0] == hash["current_x"] and koord[r][c][1] == hash["current_y"]:
                        hash["row"] = r
                        hash["col"] = c
                        break
            hash["animation"] = 1
            hash["progress"] = 0


def write_score(best_score=0, wr="r"):
    save_dir = get_save_dir()
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, "best_score.txt")

    if wr == "w":
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"{best_score}")
        return None
    elif wr == "r":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.readline().strip()
                return int(content) if content else 0
        except (FileNotFoundError, ValueError):
            return 0


koord = docs()

for j in range(po_y):
    greh_x = pole_x % po_x_f
    greh_y = pole_y % po_y_f
    for i in range(po_x):
        if greh_x != 0:
            kvadrat = pygame.Rect(offset_x*i, offset_y*j,
                                  offset_x + 1, offset_y)
            greh_x -= 1
        elif greh_y != 0:
            kvadrat = pygame.Rect(offset_x*i, offset_y*j, offset_x, offset_y+1)
            greh_y -= 1
        elif greh_y != 0 and greh_x != 0:
            kvadrat = pygame.Rect(offset_x*i, offset_y*j,
                                  offset_x+1, offset_y+1)
            greh_x -= 1
            greh_y -= 1
        elif greh_y == 0 and greh_x == 0:
            kvadrat = pygame.Rect(offset_x*i, offset_y*j, offset_x, offset_y)
        if (i+j) % 2 == 0:
            pygame.draw.rect(pole, (170, 216, 82, 235), kvadrat, 0)
        else:
            pygame.draw.rect(pole, (162, 208, 73, 235), kvadrat, 0)
pole_bg = pole.copy()

best_score = write_score()

my_snake = Snake()
pole_rect = pole.get_rect()
pole_rect.center = (WIDTH // 2, HEIGHT // 2)
screen_rect = screen.get_rect()

apple_score_img = pygame.transform.scale(
    apple_img, (offset_x+offset_x*scale*3, offset_x+offset_x*scale*3))
apple_rect = apple_score_img.get_rect(
    bottom=pole_rect.top, left=pole_rect.left)

best_score_img = pygame.transform.scale(
    best_score_img, (offset_x+offset_x*scale*10, offset_x+offset_x*scale*10))
best_score_rect = best_score_img.get_rect(
    center=(screen_rect.centerx - (offset_x+offset_x*scale*10)/2, HEIGHT/2))

while running:
    screen.fill(bg_color)
    pole.blit(pole_bg, (0, 0))

    if Start == 1:
        if sound != 0 and restart_music == 1:
            pygame.mixer.music.play(-1)
            restart_music = 0
        score = 0
        angle = []
        snake_x, snake_y = Snake.spawnsnake()
        current_x, current_y = koord[snake_x][snake_y][0], koord[snake_x][snake_y][1]
        head = rotated["head"][90]
        body = rotated["body"][90]
        tail = rotated["tail"][90]
        Start -= 1
        snake_bodymass = []
        snake_bodymass.append({"type_img": head, "target_x": koord[snake_x][snake_y+1][0], "target_y": koord[snake_x][snake_y+1][1], "row": snake_x, "col": snake_y, "angle": 90, "speed": snake_speed, "start_x": 0, "start_y": 0,
                               "current_x": koord[snake_x][snake_y][0], "current_y": koord[snake_x][snake_y][1], "animation": animation, "type": "head", "vector": "Right"})
        snake_bodymass.append({"type_img": body, "target_x": koord[snake_x][snake_y][0], "target_y": koord[snake_x][snake_y][1], "row": snake_x, "col": snake_y-1, "angle": 90, "speed": snake_speed, "start_x": 0, "start_y": 0,
                               "current_x": koord[snake_x][snake_y-1][0], "current_y": koord[snake_x][snake_y-1][1], "animation": animation, "type": "body", "vector": "Right"})
        snake_bodymass.append({"type_img": tail, "target_x": koord[snake_x][snake_y-1][0], "target_y": koord[snake_x][snake_y-1][1], "row": snake_x, "col": snake_y-2, "angle": 90, "speed": snake_speed, "start_x": 0, "start_y": 0,
                               "current_x": koord[snake_x][snake_y-2][0], "current_y": koord[snake_x][snake_y-2][1], "animation": animation, "type": "tail", "vector": "Right"})
        path = deque(maxlen=snake_bodycounter+2)
        for obj in snake_bodymass:
            path.append([obj["row"], obj["col"]])
        ax, ay = spawn_apple(path)

    if guide == 1:
        screen.blit(blur_menu_img, (0, 0))
        xc, yc = screen_rect.centerx, screen_rect.centery
        guide_wd_rect = guide_wd.get_rect(center=(xc, yc))
        pygame.draw.rect(screen, (200, 195, 155),
                         guide_wd_rect, border_radius=20)

        text = ["Как играть?", "Управляй змейкой ", "чтобы собирать яблоки.", "Чем больше соберёшь", "тем длиннее станет змейка!",
                "Не врежься в стены или в себя", "иначе игра закончится.", "Свайпай в нужном направлении", "чтобы змейка повернула"]
        text_offset = guide_wd_rect.top*1.2

        guide_font_big = load_font_safe(
            'RussoOne-Regular.ttf', 72 if platform == "android" else 36)
        guide_font_small = load_font_safe(
            'RussoOne-Regular.ttf', 48 if platform == "android" else 18)

        for i in range(len(text)):
            if text[i] == text[0]:
                guide_font = guide_font_big
            else:
                guide_font = guide_font_small
                if i % 2 == 0:
                    text_offset -= yc/24
                else:
                    text_offset += yc/12

            text_surface = guide_font.render(f'{text[i]}', True, (0, 0, 0))
            text_rect = text_surface.get_rect(centerx=(xc), top=text_offset)
            text_offset += yc/12
            screen.blit(text_surface, text_rect)
        screen.blit(head_img, head_img.get_rect(
            center=(xc, guide_wd_rect.bottom - yc/12)))
        menu = 0

    if menu == 1:
        screen.blit(menu_img, (0, 0))
        button_rect = start_button_img.get_rect(center=(WIDTH/2, HEIGHT*0.4))
        screen.blit(start_button_img, button_rect)
        guide_rect = guide_button_img.get_rect(
            topleft=(button_rect[0]/2, button_rect.bottom*1))
        screen.blit(guide_button_img, (guide_rect))
        exit_rect = exit_button_img.get_rect(
            topright=(button_rect.right+button_rect[0]/2, button_rect.bottom*1))
        screen.blit(exit_button_img, (exit_rect))
        if sound:
            sound_rect = sound_button_img.get_rect(
                centerx=(button_rect.centerx), top=button_rect.bottom*1.05)
            screen.blit(sound_button_img, (sound_rect))
        else:
            sound_rect = no_sound_button_img.get_rect(
                centerx=(button_rect.centerx), top=button_rect.bottom*1.05)
            screen.blit(no_sound_button_img, (sound_rect))

    if stop != 1:
        if second_guide != 1:
            if apple == 1:
                if score + 1 != best_score:
                    if sound != 0:
                        apple_sound.set_volume(0.08)
                        apple_sound.play()
                if score + 1 == best_score:
                    if sound != 0:
                        score_sound.set_volume(0.03)
                        score_sound.play()
                score += 1
                if best_score < score:
                    best_score += 1
                eated = 1
                ax, ay = spawn_apple(path)
                apple = 0
                snake_bodycounter += 1
                path = deque(maxlen=snake_bodycounter+2)
            if all(segment["animation"] == 1 for segment in snake_bodymass):

                if eated:
                    smooth_insert(snake_bodymass, snake_bodycounter)
                    eated = 0

                snake_bodymass[0]["vector"] = last_vector
                smooth_angles(snake_bodymass, images)

                if smooth_target(snake_bodymass, path) == 1:
                    lose = 1
                    if lose_timer == 0:
                        lose_timer = pygame.time.get_ticks()

                for obj in snake_bodymass:
                    if (snake_bodymass[0]["row"], snake_bodymass[0]["col"]) == (obj["row"], obj["col"]) and obj["type"] != "head":
                        lose = 1
                        if lose_timer == 0:
                            lose_timer = pygame.time.get_ticks()
                        stop = 1
                for obj in snake_bodymass:
                    path.append([obj["row"], obj["col"]])

            if ((ax, ay) == (snake_bodymass[0]["row"], snake_bodymass[0]["col"])):
                apple = 1

            for obj in snake_bodymass:
                smooth_movettg(obj, snake_speedX)

        else:
            hand_img_rect = hand_img.get_rect()
            hand_img_rect.center = (pole_x/2, pole_y/2)
            pole.blit(hand_img, hand_img_rect)
        for obj in snake_bodymass:
            draw_on_center(
                pole, obj["type_img"], obj["current_x"], obj["current_y"], offset_x, offset_y)
        if score >= best_score and score != 0:
            score_surface = score_font.render(f"{score}", True, (255, 215, 0))
        else:
            score_surface = score_font.render(
                f"{score}", True, (245, 252, 242))
        score_rect = score_surface.get_rect(
            bottom=pole_rect.top, left=apple_rect.right)
        exit_game_button_img_rect = arrow_img.get_rect(
            bottom=pole_rect.top, right=pole_rect.right)
        screen.blit(apple_score_img, apple_rect)
        screen.blit(score_surface, score_rect)
        screen.blit(arrow_img, exit_game_button_img_rect)

    draw_on_center(pole, apple_img,
                   koord[ax][ay][0], koord[ax][ay][1], offset_x, offset_y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.FINGERDOWN:
            swipe_start = (event.x * WIDTH, event.y * HEIGHT)

        if event.type == pygame.FINGERUP and swipe_start is not None:
            end_x = event.x * WIDTH
            end_y = event.y * HEIGHT
            dx = end_x - swipe_start[0]
            dy = end_y - swipe_start[1]

            if abs(dx) > abs(dy):
                if abs(dx) > swipe_min:
                    if dx > 0 and last_vector != "Left":
                        last_vector = "Right"
                    elif dx < 0 and last_vector != "Right":
                        last_vector = "Left"
            else:
                if abs(dy) > swipe_min:
                    if dy > 0 and last_vector != "Up":
                        last_vector = "Down"
                    elif dy < 0 and last_vector != "Down":
                        last_vector = "Up"
            swipe_start = None

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if menu:
                if x in range(button_rect.left, button_rect.right) and y in range(button_rect.top, button_rect.bottom):
                    stop = 0
                    menu = 0
                if x in range(exit_rect.left, exit_rect.right) and y in range(exit_rect.top, exit_rect.bottom):
                    running = False
                if x in range(sound_rect.left, sound_rect.right) and y in range(sound_rect.top, sound_rect.bottom):
                    if sound:
                        sound = 0
                        pygame.mixer.music.pause()
                    else:
                        sound = 1
                        pygame.mixer.music.unpause()
                if x in range(guide_rect.left, guide_rect.right) and y in range(guide_rect.top, guide_rect.bottom):
                    guide = 1
                    menu = 0
            else:
                if event.type == pygame.MOUSEBUTTONDOWN and guide != 1:
                    if second_guide == 1:
                        if pole_rect.collidepoint(x, y):
                            timer_start = pygame.time.get_ticks()
                            second_guide = 0
                            stop = 0
                            menu = 0
                if guide == 1 and x in range(0, WIDTH) and y in range(0, HEIGHT):
                    guide = 0
                    menu = 1
                if x in range(exit_game_button_img_rect.left, exit_game_button_img_rect.right) and y in range(exit_game_button_img_rect.top, exit_game_button_img_rect.bottom):
                    lose_timer = 0
                    stop = 1
                    menu = 1
                    Start = 1
                    lose = 0
                    last_vector = "Right"
                    second_guide = 1
                    write_score(best_score=best_score, wr="w")

            if lose == 1 and ((pygame.time.get_ticks() - lose_timer) > 400):
                lose_timer = 0
                stop = 1
                menu = 1
                Start = 1
                lose = 0
                last_vector = "Right"
                second_guide = 1
                write_score(best_score=best_score, wr="w")

        if event.type == pygame.KEYDOWN and guide != 1:
            if event.key == pygame.K_p:
                stop = 0
            if event.key == pygame.K_u:
                stop = 1
            if event.key == pygame.K_w:
                if last_vector != "Down":
                    last_vector = "Up"
            if event.key == pygame.K_a:
                if last_vector != "Right":
                    last_vector = "Left"
            if event.key == pygame.K_s:
                if last_vector != "Up":
                    last_vector = "Down"
            if event.key == pygame.K_d:
                if last_vector != "Left":
                    last_vector = "Right"

    if stop != 1:
        screen.blit(pole, pole_rect)

    if lose == 1:
        screen.blit(lose_img, (0, 0))
        score_surface = score_font.render(
            f"{best_score}", True, (245, 252, 242))
        score_rect = score_surface.get_rect(
            centery=best_score_rect.centery, centerx=screen_rect.centerx + (offset_x+offset_x*scale*10)/2)
        screen.blit(best_score_img, best_score_rect)
        screen.blit(score_surface, score_rect)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()
sys.exit()
