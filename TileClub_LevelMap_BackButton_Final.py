import os
import json
import random
import pygame
import math
pygame.init()

try:
    pygame.mixer.init()
except pygame.error:
    pass

try:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
except pygame.error:
    screen = pygame.display.set_mode((900, 600))

WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Tile Club - Match Puzzle")
clock = pygame.time.Clock()
FPS = 30

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
TILES_DIR = os.path.join(ASSETS_DIR, "tiles")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
BUTTONS_DIR = os.path.join(ASSETS_DIR, "buttons")
SAVE_FILE = os.path.join(BASE_DIR, "progress.json")

BACKGROUND_COLOR = (35, 24, 58)
PURPLE = (100, 60, 160)
DARK_PURPLE = (43, 27, 70)
LIGHT_PURPLE = (190, 155, 240)
GOLD = (255, 205, 90)
WHITE = (255, 255, 255)
RED = (240, 90, 110)
GREEN = (100, 220, 150)
SKY = (112, 176, 205)
MOUNTAIN = (75, 103, 113)
MOUNTAIN_LIGHT = (205, 221, 218)
PATH_COLOR = (226, 196, 125)
LOCK_COLOR = (80, 77, 94)

# Adaptive UI scale: use a phone-sized reference in portrait and cap scaling
# so high-resolution devices do not produce oversized buttons and text.
if HEIGHT >= WIDTH:
    UI_SCALE = max(0.45, min(1.15, WIDTH / 480, HEIGHT / 900))
else:
    UI_SCALE = max(0.45, min(1.0, WIDTH / 900, HEIGHT / 600))


def scaled(value):
    return max(1, int(value * UI_SCALE))


def get_font(size, bold=False):
    return pygame.font.SysFont("arial", scaled(size), bold=bold)


FONT_SMALL = get_font(18)
FONT_MEDIUM = get_font(24, True)
FONT_LARGE = get_font(38, True)
FONT_TITLE = get_font(48, True)

LEVEL_PAIRS = {
    1: 6,
    2: 8,
    3: 10,
    4: 12,
    5: 14,
    6: 16,
    7: 18,
    8: 20,
    9: 21,
    10: 21,
}

LEVEL_MAX_MOVES = {
    1: 20,
    2: 22,
    3: 24,
    4: 26,
    5: 28,
    6: 30,
    7: 32,
    8: 34,
    9: 36,
    10: 38,
}

LEVEL_TIME_LIMITS = {
    1: 120,
    2: 120,
    3: 120,
    4: 120,
    5: 120,
    6: 120,
    7: 120,
    8: 120,
    9: 120,
    10: 120,
}

LEVEL_THREE_STAR_MOVES_LEFT = {
    1: 10,
    2: 10,
    3: 10,
    4: 9,
    5: 9,
    6: 9,
    7: 8,
    8: 8,
    9: 8,
    10: 8,
}

TOTAL_LEVELS = len(LEVEL_PAIRS)
current_level = 1
current_page = "menu"
running = True
show_level_popup = False

TILE_FILES = [
    "tile_strawberry.png",
    "tile_grapes.png",
    "tile_orange.png",
    "tile_apple.png",
    "tile_banana.png",
    "tile_watermelon.png",
    "tile_lemon.png",
    "tile_pink_flower.png",
    "tile_white_flower.png",
    "tile_purple_flower.png",
    "tile_blue_flower.png",
    "tile_leaf.png",
    "tile_mushroom.png",
    "tile_butterfly.png",
    "tile_ladybug.png",
    "tile_paw.png",
    "tile_star.png",
    "tile_heart.png",
    "tile_clover.png",
    "tile_pineapple.png",
    "tile_snowflake.png",
]


def load_progress():
    data = {
        "stars": {
            str(level): 0
            for level in range(1, TOTAL_LEVELS + 1)
        },
        "best_moves": {},
        "coins": 0,
        "hearts": 5,
    }

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)

        if isinstance(saved, dict):
            stars = saved.get("stars", {})
            best_moves = saved.get("best_moves", {})

            try:
                data["coins"] = max(0, int(saved.get("coins", 0)))
            except (TypeError, ValueError):
                data["coins"] = 0

            try:
                data["hearts"] = max(0, min(5, int(saved.get("hearts", 5))))
            except (TypeError, ValueError):
                data["hearts"] = 5

            if isinstance(stars, dict):
                for level in range(1, TOTAL_LEVELS + 1):
                    try:
                        data["stars"][str(level)] = max(
                            0,
                            min(3, int(stars.get(str(level), 0)))
                        )
                    except (TypeError, ValueError):
                        pass

            if isinstance(best_moves, dict):
                for key, value in best_moves.items():
                    try:
                        if 1 <= int(key) <= TOTAL_LEVELS:
                            moves_value = int(value)
                            if moves_value > 0:
                                data["best_moves"][str(int(key))] = moves_value
                    except (TypeError, ValueError):
                        pass

    except (OSError, ValueError, TypeError):
        pass

    return data


progress = load_progress()


def save_progress():
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump(progress, file, indent=4)
    except OSError:
        pass


def get_stars(level):
    return int(progress["stars"].get(str(level), 0))


def is_level_unlocked(level):
    if level == 1:
        return True

    return get_stars(level - 1) == 3


def get_current_unlocked_level():
    unlocked = 1

    for level in range(2, TOTAL_LEVELS + 1):
        if is_level_unlocked(level):
            unlocked = level
        else:
            break

    return unlocked


def load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError, OSError):
        return None


background = load_image(
    os.path.join(IMAGES_DIR, "background.png")
)

level_map_image = load_image(
    os.path.join(IMAGES_DIR, "level_map.png")
)

card_back = load_image(
    os.path.join(TILES_DIR, "card_back.png")
)

button_images = {
    "play": load_image(
        os.path.join(BUTTONS_DIR, "button_play.png")
    ),
    "settings": load_image(
        os.path.join(BUTTONS_DIR, "button_settings.png")
    ),
    "restart": load_image(
        os.path.join(BUTTONS_DIR, "button_restart.png")
    ),
    "back": (
        load_image(os.path.join(BUTTONS_DIR, ""))
    ),
    "exit": (
        load_image(os.path.join(BUTTONS_DIR, "button_exit.png"))
        or load_image(os.path.join(BASE_DIR, "button_exit.png"))
    ),
}

ICON_FILES = {
    "crown": ("icon_crown.png", "icon_crown.png"),
    "home": ("icon_home.png", "icown_home.png"),
    "lock": ("icon_lock.png", "icone_lock.png"),
    "music": ("icon_music.png", "icon_music.png"),
    "sound": ("icon_sound.png", "icon_sound.png"),
    "star": ("icon_star.png", "icon_star.png"),
    "trophy": ("icon_trophy.png", "icon_trophy.png"),
    "coin": ("icon_coin.png", "coin.png"),
    "heart": ("icon_heart.png", "heart.png"),
}

icon_images = {}

for icon_name, filenames in ICON_FILES.items():
    for filename in filenames:
        icon = load_image(os.path.join(BUTTONS_DIR, filename))
        if icon is not None:
            icon_images[icon_name] = icon
            break

tile_images = {}

for index, filename in enumerate(TILE_FILES):
    image = load_image(os.path.join(TILES_DIR, filename))

    if image is not None:
        tile_images[index] = image

background_scaled = None
level_map_scaled = None
scaled_tile_images = {}
scaled_card_back = None

music_enabled = True
music_volume = 0.35
music_path = os.path.join(MUSIC_DIR, "background.mp3")

try:
    if os.path.isfile(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1)
except pygame.error:
    pass

overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
overlay.fill((20, 10, 35, 175))

card_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
card_overlay.fill((20, 10, 35, 90))


def prepare_images():
    global background_scaled, level_map_scaled
    global scaled_tile_images, scaled_card_back

    if background:
        background_scaled = pygame.transform.smoothscale(
            background, (WIDTH, HEIGHT)
        )

    if level_map_image:
        level_map_scaled = pygame.transform.smoothscale(
            level_map_image, (WIDTH, HEIGHT)
        )

    scaled_tile_images = {}

    for tile_id, image in tile_images.items():
        scaled_tile_images[tile_id] = image

    scaled_card_back = card_back


prepare_images()

play_width = min(int(WIDTH * 0.42), scaled(300))
play_height = max(scaled(54), int(HEIGHT * 0.11))

play_image = button_images["play"]

if play_image:
    image_ratio = play_image.get_width() / max(
        1, play_image.get_height()
    )

    play_width = min(int(WIDTH * 0.65), scaled(340))
    play_height = max(1, int(play_width / image_ratio))

    max_play_height = int(HEIGHT * 0.16)

    if play_height > max_play_height:
        play_height = max_play_height
        play_width = max(1, int(play_height * image_ratio))

play_rect = pygame.Rect(
    (WIDTH - play_width) // 2,
    int(HEIGHT * 0.48 - play_height / 2),
    play_width,
    play_height,
)

levels_menu_rect = pygame.Rect(
    (WIDTH - min(scaled(270), int(WIDTH * 0.65))) // 2,
    play_rect.bottom + scaled(18),
    min(scaled(270), int(WIDTH * 0.65)),
    scaled(48),
)

exit_menu_rect = pygame.Rect(
    scaled(14),
    scaled(14),
    scaled(82),
    scaled(36),
)

settings_rect = pygame.Rect(
    WIDTH - scaled(146),
    scaled(14),
    scaled(132),
    scaled(36),
)

back_settings_rect = pygame.Rect(
    scaled(12),
    scaled(12),
    scaled(105),
    scaled(42),
)

music_rect = pygame.Rect(
    (WIDTH - min(int(WIDTH * 0.72), scaled(450))) // 2,
    int(HEIGHT * 0.42),
    min(int(WIDTH * 0.72), scaled(450)),
    scaled(12),
)

settings_button_width = min(int(WIDTH * 0.48), scaled(330))
settings_button_height = max(scaled(44), int(HEIGHT * 0.10))

music_toggle_rect = pygame.Rect(
    (WIDTH - settings_button_width) // 2,
    int(HEIGHT * 0.56 - settings_button_height / 2),
    settings_button_width,
    settings_button_height,
)

map_back_rect = pygame.Rect(
    scaled(10),
    scaled(8),
    scaled(78),
    scaled(32),
)

map_title_y = scaled(48)

game_back_rect = pygame.Rect(
    scaled(10),
    scaled(8),
    scaled(78),
    scaled(32),
)

restart_rect = pygame.Rect(
    WIDTH - scaled(100),
    scaled(8),
    scaled(90),
    scaled(32),
)

win_restart_rect = pygame.Rect(
    WIDTH // 2 - scaled(100),
    HEIGHT // 2 + scaled(65),
    scaled(200),
    scaled(46),
)

win_continue_rect = pygame.Rect(
    WIDTH // 2 - scaled(100),
    HEIGHT // 2 + scaled(10),
    scaled(200),
    scaled(46),
)

lose_retry_rect = pygame.Rect(
    WIDTH // 2 - scaled(100),
    HEIGHT // 2 + scaled(15),
    scaled(200),
    scaled(46),
)

lose_map_rect = pygame.Rect(
    WIDTH // 2 - scaled(100),
    HEIGHT // 2 + scaled(72),
    scaled(200),
    scaled(46),
)

moves = 0
matched_pairs = 0
first_card = None
second_card = None
match_time = 0
cards = []
revealed = set()
matched = set()
game_won = False
game_lost = False
earned_stars = 0
game_start_ticks = 0
lose_reason = "moves"

GRID_COLS = 7
GRID_ROWS = 6
TOTAL_PAIRS = LEVEL_PAIRS[current_level]
CARD_SIZE = 1
MARGIN = scaled(12)
GAP = scaled(8)
HEADER_HEIGHT = scaled(68)
GRID_TOP = HEADER_HEIGHT + scaled(8)
GRID_BOTTOM = HEIGHT - scaled(12)
GRID_WIDTH = 1
GRID_LEFT = 0


def draw_text(text, font, color, position, center=True):
    surface = font.render(str(text), True, color)

    if center:
        rect = surface.get_rect(center=position)
    else:
        rect = surface.get_rect(topleft=position)

    screen.blit(surface, rect)
    return rect


def draw_background():
    if background_scaled:
        screen.blit(background_scaled, (0, 0))
    else:
        screen.fill(BACKGROUND_COLOR)


def draw_circle_button(surface, center, radius, icon_name, enabled=True, icon_scale=0.92):
    diameter = radius * 2 + scaled(6)
    button_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    button_center = (diameter // 2, diameter // 2)

    pygame.draw.circle(
        button_surface,
        (15, 8, 28, 105),
        (button_center[0] + scaled(2), button_center[1] + scaled(3)),
        radius,
    )
    pygame.draw.circle(button_surface, GOLD, button_center, radius)
    pygame.draw.circle(
        button_surface,
        PURPLE if enabled else DARK_PURPLE,
        button_center,
        max(1, radius - scaled(3)),
    )
    pygame.draw.circle(
        button_surface,
        LIGHT_PURPLE,
        button_center,
        max(1, radius - scaled(7)),
        max(1, scaled(1)),
    )

    icon = icon_images.get(icon_name)
    if icon is not None:
        icon_size = max(1, int(radius * 2 * icon_scale))
        icon = pygame.transform.smoothscale(icon, (icon_size, icon_size))
        icon_rect = icon.get_rect(center=button_center)
        button_surface.blit(icon, icon_rect)

    rect = button_surface.get_rect(center=center)
    surface.blit(button_surface, rect)
    return pygame.Rect(
        center[0] - radius,
        center[1] - radius,
        radius * 2,
        radius * 2,
    )


def circle_button_clicked(position, center, radius):
    dx = position[0] - center[0]
    dy = position[1] - center[1]
    return dx * dx + dy * dy <= radius * radius


def draw_button(rect, text, color, font=None, image_key=None):
    image = button_images.get(image_key) if image_key else None

    if image:
        if image_key in ("back", "exit"):
            image_width, image_height = image.get_size()
            fit_scale = min(
                rect.width / image_width,
                rect.height / image_height,
            )
            draw_size = (
                max(1, int(image_width * fit_scale)),
                max(1, int(image_height * fit_scale)),
            )
            resized = pygame.transform.smoothscale(image, draw_size)
            image_rect = resized.get_rect(center=rect.center)
            screen.blit(resized, image_rect)
        else:
            resized = pygame.transform.smoothscale(
                image, (rect.width, rect.height)
            )
            screen.blit(resized, rect)
    else:
        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=scaled(10),
        )

        pygame.draw.rect(
            screen,
            GOLD,
            rect,
            width=max(1, scaled(2)),
            border_radius=scaled(10),
        )

    if text and not image:
        draw_text(
            text,
            font or FONT_MEDIUM,
            WHITE,
            rect.center,
        )


def draw_stars(center, count, radius):
    """Draw three compact, polished stars beneath a level marker."""
    spacing = radius * 2 + scaled(5)
    total_width = spacing * 2

    for index in range(3):
        x = center[0] - total_width // 2 + index * spacing
        y = center[1]
        points = []

        for point in range(10):
            angle = -90 + point * 36
            distance = radius if point % 2 == 0 else radius * 0.43
            px = x + distance * math.cos(math.radians(angle))
            py = y + distance * math.sin(math.radians(angle))
            points.append((int(px), int(py)))

        earned = index < count
        color = GOLD if earned else (65, 61, 78)
        pygame.draw.polygon(screen, (28, 18, 42), points)
        shifted = [(px, py - scaled(1)) for px, py in points]
        pygame.draw.polygon(screen, color, shifted)
        pygame.draw.polygon(
            screen,
            (255, 239, 180) if earned else (126, 117, 143),
            shifted,
            width=max(1, scaled(1)),
        )


def get_level_positions():
    # Normalized centers follow the visible yellow road on level_map.png.
    # The image is stretched to the screen, so normalized coordinates adapt too.
    road_points = [
        (0.78, 0.935),  # bottom-right entrance
        (0.62, 0.895),  # lower road heading left
        (0.34, 0.855),  # lower-left bend
        (0.35, 0.735),  # road turning upward/right
        (0.66, 0.675),  # approach to the bridge
        (0.73, 0.575),  # beyond the bridge
        (0.43, 0.485),  # left side of the middle loop
        (0.29, 0.365),  # upper-left bend
        (0.62, 0.285),  # upper-right loop
        (0.45, 0.105),  # top road finish
    ]

    points = road_points[:TOTAL_LEVELS]
    radius = scaled(27)
    top_safe = max(scaled(132), map_title_y + scaled(62))
    bottom_safe = HEIGHT - scaled(82)

    return [
        (
            max(radius + scaled(3), min(WIDTH - radius - scaled(3), int(WIDTH * x))),
            max(top_safe, min(bottom_safe, int(HEIGHT * y))),
        )
        for x, y in points
    ]


def draw_map():
    if level_map_scaled:
        screen.blit(level_map_scaled, (0, 0))
        screen.blit(card_overlay, (0, 0))
    else:
        draw_background()
        screen.blit(overlay, (0, 0))

    # Use the same text-and-border Back button as the Game scene.
    # No image is loaded or drawn here, so there is no blank duplicate rectangle.
    draw_button(map_back_rect, "BACK", DARK_PURPLE, font=FONT_SMALL)

    draw_text("LEVEL MAP", get_font(30, True), GOLD, (WIDTH // 2, scaled(40)))

    hud_y = scaled(82)
    counter_h = scaled(34)
    counter_w = min(scaled(112), int(WIDTH * 0.30))
    heart_rect = pygame.Rect(WIDTH - counter_w * 2 - scaled(20), hud_y, counter_w, counter_h)
    coin_rect = pygame.Rect(WIDTH - counter_w - scaled(10), hud_y, counter_w, counter_h)

    for rect in (heart_rect, coin_rect):
        pygame.draw.rect(screen, (37, 22, 59), rect, border_radius=counter_h // 2)
        pygame.draw.rect(screen, GOLD, rect, width=max(1, scaled(2)), border_radius=counter_h // 2)

    heart_icon = icon_images.get("heart")
    coin_icon = icon_images.get("coin")

    def draw_counter(rect, value, kind, icon):
        icon_size = scaled(20)
        icon_x = rect.x + scaled(12)
        icon_center = (icon_x + icon_size // 2, rect.centery)
        if icon is not None:
            icon_surface = pygame.transform.smoothscale(icon, (icon_size, icon_size))
            screen.blit(icon_surface, icon_surface.get_rect(center=icon_center))
        elif kind == "heart":
            # Smooth heart silhouette fallback if no heart image is supplied.
            cx, cy = icon_center
            r = max(3, icon_size // 4)
            pygame.draw.circle(screen, RED, (cx - r // 2, cy - r // 3), r)
            pygame.draw.circle(screen, RED, (cx + r // 2, cy - r // 3), r)
            pygame.draw.polygon(screen, RED, [(cx - r - 1, cy), (cx + r + 1, cy), (cx, cy + r + 2)])
        else:
            pygame.draw.circle(screen, GOLD, icon_center, icon_size // 2)
            pygame.draw.circle(screen, (255, 238, 157), icon_center, icon_size // 2, max(1, scaled(2)))
        draw_text(str(value), get_font(16, True), WHITE,
                  (rect.right - scaled(19), rect.centery))

    draw_counter(heart_rect, progress.get("hearts", 5), "heart", heart_icon)
    draw_counter(coin_rect, progress.get("coins", 0), "coin", coin_icon)

    # The road is already painted into level_map.png; don't draw a second
    # artificial line over the artwork. Place markers directly on the road.
    points = get_level_positions()

    for level, center in enumerate(points, start=1):
        unlocked = is_level_unlocked(level)
        stars = get_stars(level)
        radius = scaled(25)

        pygame.draw.circle(screen, (22, 13, 34), (center[0], center[1] + scaled(4)), radius + scaled(5))
        pygame.draw.circle(screen, (255, 232, 153), center, radius + scaled(3))
        pygame.draw.circle(screen, PURPLE if unlocked else (55, 48, 69), center, radius)
        pygame.draw.circle(
            screen, LIGHT_PURPLE if unlocked else (115, 106, 128), center,
            max(1, radius - scaled(4)), max(1, scaled(2))
        )
        pygame.draw.circle(screen, (255, 255, 255, 40), (center[0], center[1] - scaled(7)), max(2, scaled(3)))

        if unlocked:
            draw_text(str(level), get_font(22, True), WHITE, center)
        elif "lock" in icon_images:
            lock_size = scaled(22)
            lock_icon = pygame.transform.smoothscale(icon_images["lock"], (lock_size, lock_size))
            screen.blit(lock_icon, lock_icon.get_rect(center=center))
        else:
            draw_text("LOCK", get_font(11, True), WHITE, center)

        if stars:
            draw_stars((center[0], center[1] + radius + scaled(10)), stars, scaled(5))

        best = progress["best_moves"].get(str(level))
        if best is not None and unlocked:
            draw_text(f"{best} moves", get_font(11), WHITE, (center[0], center[1] + radius + scaled(25)))

def update_grid():
    global GRID_COLS, GRID_ROWS, CARD_SIZE
    global GAP, MARGIN, HEADER_HEIGHT, GRID_TOP
    global GRID_BOTTOM, GRID_WIDTH, GRID_LEFT
    global scaled_card_back

    total_cards = TOTAL_PAIRS * 2

    MARGIN = max(4, scaled(10))
    GAP = max(3, scaled(7))
    HEADER_HEIGHT = max(scaled(126), int(HEIGHT * 0.155))
    GRID_TOP = HEADER_HEIGHT + scaled(8)
    GRID_BOTTOM = HEIGHT - max(scaled(14), int(HEIGHT * 0.035))

    available_width = max(1, WIDTH - MARGIN * 2)
    available_height = max(1, GRID_BOTTOM - GRID_TOP)

    # Choose the column count that gives the largest square cards while
    # keeping every row inside the available screen area.
    if HEIGHT > WIDTH:
        candidate_columns = range(3, 8)
    else:
        candidate_columns = range(5, 10)

    best_layout = None

    for columns in candidate_columns:
        rows = (total_cards + columns - 1) // columns
        card_width = (
            available_width - GAP * (columns - 1)
        ) // columns
        card_height = (
            available_height - GAP * (rows - 1)
        ) // max(1, rows)
        card_size = min(card_width, card_height)

        if card_size > 0:
            # Prefer the largest cards; on ties prefer fewer rows.
            score = (card_size, -rows, columns)
            if best_layout is None or score > best_layout[0]:
                best_layout = (score, columns, rows, card_size)

    if best_layout is None:
        GRID_COLS = 1
        GRID_ROWS = total_cards
        CARD_SIZE = 1
    else:
        _, GRID_COLS, GRID_ROWS, CARD_SIZE = best_layout

    GRID_WIDTH = GRID_COLS * CARD_SIZE + (GRID_COLS - 1) * GAP
    GRID_LEFT = max(MARGIN, (WIDTH - GRID_WIDTH) // 2)

    scaled_tile_images.clear()

    for tile_id, image in tile_images.items():
        scaled_tile_images[tile_id] = pygame.transform.smoothscale(
            image, (CARD_SIZE, CARD_SIZE)
        )

    if card_back:
        scaled_card_back = pygame.transform.smoothscale(
            card_back, (CARD_SIZE, CARD_SIZE)
        )
    else:
        scaled_card_back = None

def restart_game():
    global TOTAL_PAIRS, cards, revealed, matched
    global moves, matched_pairs, first_card, second_card
    global match_time, game_won, game_lost, earned_stars
    global game_start_ticks, lose_reason

    TOTAL_PAIRS = LEVEL_PAIRS[current_level]
    update_grid()

    available_tiles = list(tile_images.keys())

    if len(available_tiles) < TOTAL_PAIRS:
        available_tiles = list(range(max(TOTAL_PAIRS, len(available_tiles))))

    selected_tiles = random.sample(
        available_tiles,
        min(TOTAL_PAIRS, len(available_tiles)),
    )

    while len(selected_tiles) < TOTAL_PAIRS:
        selected_tiles.append(len(selected_tiles) + 1000)

    cards = selected_tiles * 2
    random.shuffle(cards)

    revealed = set()
    matched = set()
    moves = 0
    matched_pairs = 0
    first_card = None
    second_card = None
    match_time = 0
    game_won = False
    game_lost = False
    earned_stars = 0
    game_start_ticks = pygame.time.get_ticks()
    lose_reason = "moves"


def get_card_rect(index):
    row = index // GRID_COLS
    col = index % GRID_COLS

    x = GRID_LEFT + col * (CARD_SIZE + GAP)
    y = GRID_TOP + row * (CARD_SIZE + GAP)

    return pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)


def draw_card(index):
    rect = get_card_rect(index)

    pygame.draw.rect(
        screen,
        DARK_PURPLE,
        rect.move(0, max(1, scaled(2))),
        border_radius=max(2, scaled(8)),
    )

    if index in matched or index in revealed:
        tile_id = cards[index]
        image = scaled_tile_images.get(tile_id)

        pygame.draw.rect(
            screen,
            WHITE,
            rect,
            border_radius=max(2, scaled(8)),
        )

        if image:
            image_rect = image.get_rect(center=rect.center)
            screen.blit(image, image_rect)
        else:
            draw_text(
                str(tile_id + 1),
                get_font(18),
                PURPLE,
                rect.center,
            )

        border_color = GREEN if index in matched else GOLD

        pygame.draw.rect(
            screen,
            border_color,
            rect,
            width=max(1, scaled(2)),
            border_radius=max(2, scaled(8)),
        )

    else:
        if scaled_card_back:
            screen.blit(scaled_card_back, rect)
        else:
            pygame.draw.rect(
                screen,
                PURPLE,
                rect,
                border_radius=max(2, scaled(8)),
            )

            pygame.draw.rect(
                screen,
                GOLD,
                rect,
                width=max(1, scaled(2)),
                border_radius=max(2, scaled(8)),
            )

            draw_text(
                "✦",
                get_font(22),
                GOLD,
                rect.center,
            )


def get_time_left():
    if game_won or game_lost or not game_start_ticks:
        return LEVEL_TIME_LIMITS[current_level]

    elapsed = (pygame.time.get_ticks() - game_start_ticks) // 1000
    return max(0, LEVEL_TIME_LIMITS[current_level] - elapsed)



def calculate_stars(level, move_count, elapsed_seconds=None):
    # A completed level always earns one star.
    # Bonus star: finish within the first 60 seconds.
    # Bonus star: finish with at least 5 moves remaining.
    stars = 1

    if elapsed_seconds is None:
        elapsed_seconds = max(
            0,
            (pygame.time.get_ticks() - game_start_ticks) // 1000,
        )

    if elapsed_seconds <= 60:
        stars += 1

    moves_left = LEVEL_MAX_MOVES[level] - move_count
    if moves_left >= 5:
        stars += 1

    return min(3, stars)

def finish_level():
    global game_won, earned_stars

    game_won = True
    earned_stars = calculate_stars(current_level, moves)
    progress["coins"] = int(progress.get("coins", 0)) + 50

    key = str(current_level)
    old_stars = get_stars(current_level)

    progress["stars"][key] = max(old_stars, earned_stars)

    old_best = progress["best_moves"].get(key)

    if old_best is None or moves < int(old_best):
        progress["best_moves"][key] = moves

    save_progress()


def draw_win_popup():
    screen.blit(overlay, (0, 0))

    panel_width = min(WIDTH - scaled(24), scaled(380))
    panel_height = min(HEIGHT - scaled(24), scaled(330))

    panel = pygame.Rect(
        (WIDTH - panel_width) // 2,
        (HEIGHT - panel_height) // 2,
        panel_width,
        panel_height,
    )

    pygame.draw.rect(
        screen,
        DARK_PURPLE,
        panel,
        border_radius=scaled(20),
    )

    pygame.draw.rect(
        screen,
        GOLD,
        panel,
        width=max(1, scaled(3)),
        border_radius=scaled(20),
    )

    draw_text(
        "LEVEL COMPLETE!",
        get_font(28),
        GOLD,
        (panel.centerx, panel.y + scaled(38)),
    )

    draw_stars(
        (panel.centerx, panel.y + scaled(90)),
        earned_stars,
        scaled(22),
    )

    draw_text(
        f"Moves: {moves}/{LEVEL_MAX_MOVES[current_level]}",
        FONT_MEDIUM,
        WHITE,
        (panel.centerx, panel.y + scaled(135)),
    )

    if earned_stars == 3:
        message = (
            "Next level unlocked!"
            if current_level < TOTAL_LEVELS
            else "You completed every level!"
        )
        message_color = GREEN
    else:
        message = "Get 3 stars to unlock the next level"
        message_color = WHITE

    draw_text(
        message,
        get_font(14),
        message_color,
        (panel.centerx, panel.y + scaled(165)),
    )

    win_restart_rect.center = (
        panel.centerx,
        panel.y + panel.height - scaled(80),
    )

    win_continue_rect.center = (
        panel.centerx,
        panel.y + panel.height - scaled(28),
    )

    draw_button(
        win_restart_rect,
        "REPLAY",
        PURPLE,
    )

    draw_button(
        win_continue_rect,
        "CONTINUE",
        DARK_PURPLE,
    )


def draw_lose_popup():
    screen.blit(overlay, (0, 0))

    panel_width = min(WIDTH - scaled(24), scaled(380))
    panel_height = min(HEIGHT - scaled(24), scaled(290))

    panel = pygame.Rect(
        (WIDTH - panel_width) // 2,
        (HEIGHT - panel_height) // 2,
        panel_width,
        panel_height,
    )

    pygame.draw.rect(
        screen,
        DARK_PURPLE,
        panel,
        border_radius=scaled(20),
    )

    pygame.draw.rect(
        screen,
        RED,
        panel,
        width=max(1, scaled(3)),
        border_radius=scaled(20),
    )

    lose_title = "TIME'S UP!" if lose_reason == "time" else "OUT OF MOVES!"
    draw_text(
        lose_title,
        get_font(28),
        RED,
        (panel.centerx, panel.y + scaled(42)),
    )

    draw_text(
        f"Pairs: {matched_pairs}/{TOTAL_PAIRS}",
        FONT_MEDIUM,
        WHITE,
        (panel.centerx, panel.y + scaled(95)),
    )

    draw_text(
        "Try again to earn 3 stars",
        get_font(14),
        WHITE,
        (panel.centerx, panel.y + scaled(130)),
    )

    lose_retry_rect.center = (
        panel.centerx,
        panel.y + panel.height - scaled(75),
    )

    lose_map_rect.center = (
        panel.centerx,
        panel.y + panel.height - scaled(25),
    )

    draw_button(
        lose_retry_rect,
        "TRY AGAIN",
        PURPLE,
    )

    draw_button(
        lose_map_rect,
        "LEVEL MAP",
        DARK_PURPLE,
    )


def draw_menu():
    draw_background()
    screen.blit(overlay, (0, 0))


    draw_button(
        exit_menu_rect,
        "",
        DARK_PURPLE,
        font=FONT_SMALL,
        image_key="exit",
    )

    draw_button(
        settings_rect,
        "SETTINGS",
        DARK_PURPLE,
        font=FONT_SMALL,
        image_key="settings",
    )

    draw_button(
        play_rect,
        "START",
        PURPLE,
        font=FONT_LARGE,
        image_key="play",
    )

    draw_button(
        levels_menu_rect,
        "LEVELS",
        DARK_PURPLE,
        font=FONT_MEDIUM,
    )

    draw_text(
        f"Level {get_current_unlocked_level()} unlocked",
        FONT_SMALL,
        WHITE,
        (WIDTH // 2, levels_menu_rect.bottom + scaled(25)),
    )


def draw_settings():
    draw_background()
    screen.blit(overlay, (0, 0))

    if "home" in icon_images:
        draw_circle_button(
            screen,
            (back_settings_rect.centerx, back_settings_rect.centery),
            max(scaled(18), min(back_settings_rect.width, back_settings_rect.height) // 2),
            "home",
        )
    else:
        draw_button(
            back_settings_rect,
            "BACK",
            DARK_PURPLE,
            font=FONT_SMALL,
            image_key="back",
        )

    music_label = "Music: ON" if music_enabled else "Music: OFF"

    draw_text(
        music_label,
        FONT_MEDIUM,
        WHITE,
        (WIDTH // 2, int(HEIGHT * 0.35)),
    )

    pygame.draw.rect(
        screen,
        DARK_PURPLE,
        music_rect,
        border_radius=scaled(8),
    )

    pygame.draw.rect(
        screen,
        GOLD,
        pygame.Rect(
            music_rect.x,
            music_rect.y,
            int(music_rect.width * music_volume),
            music_rect.height,
        ),
        border_radius=scaled(8),
    )

    knob_x = music_rect.x + int(
        music_rect.width * music_volume
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (knob_x, music_rect.centery),
        scaled(12),
    )

    if "music" in icon_images:
        draw_circle_button(
            screen,
            music_toggle_rect.center,
            max(scaled(22), min(music_toggle_rect.height, music_toggle_rect.width) // 2),
            "music",
            enabled=music_enabled,
        )
        draw_text(
            music_label,
            FONT_MEDIUM,
            WHITE,
            (music_toggle_rect.centerx, music_toggle_rect.bottom + scaled(18)),
        )
    else:
        draw_button(
            music_toggle_rect,
            music_label,
            PURPLE if music_enabled else DARK_PURPLE,
        )

    draw_text(
        "Tap the bar to change volume",
        FONT_SMALL,
        WHITE,
        (WIDTH // 2, int(HEIGHT * 0.68)),
    )


def draw_game():
    draw_background()

    header = pygame.Rect(
        0,
        0,
        WIDTH,
        GRID_TOP - scaled(4),
    )

    pygame.draw.rect(screen, DARK_PURPLE, header)

    if "home" in icon_images:
        draw_circle_button(
            screen,
            (game_back_rect.centerx, game_back_rect.centery),
            max(scaled(16), min(game_back_rect.width, game_back_rect.height) // 2),
            "home",
        )
    else:
        draw_button(
            game_back_rect,
            "BACK",
            DARK_PURPLE,
            font=FONT_SMALL,
            image_key="back",
        )

    draw_button(
        restart_rect,
        "RESTART",
        DARK_PURPLE,
        font=FONT_SMALL,
        image_key="restart",
    )

    draw_text(
        f"LEVEL {current_level}",
        get_font(22),
        GOLD,
        (WIDTH // 2, scaled(17)),
    )

    draw_text(
        f"♥ {progress.get('hearts', 5)}",
        get_font(17),
        RED,
        (WIDTH * 0.30, scaled(43)),
    )

    time_left = get_time_left()
    timer_color = RED if time_left <= 15 else WHITE
    draw_text(
        f"TIME {time_left // 60:02d}:{time_left % 60:02d}",
        get_font(17),
        timer_color,
        (WIDTH * 0.50, scaled(43)),
    )

    draw_text(
        f"● {progress.get('coins', 0)}",
        get_font(17),
        GOLD,
        (WIDTH * 0.70, scaled(43)),
    )

    draw_text(
        f"Moves: {moves}/{LEVEL_MAX_MOVES[current_level]}",
        get_font(15),
        WHITE,
        (WIDTH * 0.27, scaled(68)),
    )

    draw_text(
        f"Pairs: {matched_pairs}/{TOTAL_PAIRS}",
        get_font(15),
        WHITE,
        (WIDTH * 0.73, scaled(68)),
    )

    for index in range(len(cards)):
        draw_card(index)

    if game_won:
        draw_win_popup()
    elif game_lost:
        draw_lose_popup()


def toggle_music():
    global music_enabled

    music_enabled = not music_enabled

    try:
        if music_enabled:
            pygame.mixer.music.set_volume(music_volume)

            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.pause()
    except pygame.error:
        pass


def update_volume(x):
    global music_volume

    music_volume = max(
        0.0,
        min(
            1.0,
            (x - music_rect.x) / max(1, music_rect.width),
        ),
    )

    try:
        if music_enabled:
            pygame.mixer.music.set_volume(music_volume)
    except pygame.error:
        pass


def handle_card_click(position):
    global first_card, second_card, moves
    global match_time, matched_pairs, game_lost

    if game_won or game_lost:
        return

    if first_card is not None and second_card is not None:
        return

    for index in range(len(cards)):
        if not get_card_rect(index).collidepoint(position):
            continue

        if index in matched or index in revealed:
            return

        revealed.add(index)

        if first_card is None:
            first_card = index
        else:
            second_card = index
            moves += 1

            if cards[first_card] == cards[second_card]:
                matched.add(first_card)
                matched.add(second_card)

                revealed.discard(first_card)
                revealed.discard(second_card)

                matched_pairs += 1

                first_card = None
                second_card = None

                if matched_pairs == TOTAL_PAIRS:
                    finish_level()

            else:
                match_time = pygame.time.get_ticks()

        return


def start_level(level):
    global current_level, current_page

    if not 1 <= level <= TOTAL_LEVELS:
        return

    if not is_level_unlocked(level):
        return

    current_level = level
    restart_game()
    current_page = "game"


def handle_click(position):
    global current_page

    if current_page == "menu":
        if play_rect.collidepoint(position):
            start_level(get_current_unlocked_level())

        elif levels_menu_rect.collidepoint(position):
            current_page = "map"

        elif settings_rect.collidepoint(position):
            current_page = "settings"

        elif exit_menu_rect.collidepoint(position):
            return "exit"

    elif current_page == "map":
        if map_back_rect.collidepoint(position):
            current_page = "menu"
            return None

        points = get_level_positions()

        for level, center in enumerate(points, start=1):
            level_radius = scaled(34)
            rect = pygame.Rect(
                center[0] - level_radius,
                center[1] - level_radius,
                level_radius * 2,
                level_radius * 2,
            )

            if rect.collidepoint(position):
                if is_level_unlocked(level):
                    start_level(level)

                return None

    elif current_page == "settings":
        if back_settings_rect.collidepoint(position):
            current_page = "menu"

        elif music_toggle_rect.collidepoint(position):
            toggle_music()

        elif music_rect.inflate(
            scaled(20),
            scaled(30),
        ).collidepoint(position):
            update_volume(position[0])

    elif current_page == "game":
        if game_won:
            if win_restart_rect.collidepoint(position):
                restart_game()

            elif win_continue_rect.collidepoint(position):
                if (
                    current_level < TOTAL_LEVELS
                    and is_level_unlocked(current_level + 1)
                ):
                    start_level(current_level + 1)
                else:
                    current_page = "map"

        elif game_lost:
            if lose_retry_rect.collidepoint(position):
                restart_game()

            elif lose_map_rect.collidepoint(position):
                current_page = "map"

        elif restart_rect.collidepoint(position):
            restart_game()

        elif game_back_rect.collidepoint(position):
            current_page = "map"

        else:
            handle_card_click(position)

    return None


restart_game()

last_click_position = None
last_click_time = 0

while running:
    now = pygame.time.get_ticks()

    if (
        current_page == "game"
        and not game_won
        and not game_lost
        and get_time_left() <= 0
    ):
        game_lost = True
        lose_reason = "time"
        progress["hearts"] = max(0, int(progress.get("hearts", 5)) - 1)
        save_progress()

    if (
        second_card is not None
        and now - match_time >= 800
    ):
        revealed.discard(first_card)
        revealed.discard(second_card)

        first_card = None
        second_card = None

        if (
            not game_won
            and not game_lost
            and moves >= LEVEL_MAX_MOVES[current_level]
            and matched_pairs < TOTAL_PAIRS
        ):
            game_lost = True
            lose_reason = "moves"
            progress["hearts"] = max(0, int(progress.get("hearts", 5)) - 1)
            save_progress()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_page in ("game", "settings", "map"):
                    current_page = (
                        "map" if current_page == "game" else "menu"
                    )
                else:
                    running = False

        elif event.type == pygame.MOUSEMOTION:
            if (
                current_page == "settings"
                and event.buttons[0]
                and music_rect.inflate(
                    scaled(20),
                    scaled(30),
                ).collidepoint(event.pos)
            ):
                update_volume(event.pos[0])

        elif event.type in (
            pygame.MOUSEBUTTONDOWN,
            pygame.FINGERDOWN,
        ):
            if event.type == pygame.FINGERDOWN:
                position = (
                    int(event.x * WIDTH),
                    int(event.y * HEIGHT),
                )
            else:
                if event.button != 1:
                    continue

                position = event.pos

            click_time = pygame.time.get_ticks()

            if (
                last_click_position is not None
                and position == last_click_position
                and click_time - last_click_time < 120
            ):
                continue

            last_click_position = position
            last_click_time = click_time

            result = handle_click(position)

            if result == "exit":
                running = False

    if current_page == "menu":
        draw_menu()
    elif current_page == "map":
        draw_map()
    elif current_page == "settings":
        draw_settings()
    elif current_page == "game":
        draw_game()

    pygame.display.flip()
    clock.tick(FPS)

try:
    pygame.mixer.music.stop()
except pygame.error:
    pass

pygame.quit()
