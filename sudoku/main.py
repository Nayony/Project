import pygame
import sys
import os
import json
import random
import copy
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def res(*path):
    return os.path.join(BASE_DIR, *path)


if sys.platform == "android":
    from android.storage import app_storage_path
    SAVE_DIR = app_storage_path()
else:
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_FILE = os.path.join(SAVE_DIR, "sudoku_save.json")

def save_arrays(arr, norm):
    """Сохраняем оба массива: текущее состояние и решение"""
    game_state = {
        "arr": arr,  
        "norm": norm  
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(game_state, f, indent=2)

def load_arrays():
    """Загружаем оба массива"""
    if not os.path.exists(SAVE_FILE):
        return None, None

    try:
        with open(SAVE_FILE, "r") as f:
            game_state = json.load(f)

        arr = game_state.get("arr")
        norm = game_state.get("norm")

        if arr is not None and norm is not None and len(arr) == 81 and len(norm) == 81:
            return (arr, norm)
        else:
            return None, None

    except Exception as e:
        return None, None


podstroka = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
poleX81 = [0 for _ in range(81)]
poleX0 = [0 for _ in range(81)]
def fssk():
    arr, strn, stol, kv = [], [], [], []
    for x in range(0, 81):
        strn.append(x // 9)
        stol.append(x % 9)
        kv.append((strn[x] // 3) * 3 + (stol[x] // 3))
    arr.extend([strn, stol, kv])
    return arr


koordinaty = fssk()

def fssk_re(strn, stol): return strn * 9 + stol

def docx(target, field):
    stroka, stolbec, kv = [], [], []
    for x in range(0, 81):
        if x != target:
            if koordinaty[0][x] == koordinaty[0][target]:
                stroka.append(field[x])
            if koordinaty[1][x] == koordinaty[1][target]:
                stolbec.append(field[x])
            if koordinaty[2][x] == koordinaty[2][target]:
                kv.append(field[x])
    return (stroka, stolbec, kv)

def pole(field):
    nums = [1,2,3,4,5,6,7,8,9]
    if 0 not in field:
        return field.copy()
    for x in range(81):
        if field[x] == 0:
            r, c, b = docx(x, field)
            for num in range(1, 10):
                num = random.choice(nums)
                if num not in r and num not in c and num not in b:
                    field[x] = num
                    res = pole(field)
                    if res is not None:
                        return res
                    field[x] = 0
                else:
                    nums.remove(num)
            break
    return None
   
def nuller(field):
    while True:
        idx = list(range(81))
        cp = field.copy()
        colvo = 0
        need = 2
        while colvo < need:
            a = random.choice(idx)
            backup = cp[a]
            cp[a] = 0
            if solver(cp)[0] == 1:
                idx.remove(a)
                colvo+= 1
            else:
                cp[a] = backup
        if colvo >= need:
            return cp
                

def solver(field, limit=2):
    if 0 not in field:
        return [1, [field.copy()]]
    total, solutions = 0, []
    for x in range(81):
        if field[x] == 0:
            r, c, b = docx(x, field)
            for num in range(1, 10):
                if num not in r and num not in c and num not in b:
                    field[x] = num
                    res = solver(field, limit)
                    total += res[0]
                    solutions.extend(res[1])
                    field[x] = 0
                    if total >= limit:
                        return [total, solutions]
            break
    return [total, solutions]


loaded_arr, loaded_norm = load_arrays()

def generate_and_save():
    poleX0 = [0 for _ in range(81)]
    poleX81 = pole(poleX0)
    new_b = nuller(poleX81)
    new_a = solver(new_b)
    while new_a[0] != 1:
        new_b = nuller(poleX81)
        new_a = solver(new_b)
    new_arr = new_b
    new_norm = new_a[1][0]
    save_arrays(new_arr, new_norm)
    print("Saves done",new_arr, new_norm)


if loaded_arr is None or loaded_norm is None:
    poleX81 = pole(poleX0)
    b = nuller(poleX81)
    a = solver(b)
    while a[0] != 1:
        b = nuller(poleX81)
        a = solver(b)
    arr = b
    norm = a[1][0]
else:
    arr = load_arrays()[0]
    norm = load_arrays()[1]
pygame.init()


info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h
WIDTH = 360
HEIGHT = 740
pygame.display.set_caption("Sudoku")

offset = WIDTH//40

step = (WIDTH - (offset * 2)) // 9


grid_height = step * 9

font = pygame.font.SysFont("Arial", int(step * 0.6))
font_ui = pygame.font.SysFont("Arial", int(step * 0.5))
font_notes = pygame.font.SysFont("Arial", int(step * 0.4))

delta_y = HEIGHT * 0.1
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def get_font(size_multiplier):
    return pygame.font.SysFont("Arial", int(WIDTH * size_multiplier))


font = get_font(0.08)
font_ui = get_font(0.08)
font_notes = get_font(0.05)
font_sg = get_font(0.2)
font_menu = get_font(0.13)

start_game = 0
menu = True
running = True
selected_num, cur_num, picked, miss = 0, 0, False, 0
timer, fake_timer, ugadano, pravda = 0, 0, 0, True
selected, number_9, add, fake_add = [], [], [], []
notes_mode = False
alpha = 255
true_alpha = 255
R, G, B = 0, 0, 0
restart = False
notes_grid = [set() for _ in range(81)]

keypad_y = delta_y + grid_height + 20

btn_y = keypad_y + step + 60
btn_width = (9 * step - 10) // 2
btn_note_rect = pygame.Rect(offset, btn_y, btn_width, int(step * 1.2))
btn_reset_rect = pygame.Rect(
    offset + btn_width + 10, btn_y, btn_width, int(step * 1.2))

bg_original = pygame.image.load(res("bg.png"))
bg = pygame.transform.scale(bg_original, (WIDTH, HEIGHT))

color_black = (0, 0, 0)
start_surf = font_menu.render("Начать", True, color_black)
start_rect = start_surf.get_rect(center=(WIDTH * 0.5, HEIGHT // 2))

exit_surf = font_menu.render("Выход", True, color_black)
exit_rect_menu = exit_surf.get_rect(center=(WIDTH * 0.5, HEIGHT * 0.6))

s_text = font_sg.render("SUDOKU", True, color_black)
s_rect = s_text.get_rect(center=(WIDTH * 0.5, HEIGHT // 5))

g_text = font_sg.render("GAME", True, color_black)
g_rect = g_text.get_rect(center=(WIDTH * 0.5, HEIGHT * 0.27))


while running:
    if restart:
        arr = []
        norm = []
        arr = load_arrays()[0]
        norm = load_arrays()[1]
        start_game = 0
        menu = True
        selected_num, cur_num, picked, miss = 0, 0, False, 0
        timer, fake_timer, ugadano, pravda = 0, 0, 0, True
        selected, number_9, add, fake_add = [], [], [], []
        notes_mode = False
        alpha = 255
        true_alpha = 255
        R, G, B = 0, 0, 0
        notes_grid = [set() for _ in range(81)]
        print("Restart",arr,norm)
        restart = False
        start_game = 0
        miss = 0
    if start_game == 0:
        threading.Thread(
            target=generate_and_save,
            daemon=True
        ).start()
    start_game += 1
    if menu == True:

        screen.fill((232, 231, 213))
        screen.blit(bg, (0, 0))

        screen.blit(exit_surf, exit_rect_menu)

        screen.blit(start_surf, start_rect)

        screen.blit(s_text, s_rect)

        screen.blit(g_text, g_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if exit_rect_menu.collidepoint(x, y):
                    running = False
                if start_rect.collidepoint(x, y):
                    menu = False

        pygame.display.update()
        clock.tick(60)
    else:
        Z = 0
        screen.fill((232, 231, 213))
        exit_text = font_ui.render("Выход", True, (0, 0, 0))
        exit_rect = exit_text.get_rect(center=(WIDTH // 9 * 8, delta_y // 2))
        screen.blit(exit_text, exit_rect)
        pygame.mouse.set_visible(True)

        if miss < 4 and arr != norm:

            kvsurface = font_ui.render(f'Ошибки: {miss}/3', True, (0, 0, 0))
            error_text = font_ui.render(f'Ошибки: {miss}/3', True, (0, 0, 0))
            error_rect = error_text.get_rect(center=(WIDTH // 2, delta_y // 2))
            screen.blit(error_text, error_rect)

            for i in range(10):
                w = 3 if i % 3 == 0 else 1
                pygame.draw.line(screen, "black", (offset, delta_y +
                                 i * step), (WIDTH - offset, delta_y + i * step), w)
                pygame.draw.line(screen, "black", (offset + i * step,
                                 delta_y), (offset + i * step, delta_y + 9 * step), w)

            if timer > 0 and add:
                timer -= 1
                true_alpha -= 2
                h = pygame.Surface((step - 1, step - 1), pygame.SRCALPHA)
                h.fill((84, 232, 168, true_alpha))
                if offset < x < WIDTH - offset and delta_y < y < delta_y + 9 * step:
                        col, row = (x - offset) // step, (y - delta_y) // step
                        pos = int(row * 9 + col)

                        selected, number_9 = [], []
                        for nx in range(9):
                            selected.append((nx, row))
                        for ny in range(9):
                            selected.append((col, ny))

                        if arr[pos] == 0:
                            if picked:
                                if notes_mode:
                                    if cur_num in notes_grid[pos]:
                                        notes_grid[pos].remove(cur_num)
                                    else:
                                        notes_grid[pos].add(cur_num)
                                else:
                                    if cur_num == norm[pos]:
                                        arr[pos] = cur_num
                                        add.append([col, row, cur_num])
                                        timer = 120
                                        true_alpha = 255
                                        notes_grid[pos].clear()
                                    else:
                                        fake_timer = 120
                                        alpha = 255
                                        R = 0
                                        G = 0
                                        B = 0
                                        fake_add.append([col, row, cur_num])
                                        miss, pravda = miss + 1, False
                        else:

                            for kvad in range(81):
                                if koordinaty[2][pos] == koordinaty[2][kvad]:
                                    selected.append(
                                        (koordinaty[1][kvad], koordinaty[0][kvad]))
                                if arr[pos] == arr[kvad]:
                                    number_9.append(
                                        (koordinaty[1][kvad], koordinaty[0][kvad]))
                screen.blit(h, (add[-1][0] * step + offset +
                            1, add[-1][1] * step + delta_y + 1))

            if fake_timer > 0 and fake_add and not pravda:
                fake_timer -= 1
                alpha -= 2
                R += 1.1
                G += 1.1
                B += 1.2
                h = pygame.Surface((step - 1, step - 1), pygame.SRCALPHA)
                h.fill((255, 0, 0, alpha))
                screen.blit(
                    h, (fake_add[-1][0] * step + offset + 1, fake_add[-1][1] * step + delta_y + 1))
                txt = font.render(f'{fake_add[-1][2]}', True, (R, G, B))
                screen.blit(txt, txt.get_rect(center=(
                    fake_add[-1][0] * step + offset + step / 2, fake_add[-1][1] * step + delta_y + step / 2)))
            elif fake_timer <= 0:
                pravda = True

            keypad_y = delta_y + (9 * step) + 10
            for num in range(9):

                num_rect = pygame.Rect(
                    num * step + 1*offset, keypad_y+2*offset, step, step+2*offset)
                if selected_num == num + 1:
                    pygame.draw.rect(screen, (106, 150, 153, 150),
                                     num_rect, border_radius=5)

                val = font.render(f'{num+1}', True, (0, 0, 0))
                screen.blit(val, val.get_rect(center=num_rect.center))

            index_y = 0
            for row in range(9):
                index_x = 0
                for col in range(9):

                    rect_pos = (offset + index_x + 1, delta_y + index_y + 1)
                    if (col, row) in selected:
                        h = pygame.Surface(
                            (step - 1, step - 1), pygame.SRCALPHA)
                        h.fill((106, 150, 153, 60))
                        screen.blit(h, rect_pos)
                    if (col, row) in number_9:
                        h = pygame.Surface(
                            (step - 1, step - 1), pygame.SRCALPHA)
                        h.fill((106, 150, 153, 170))
                        screen.blit(h, rect_pos)

                    center = (offset + index_x + step // 2,
                              delta_y + index_y + step // 2)
                    if arr[Z] != 0:
                        txt = font.render(f'{arr[Z]}', True, (0, 0, 0))
                        screen.blit(txt, txt.get_rect(center=center))
                    elif notes_grid[Z]:
                        for note in notes_grid[Z]:
                            nx = ((note - 1) % 3) * (step // 3) + 5
                            ny = ((note - 1) // 3) * (step // 3) + 2
                            n_txt = font_notes.render(
                                str(note), True, (100, 100, 100))
                            screen.blit(n_txt, (offset + index_x +
                                        nx, delta_y + index_y + ny))

                    index_x += step
                    Z += 1
                index_y += step

            pygame.draw.rect(screen, (170, 200, 170) if notes_mode else (
                200, 200, 200), btn_note_rect, border_radius=10)
            screen.blit(font_ui.render("Заметки", True, "black"), font_ui.render(
                "Заметки", True, "black").get_rect(center=btn_note_rect.center))
            pygame.draw.rect(screen, (200, 170, 170),
                             btn_reset_rect, border_radius=10)
            screen.blit(font_ui.render("Сброс", True, "black"), font_ui.render(
                "Сброс", True, "black").get_rect(center=btn_reset_rect.center))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if exit_rect.collidepoint(x, y):
                        menu = True
                    if btn_note_rect.collidepoint(x, y):
                        notes_mode = not notes_mode
                    if btn_reset_rect.collidepoint(x, y):
                        cur_num = selected_num = 0
                        picked = False
                        selected = number_9 = []

                    if keypad_y + 2*offset < y < keypad_y + step + 4*offset:
                        chosen = (x - offset) // step + 1
                        if 1 <= chosen <= 9:
                            if selected_num == chosen:
                                selected_num = cur_num = 0
                                picked = False
                            else:
                                selected_num = cur_num = int(chosen)
                                picked = True

                    if offset < x < WIDTH - offset and delta_y < y < delta_y + 9 * step:
                        col, row = (x - offset) // step, (y - delta_y) // step
                        pos = int(row * 9 + col)

                        selected, number_9 = [], []
                        for nx in range(9):
                            selected.append((nx, row))
                        for ny in range(9):
                            selected.append((col, ny))

                        if arr[pos] == 0:
                            if picked:
                                if notes_mode:
                                    if cur_num in notes_grid[pos]:
                                        notes_grid[pos].remove(cur_num)
                                    else:
                                        notes_grid[pos].add(cur_num)
                                else:
                                    if cur_num == norm[pos]:
                                        arr[pos] = cur_num
                                        add.append([col, row, cur_num])
                                        timer = 120
                                        true_alpha = 255
                                        notes_grid[pos].clear()
                                    else:
                                        fake_timer = 120
                                        alpha = 255
                                        R = 0
                                        G = 0
                                        B = 0
                                        fake_add.append([col, row, cur_num])
                                        miss, pravda = miss + 1, False
                        else:

                            for kvad in range(81):
                                if koordinaty[2][pos] == koordinaty[2][kvad]:
                                    selected.append(
                                        (koordinaty[1][kvad], koordinaty[0][kvad]))
                                if arr[pos] == arr[kvad]:
                                    number_9.append(
                                        (koordinaty[1][kvad], koordinaty[0][kvad]))

            pygame.display.update()
            clock.tick(60)
        else:
            if arr == norm:
                msg = "ПОБЕДА!"

            else:
                msg = "ИГРА ОКОНЧЕНА"
            screen.fill((232, 231, 213))
            #screen.blit(exit_surf, exit_rect_menu)
            end_txt = font.render(msg, True, "black")
            screen.blit(end_txt, end_txt.get_rect(
                center=(WIDTH // 2, HEIGHT // 2)))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    menu = True
                    restart = True
        pygame.display.update()
        clock.tick(60)

pygame.quit()
