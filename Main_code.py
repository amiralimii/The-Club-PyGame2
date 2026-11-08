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
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 7,
    7: 8,
    8: 9,
    9: 10,
    10: 11,
}

LEVEL_MAX_MOVES = {
    1: 10,
    2: 13,
    3: 16,
    4: 19,
    5: 22,
    6: 25,
    7: 28,
    8: 31,
    9: 34,
    10: 37,
}

LEVEL_TIME_LIMITS = {level: 0 for level in range(1, 11)}

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
show_back_confirm = False
back_confirm_opened_at = 0

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
        "best_times": {},
        "best_stage_times": {},
        "coins": 0,
        "hearts": 5,
    }

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)

        if isinstance(saved, dict):
            stars = saved.get("stars", {})
            best_moves = saved.get("best_moves", {})
            best_times = saved.get("best_times", {})
            best_stage_times = saved.get("best_stage_times", {})
            if isinstance(best_stage_times, dict):
                data["best_stage_times"] = {str(k): max(0, int(v)) for k, v in best_stage_times.items() if str(k).replace("_", "").isdigit()}

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

            if isinstance(best_times, dict):
                for key, value in best_times.items():
                    try:
                        if 1 <= int(key) <= TOTAL_LEVELS:
                            time_value = max(0, int(value))
                            data["best_times"][str(int(key))] = time_value
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

    return get_stars(level - 1) >= 1


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


level_map_heart_icon = load_image(os.path.join(ASSETS_DIR, "ui", "heart_icon.png"))
level_map_coin_icon = load_image(os.path.join(ASSETS_DIR, "ui", "coin_icon.png"))


logo_image = load_image(os.path.join(IMAGES_DIR, "tile_club_logo.png"))

card_back = load_image(
    os.path.join(TILES_DIR, "card_back.png")
)

settings_panel_image = load_image(
    os.path.join(IMAGES_DIR, "settings_panel.png")
)


music_on_image = load_image(os.path.join(BUTTONS_DIR, "button_music_on.png"))
music_off_image = load_image(os.path.join(BUTTONS_DIR, "button_music_off.png"))
volume_down_image = load_image(os.path.join(BUTTONS_DIR, "button_volume_down.png"))
volume_up_image = load_image(os.path.join(BUTTONS_DIR, "button_volume_up.png"))
volume_slider_track_image = load_image(os.path.join(ASSETS_DIR, "ui", "volume_slider_track.png"))
volume_slider_fill_image = load_image(os.path.join(ASSETS_DIR, "ui", "volume_slider_fill.png"))
volume_slider_knob_image = load_image(os.path.join(ASSETS_DIR, "ui", "volume_slider_knob.png"))
volume_percentage_frame = load_image(
    os.path.join(ASSETS_DIR, "ui_icons", "volume_percentage_frame.png")
)


stats_title_image = load_image(os.path.join(ASSETS_DIR, "ui_icons", "stats_title.png"))
STATS_ICON_FILES = {
    "level": "level_icon.png",
    "completed": "levels_completed_icon.png",
    "stars": "stars_icon.png",
    "best_moves": "best_moves_icon.png",
    "coins": "coins_icon.png",
}
stats_icon_images = {
    key: load_image(os.path.join(ASSETS_DIR, "stats", filename))
    for key, filename in STATS_ICON_FILES.items()
}

button_images = {
    "play": load_image(
        os.path.join(BUTTONS_DIR, "button_play.png")
    ),
    "settings": load_image(
        os.path.join(BUTTONS_DIR, "button_settings.png")
    ),
    "stats": load_image(
        os.path.join(BUTTONS_DIR, "button_stats.png")
    ),
    "shop": load_image(
        os.path.join(BUTTONS_DIR, "button_shop.png")
    ),
    "levels": load_image(
        os.path.join(BUTTONS_DIR, "button_levels.png")
    ),
    "restart": load_image(
        os.path.join(BUTTONS_DIR, "button_restart.png")
    ),
    "back": (
        load_image(os.path.join(BUTTONS_DIR, "button_back.png"))
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
music_volume = 0.70
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

menu_row_gap = scaled(12)
menu_side_margin = scaled(22)


menu_button_width = max(
    scaled(90),
    min(scaled(205), (WIDTH - 2 * menu_side_margin - 3 * menu_row_gap) // 4),
)
menu_button_height = max(
    scaled(48),
    min(scaled(76), int(HEIGHT * 0.12)),
)


play_rect.y = int(HEIGHT * 0.49)
play_rect.centerx = WIDTH // 2


logo_rect = pygame.Rect(0, 0, 1, 1)
if logo_image:
    logo_ratio = logo_image.get_width() / max(1, logo_image.get_height())
    logo_width = min(int(WIDTH * 0.76), scaled(430))
    logo_height = max(1, int(logo_width / logo_ratio))
    max_logo_height = int(HEIGHT * 0.25)
    if logo_height > max_logo_height:
        logo_height = max_logo_height
        logo_width = max(1, int(logo_height * logo_ratio))
    logo_rect = pygame.Rect(0, 0, logo_width, logo_height)
    logo_rect.centerx = WIDTH // 2
    logo_rect.centery = int(HEIGHT * 0.22)

menu_row_width = menu_button_width * 4 + menu_row_gap * 3
menu_row_x = (WIDTH - menu_row_width) // 2
menu_row_y = min(
    HEIGHT - menu_button_height - scaled(24),
    int(HEIGHT * 0.80),
)

levels_menu_rect = pygame.Rect(
    menu_row_x,
    menu_row_y,
    menu_button_width,
    menu_button_height,
)
settings_rect = pygame.Rect(
    levels_menu_rect.right + menu_row_gap,
    menu_row_y,
    menu_button_width,
    menu_button_height,
)
menu_stats_rect = pygame.Rect(
    settings_rect.right + menu_row_gap,
    menu_row_y,
    menu_button_width,
    menu_button_height,
)
menu_shop_rect = pygame.Rect(
    menu_stats_rect.right + menu_row_gap,
    menu_row_y,
    menu_button_width,
    menu_button_height,
)

stats_back_rect = pygame.Rect(
    scaled(8),
    scaled(8),
    scaled(150),
    scaled(60),
)
shop_back_rect = stats_back_rect.copy()

exit_menu_rect = pygame.Rect(
    scaled(14),
    scaled(14),
    scaled(82),
    scaled(36),
)

back_settings_rect = pygame.Rect(
    scaled(12),
    scaled(12),
    scaled(105),
    scaled(42),
)



settings_panel_rect = pygame.Rect(0, 0, 1, 1)
settings_panel_scaled = None
music_rect = pygame.Rect(0, 0, 1, 1)
music_toggle_rect = pygame.Rect(0, 0, 1, 1)
volume_down_rect = pygame.Rect(0, 0, 1, 1)
volume_up_rect = pygame.Rect(0, 0, 1, 1)

def prepare_settings_panel():
    global settings_panel_rect, settings_panel_scaled
    global music_rect, music_toggle_rect

    if settings_panel_image is None:
        return

    image_ratio = settings_panel_image.get_width() / max(
        1, settings_panel_image.get_height()
    )
    max_width = int(WIDTH * 0.92)
    max_height = int(HEIGHT * 0.76)
    panel_width = min(max_width, int(max_height * image_ratio))
    panel_height = max(1, int(panel_width / image_ratio))

    settings_panel_scaled = pygame.transform.smoothscale(
        settings_panel_image, (panel_width, panel_height)
    )
    settings_panel_rect = settings_panel_scaled.get_rect(
        center=(WIDTH // 2, int(HEIGHT * 0.53))
    )


    music_toggle_rect = pygame.Rect(
        settings_panel_rect.x + int(panel_width * 0.635),
        settings_panel_rect.y + int(panel_height * 0.365),
        int(panel_width * 0.245),
        int(panel_height * 0.135),
    )
    music_rect = pygame.Rect(
        settings_panel_rect.x + int(panel_width * 0.245),
        settings_panel_rect.y + int(panel_height * 0.685),
        int(panel_width * 0.525),
        max(scaled(12), int(panel_height * 0.065)),
    )

prepare_settings_panel()

map_back_rect = pygame.Rect(
    scaled(10),
    scaled(8),
    scaled(78),
    scaled(32),
)


map_heart_plus_rect = pygame.Rect(0, 0, 1, 1)
map_coin_plus_rect = pygame.Rect(0, 0, 1, 1)

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

continue_game_rect = pygame.Rect(
    WIDTH // 2 - scaled(105),
    HEIGHT // 2 + scaled(18),
    scaled(210),
    scaled(44),
)

confirm_back_rect = pygame.Rect(
    WIDTH // 2 - scaled(105),
    HEIGHT // 2 + scaled(70),
    scaled(210),
    scaled(44),
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
completed_time = 0
lose_reason = "moves"

GRID_COLS = 7
GRID_ROWS = 6
TOTAL_PAIRS = LEVEL_PAIRS[current_level]
STAGE_GROUP_SIZES = (2, 3, 4, 5)
STAGE_NAMES = ("NORMAL", "HARD", "HARDER", "MASTER")
stage_index = 0
selected_cards = []
stage_complete = False
stage_completed_time = 0
stage_start_ticks = 0
run_start_ticks = 0
run_completed_time = 0



frozen_tile_requirements = {}
unlocked_frozen_tiles = set()
frozen_unlock_animations = {}
FROZEN_UNLOCK_ANIMATION_MS = 700
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


    road_points = [
        (0.78, 0.935),
        (0.62, 0.895),
        (0.34, 0.855),
        (0.35, 0.735),
        (0.66, 0.675),
        (0.73, 0.575),
        (0.43, 0.485),
        (0.29, 0.365),
        (0.62, 0.285),
        (0.45, 0.105),
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



    draw_button(
        map_back_rect,
        "",
        DARK_PURPLE,
        font=FONT_SMALL,
        image_key="back",
    )

    draw_text("LEVEL MAP", get_font(30, True), GOLD, (WIDTH // 2, scaled(40)))



    global map_heart_plus_rect, map_coin_plus_rect

    hud_y = scaled(78)
    hud_h = max(scaled(34), min(scaled(54), int(HEIGHT * 0.075)))
    icon_size = int(hud_h * 1.12)
    plus_size = max(scaled(23), int(hud_h * 0.70))
    group_w = max(scaled(126), min(scaled(178), int(WIDTH * 0.34)))
    group_gap = scaled(9)
    right_margin = scaled(14)

    total_hud_w = group_w * 2 + group_gap
    hud_x = WIDTH - right_margin - total_hud_w



    if hud_x < scaled(4):
        group_w = max(scaled(92), (WIDTH - scaled(24) - group_gap) // 2)
        total_hud_w = group_w * 2 + group_gap
        hud_x = max(scaled(4), WIDTH - scaled(8) - total_hud_w)

    def draw_map_counter(x, value, icon, kind):
        group_rect = pygame.Rect(x, hud_y, group_w, hud_h)
        capsule_rect = pygame.Rect(
            x + int(icon_size * 0.55),
            hud_y + scaled(2),
            group_w - int(icon_size * 0.55),
            hud_h - scaled(4),
        )
        pygame.draw.rect(
            screen, (28, 12, 48), capsule_rect.move(0, scaled(2)),
            border_radius=capsule_rect.height // 2,
        )
        pygame.draw.rect(
            screen, (42, 20, 68), capsule_rect,
            border_radius=capsule_rect.height // 2,
        )
        pygame.draw.rect(
            screen, GOLD, capsule_rect,
            width=max(1, scaled(2)),
            border_radius=capsule_rect.height // 2,
        )

        icon_center = (x + icon_size // 2, hud_y + hud_h // 2)
        if icon is not None:
            fitted_icon = pygame.transform.smoothscale(
                icon, (icon_size, icon_size)
            )
            screen.blit(fitted_icon, fitted_icon.get_rect(center=icon_center))
        elif kind == "heart":
            cx, cy = icon_center
            radius = max(3, icon_size // 4)
            pygame.draw.circle(screen, RED, (cx - radius // 2, cy - radius // 3), radius)
            pygame.draw.circle(screen, RED, (cx + radius // 2, cy - radius // 3), radius)
            pygame.draw.polygon(
                screen, RED,
                [(cx - radius - 1, cy), (cx + radius + 1, cy), (cx, cy + radius + 2)],
            )
        else:
            pygame.draw.circle(screen, GOLD, icon_center, icon_size // 2)
            pygame.draw.circle(
                screen, (255, 245, 180), icon_center,
                max(1, icon_size // 2 - scaled(2)), max(1, scaled(2)),
            )

        plus_rect = pygame.Rect(0, 0, plus_size, plus_size)
        plus_rect.center = (
            capsule_rect.right - plus_size // 2,
            capsule_rect.centery,
        )
        pygame.draw.circle(
            screen, (15, 65, 26),
            (plus_rect.centerx, plus_rect.centery + scaled(2)),
            plus_size // 2,
        )
        pygame.draw.circle(screen, (255, 205, 45), plus_rect.center, plus_size // 2)
        pygame.draw.circle(
            screen, (28, 185, 62), plus_rect.center,
            max(1, plus_size // 2 - scaled(3)),
        )
        pygame.draw.circle(
            screen, (170, 255, 170), plus_rect.center,
            max(1, plus_size // 2 - scaled(5)), max(1, scaled(1)),
        )
        plus_font = get_font(max(14, int(plus_size / max(0.45, UI_SCALE) * 0.72)), True)
        draw_text("+", plus_font, WHITE, plus_rect.center)

        number_x = (capsule_rect.left + scaled(4) + plus_rect.left) // 2
        number_font = get_font(max(14, int(hud_h / max(0.45, UI_SCALE) * 0.43)), True)
        draw_text(str(value), number_font, WHITE, (number_x, capsule_rect.centery))

        return plus_rect

    map_heart_plus_rect = draw_map_counter(
        hud_x, progress.get("hearts", 5), level_map_heart_icon, "heart"
    )
    map_coin_plus_rect = draw_map_counter(
        hud_x + group_w + group_gap,
        progress.get("coins", 0),
        level_map_coin_icon,
        "coin",
    )



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

    total_cards = TOTAL_PAIRS * STAGE_GROUP_SIZES[stage_index]

    MARGIN = max(4, scaled(10))
    GAP = max(3, scaled(7))
    HEADER_HEIGHT = max(scaled(126), int(HEIGHT * 0.155))
    GRID_TOP = HEADER_HEIGHT + scaled(8)
    GRID_BOTTOM = HEIGHT - max(scaled(14), int(HEIGHT * 0.035))

    available_width = max(1, WIDTH - MARGIN * 2)
    available_height = max(1, GRID_BOTTOM - GRID_TOP)



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

def restart_game(new_run=True):
    global TOTAL_PAIRS, cards, revealed, matched
    global moves, matched_pairs, first_card, second_card, selected_cards
    global match_time, game_won, game_lost, earned_stars
    global game_start_ticks, completed_time, lose_reason
    global stage_index, stage_complete, stage_completed_time
    global stage_start_ticks, run_start_ticks, run_completed_time
    global frozen_tile_requirements, unlocked_frozen_tiles, frozen_unlock_animations

    if new_run:
        stage_index = 0
        run_start_ticks = pygame.time.get_ticks()
        run_completed_time = 0

    TOTAL_PAIRS = LEVEL_PAIRS[current_level]
    update_grid()
    available_tiles = list(tile_images.keys())
    if len(available_tiles) < TOTAL_PAIRS:
        available_tiles = list(range(max(TOTAL_PAIRS, len(available_tiles))))
    selected_tiles = random.sample(available_tiles, min(TOTAL_PAIRS, len(available_tiles)))
    while len(selected_tiles) < TOTAL_PAIRS:
        selected_tiles.append(len(selected_tiles) + 1000)

    group_size = STAGE_GROUP_SIZES[stage_index]
    cards = [tile for tile in selected_tiles for _ in range(group_size)]
    random.shuffle(cards)



    frozen_count = 0
    if current_level >= 3:
        frozen_count = 1
    if current_level >= 6:
        frozen_count = 2
    if current_level >= 9:
        frozen_count = 3
    frozen_count = min(frozen_count, max(0, TOTAL_PAIRS - 1))
    frozen_tiles = random.sample(selected_tiles, frozen_count) if frozen_count else []

    frozen_tile_requirements = {
        tile_id: requirement
        for requirement, tile_id in enumerate(frozen_tiles, start=1)
    }
    unlocked_frozen_tiles = set()
    frozen_unlock_animations = {}

    revealed = set()
    matched = set()
    moves = 0
    matched_pairs = 0
    first_card = None
    second_card = None
    selected_cards = []
    match_time = 0
    game_won = False
    game_lost = False
    stage_complete = False
    stage_completed_time = 0
    earned_stars = 0
    game_start_ticks = run_start_ticks
    stage_start_ticks = pygame.time.get_ticks()
    completed_time = 0
    lose_reason = "moves"


def get_card_rect(index):
    row = index // GRID_COLS
    col = index % GRID_COLS

    x = GRID_LEFT + col * (CARD_SIZE + GAP)
    y = GRID_TOP + row * (CARD_SIZE + GAP)

    return pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)


def draw_frozen_overlay(rect, tile_id):
    """Draw a lightweight translucent ice layer over a frozen card."""
    now = pygame.time.get_ticks()
    animation_start = frozen_unlock_animations.get(tile_id)
    if animation_start is not None:
        elapsed = now - animation_start
        if elapsed >= FROZEN_UNLOCK_ANIMATION_MS:
            return
        alpha = int(190 * (1 - elapsed / FROZEN_UNLOCK_ANIMATION_MS))
    else:
        alpha = 190

    ice = pygame.Surface(rect.size, pygame.SRCALPHA)
    radius = max(2, scaled(8))
    pygame.draw.rect(ice, (145, 220, 250, alpha), ice.get_rect(), border_radius=radius)
    pygame.draw.rect(
        ice,
        (235, 250, 255, min(255, alpha + 35)),
        ice.get_rect().inflate(-max(2, scaled(5)), -max(2, scaled(5))),
        width=max(1, scaled(2)),
        border_radius=max(2, radius - scaled(2)),
    )

    w, h = rect.size
    facet = max(3, min(w, h) // 5)
    pygame.draw.line(ice, (255, 255, 255, min(255, alpha + 45)),
                     (facet, facet), (w - facet, h - facet), max(1, scaled(1)))
    pygame.draw.line(ice, (225, 248, 255, alpha),
                     (w - facet, facet), (facet, h - facet), max(1, scaled(1)))
    pygame.draw.circle(ice, (255, 255, 255, min(255, alpha + 50)),
                       (w // 2, h // 2), max(2, min(w, h) // 12), max(1, scaled(1)))
    screen.blit(ice, rect.topleft)


def get_frozen_tile_id(index):
    if 0 <= index < len(cards):
        tile_id = cards[index]
        if tile_id in frozen_tile_requirements and tile_id not in unlocked_frozen_tiles:
            return tile_id
    return None


def update_frozen_unlocks():
    """Unlock frozen groups when their matching objective is achieved."""
    now = pygame.time.get_ticks()
    for tile_id, required_groups in frozen_tile_requirements.items():
        if tile_id not in unlocked_frozen_tiles and matched_pairs >= required_groups:
            unlocked_frozen_tiles.add(tile_id)
            frozen_unlock_animations[tile_id] = now


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

    frozen_tile_id = get_frozen_tile_id(index)
    if frozen_tile_id is not None:
        draw_frozen_overlay(rect, frozen_tile_id)
    elif cards[index] in frozen_unlock_animations:
        draw_frozen_overlay(rect, cards[index])


def get_elapsed_time():
    if not run_start_ticks:
        return 0
    if game_won or game_lost:
        return max(0, int(run_completed_time or completed_time))
    return max(0, (pygame.time.get_ticks() - run_start_ticks) // 1000)


def calculate_stars(level, move_count, elapsed_seconds=None):
    max_moves = LEVEL_MAX_MOVES[level]
    moves_left = max(0, max_moves - move_count)
    if moves_left >= max(5, max_moves // 2):
        return 3
    if moves_left >= 2:
        return 2
    return 1


def finish_level():
    global stage_complete, game_won, earned_stars
    global stage_completed_time, run_completed_time, completed_time

    now = pygame.time.get_ticks()
    stage_completed_time = max(0, (now - stage_start_ticks) // 1000)
    elapsed = max(0, (now - run_start_ticks) // 1000)
    stage_complete = True
    earned_stars = calculate_stars(current_level, moves, elapsed)

    stage_key = f"{current_level}_{stage_index + 1}"
    progress.setdefault("best_stage_times", {})
    old_stage_best = progress["best_stage_times"].get(stage_key)
    if old_stage_best is None or stage_completed_time < int(old_stage_best):
        progress["best_stage_times"][stage_key] = stage_completed_time

    if stage_index == len(STAGE_GROUP_SIZES) - 1:
        game_won = True
        run_completed_time = elapsed
        completed_time = elapsed
        progress["coins"] = int(progress.get("coins", 0)) + 50
        key = str(current_level)
        old_best_time = progress.get("best_times", {}).get(key)
        if old_best_time is None or elapsed < int(old_best_time):
            progress.setdefault("best_times", {})[key] = elapsed
        progress["stars"][key] = max(get_stars(current_level), earned_stars)
        old_best = progress["best_moves"].get(key)
        if old_best is None or moves < int(old_best):
            progress["best_moves"][key] = moves
    save_progress()


def draw_win_popup():
    screen.blit(overlay, (0, 0))
    panel_width = min(WIDTH - scaled(24), scaled(380))
    panel_height = min(HEIGHT - scaled(24), scaled(350))
    panel = pygame.Rect((WIDTH - panel_width) // 2, (HEIGHT - panel_height) // 2, panel_width, panel_height)
    pygame.draw.rect(screen, DARK_PURPLE, panel, border_radius=scaled(20))
    pygame.draw.rect(screen, GOLD, panel, width=max(1, scaled(3)), border_radius=scaled(20))

    final_stage = stage_index == len(STAGE_GROUP_SIZES) - 1
    heading = "LEVEL COMPLETE!" if final_stage else f"{STAGE_NAMES[stage_index]} COMPLETE!"
    draw_text(heading, get_font(26), GOLD, (panel.centerx, panel.y + scaled(38)))
    if final_stage:
        draw_stars((panel.centerx, panel.y + scaled(88)), earned_stars, scaled(22))
    draw_text(f"Stage time: {stage_completed_time // 60:02d}:{stage_completed_time % 60:02d}", FONT_MEDIUM, WHITE, (panel.centerx, panel.y + scaled(130)))
    draw_text(f"Total time: {get_elapsed_time() // 60:02d}:{get_elapsed_time() % 60:02d}", get_font(16), WHITE, (panel.centerx, panel.y + scaled(162)))
    draw_text(f"Moves: {moves}   |   Match {STAGE_GROUP_SIZES[stage_index]} cards", get_font(14), WHITE, (panel.centerx, panel.y + scaled(190)))

    win_restart_rect.center = (panel.centerx, panel.y + panel.height - scaled(82))
    win_continue_rect.center = (panel.centerx, panel.y + panel.height - scaled(29))
    draw_button(win_restart_rect, "REPLAY", PURPLE)
    draw_button(win_continue_rect, "LEVEL MAP" if final_stage else "CONTINUE", DARK_PURPLE)


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
        f"Groups: {matched_pairs}/{TOTAL_PAIRS}  |  Match {STAGE_GROUP_SIZES[stage_index]}",
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

    if logo_image:
        fitted_logo = pygame.transform.smoothscale(logo_image, logo_rect.size)
        screen.blit(fitted_logo, logo_rect)
    else:

        draw_text("TILE CLUB", get_font(42, True), GOLD,
                  (WIDTH // 2, int(HEIGHT * 0.22)))

    draw_button(
        play_rect,
        "PLAY",
        PURPLE,
        font=FONT_LARGE,
        image_key="play",
    )


    draw_button(
        levels_menu_rect, "", DARK_PURPLE,
        font=FONT_SMALL, image_key="levels",
    )
    draw_button(
        settings_rect, "", DARK_PURPLE,
        font=FONT_SMALL, image_key="settings",
    )
    draw_button(
        menu_stats_rect, "", DARK_PURPLE,
        font=FONT_SMALL, image_key="stats",
    )
    draw_button(
        menu_shop_rect, "", DARK_PURPLE,
        font=FONT_SMALL, image_key="shop",
    )

    draw_text(
        f"Level {get_current_unlocked_level()} unlocked",
        FONT_SMALL,
        WHITE,
        (WIDTH // 2, min(play_rect.bottom + scaled(16), menu_row_y - scaled(18))),
    )


def draw_stats():
    draw_background()
    screen.blit(overlay, (0, 0))


    draw_button(stats_back_rect, "", DARK_PURPLE, font=FONT_SMALL, image_key="back")

    title_w = min(int(WIDTH * 0.62), scaled(700))
    if stats_title_image is not None:
        ratio = stats_title_image.get_width() / max(1, stats_title_image.get_height())
        title_h = max(1, int(title_w / ratio))
        max_title_h = int(HEIGHT * 0.22)
        if title_h > max_title_h:
            title_h = max_title_h
            title_w = max(1, int(title_h * ratio))
        title_rect = pygame.Rect(0, 0, title_w, title_h)
        title_rect.center = (WIDTH // 2, int(HEIGHT * 0.16))
        title_art = pygame.transform.smoothscale(stats_title_image, title_rect.size)
        screen.blit(title_art, title_rect)
    else:
        title_rect = pygame.Rect(0, 0, 1, 1)
        title_rect.center = (WIDTH // 2, int(HEIGHT * 0.16))
        draw_text("YOUR STATS", FONT_TITLE, GOLD, title_rect.center)

    total_stars = sum(get_stars(level) for level in range(1, TOTAL_LEVELS + 1))
    completed_levels = sum(
        1 for level in range(1, TOTAL_LEVELS + 1) if get_stars(level) > 0
    )
    best_moves_count = len(progress.get("best_moves", {}))

    stat_rows = [
        ("level", "LEVEL UNLOCKED", str(get_current_unlocked_level())),
        ("completed", "LEVELS COMPLETED", f"{completed_levels} / {TOTAL_LEVELS}"),
        ("stars", "TOTAL STARS", f"{total_stars} / {TOTAL_LEVELS * 3}"),
        ("best_moves", "BEST-MOVE RECORDS", str(best_moves_count)),
        ("coins", "COINS", str(progress.get("coins", 0))),
    ]

    card_w = min(int(WIDTH * 0.76), scaled(560))
    card_h = max(scaled(54), min(scaled(68), int(HEIGHT * 0.092)))
    gap = max(scaled(7), int(card_h * 0.13))
    total_h = len(stat_rows) * card_h + (len(stat_rows) - 1) * gap


    preferred_top = max(int(HEIGHT * 0.29), title_rect.bottom + scaled(18))
    max_top = HEIGHT - total_h - scaled(24)
    rows_top = min(preferred_top, max(scaled(74), max_top))
    rows_top = max(scaled(70), rows_top)

    for index, (icon_key, label, value) in enumerate(stat_rows):
        rect = pygame.Rect(
            (WIDTH - card_w) // 2,
            rows_top + index * (card_h + gap),
            card_w,
            card_h,
        )


        pygame.draw.rect(
            screen, (23, 7, 43),
            rect.move(0, scaled(3)),
            border_radius=max(6, scaled(15)),
        )
        pygame.draw.rect(
            screen, (75, 12, 105),
            rect,
            border_radius=max(6, scaled(15)),
        )
        pygame.draw.rect(
            screen, (180, 28, 205),
            rect.inflate(-scaled(5), -scaled(5)),
            width=max(1, scaled(2)),
            border_radius=max(5, scaled(12)),
        )
        pygame.draw.rect(
            screen, GOLD,
            rect,
            width=max(1, scaled(2)),
            border_radius=max(6, scaled(15)),
        )

        icon = stats_icon_images.get(icon_key)
        icon_size = min(int(card_h * 0.82), scaled(58))
        icon_rect = pygame.Rect(
            rect.x + scaled(12),
            rect.centery - icon_size // 2,
            icon_size,
            icon_size,
        )
        if icon is not None:
            fitted_icon = pygame.transform.smoothscale(icon, icon_rect.size)
            screen.blit(fitted_icon, icon_rect)
        else:

            pygame.draw.circle(screen, GOLD, icon_rect.center, icon_size // 2)
            pygame.draw.circle(
                screen, PURPLE, icon_rect.center,
                max(2, icon_size // 2 - scaled(4)),
            )

        label_x = icon_rect.right + scaled(12)
        value_font = get_font(20, True)
        label_font = get_font(17, True)
        draw_text(
            label,
            label_font,
            (255, 235, 255),
            (label_x, rect.centery),
            center=False,
        )
        value_surface = value_font.render(value, True, GOLD)
        value_rect = value_surface.get_rect(
            midright=(rect.right - scaled(18), rect.centery)
        )
        screen.blit(value_surface, value_rect)



def draw_shop():
    draw_background()
    screen.blit(overlay, (0, 0))

    draw_button(shop_back_rect, "BACK", DARK_PURPLE, font=FONT_SMALL)
    draw_text("SHOP", FONT_TITLE, GOLD, (WIDTH // 2, int(HEIGHT * 0.20)))
    draw_text(
        f"YOUR COINS: {progress.get('coins', 0)}",
        FONT_MEDIUM,
        WHITE,
        (WIDTH // 2, int(HEIGHT * 0.31)),
    )



    card_w = min(int(WIDTH * 0.72), scaled(440))
    card_h = max(scaled(74), min(scaled(110), int(HEIGHT * 0.16)))
    item_rect = pygame.Rect(
        (WIDTH - card_w) // 2,
        int(HEIGHT * 0.42),
        card_w,
        card_h,
    )
    draw_button(item_rect, "MORE ITEMS COMING SOON", DARK_PURPLE, font=FONT_MEDIUM)
    draw_text(
        "Your coins are safe. Items can be added next.",
        FONT_SMALL,
        WHITE,
        (WIDTH // 2, item_rect.bottom + scaled(24)),
    )


def draw_settings():
    global volume_down_rect, volume_up_rect, music_rect
    draw_background()
    screen.blit(overlay, (0, 0))



    if settings_panel_scaled is not None:
        screen.blit(settings_panel_scaled, settings_panel_rect)

        panel_w = settings_panel_rect.width
        panel_h = settings_panel_rect.height
        px = settings_panel_rect.x
        py = settings_panel_rect.y



        toggle_rect = music_toggle_rect
        toggle_image = music_on_image if music_enabled else music_off_image
        if toggle_image is not None:
            image_ratio = toggle_image.get_width() / max(1, toggle_image.get_height())
            target_ratio = toggle_rect.width / max(1, toggle_rect.height)
            if image_ratio > target_ratio:
                draw_w = toggle_rect.width
                draw_h = max(1, int(draw_w / image_ratio))
            else:
                draw_h = toggle_rect.height
                draw_w = max(1, int(draw_h * image_ratio))
            fitted_toggle = pygame.transform.smoothscale(toggle_image, (draw_w, draw_h))
            fitted_rect = fitted_toggle.get_rect(center=toggle_rect.center)
            screen.blit(fitted_toggle, fitted_rect)
        else:

            radius = max(2, toggle_rect.height // 2)
            switch_color = (28, 190, 45) if music_enabled else (145, 35, 65)
            pygame.draw.rect(screen, (255, 190, 35), toggle_rect.inflate(4, 4),
                             border_radius=radius + 3)
            pygame.draw.rect(screen, switch_color, toggle_rect,
                             border_radius=radius)
            draw_text("ON" if music_enabled else "OFF", get_font(17), WHITE,
                      toggle_rect.center)


        percent = int(round(music_volume * 100))
        value_rect = pygame.Rect(
            px + int(panel_w * 0.675),
            py + int(panel_h * 0.545),
            int(panel_w * 0.20),
            int(panel_h * 0.105),
        )
        if volume_percentage_frame is not None:
            badge = pygame.transform.smoothscale(
                volume_percentage_frame, value_rect.size
            )
            screen.blit(badge, value_rect)
        else:

            pygame.draw.rect(
                screen, (65, 5, 90), value_rect,
                border_radius=value_rect.height // 2
            )
            pygame.draw.rect(
                screen, (220, 35, 220), value_rect,
                width=max(1, scaled(2)),
                border_radius=value_rect.height // 2
            )
        draw_text(f"{percent}%", get_font(19), (255, 205, 35), value_rect.center)

        slider_rect = pygame.Rect(
            px + int(panel_w * 0.285),
            py + int(panel_h * 0.685),
            int(panel_w * 0.445),
            max(scaled(12), int(panel_h * 0.065)),
        )

        music_rect = slider_rect.copy()


        button_size = max(scaled(28), min(scaled(48), int(panel_h * 0.105)))
        volume_down_rect = pygame.Rect(
            px + int(panel_w * 0.205),
            slider_rect.centery - button_size // 2,
            button_size,
            button_size,
        )
        volume_up_rect = pygame.Rect(
            px + int(panel_w * 0.755),
            slider_rect.centery - button_size // 2,
            button_size,
            button_size,
        )

        if volume_down_image is not None:
            down_image = pygame.transform.smoothscale(
                volume_down_image, volume_down_rect.size
            )
            screen.blit(down_image, volume_down_rect)
        else:
            pygame.draw.circle(screen, GOLD, volume_down_rect.center, button_size // 2)
            draw_text("−", get_font(25, True), DARK_PURPLE, volume_down_rect.center)

        if volume_up_image is not None:
            up_image = pygame.transform.smoothscale(
                volume_up_image, volume_up_rect.size
            )
            screen.blit(up_image, volume_up_rect)
        else:
            pygame.draw.circle(screen, GOLD, volume_up_rect.center, button_size // 2)
            draw_text("+", get_font(25, True), DARK_PURPLE, volume_up_rect.center)


        track_h = max(button_size, int(panel_h * 0.105))
        track_rect = pygame.Rect(
            slider_rect.x, slider_rect.centery - track_h // 2,
            slider_rect.width, track_h
        )
        if volume_slider_track_image is not None:
            track_img = pygame.transform.smoothscale(
                volume_slider_track_image, track_rect.size
            )
            screen.blit(track_img, track_rect)
        else:
            pygame.draw.rect(screen, GOLD, track_rect, border_radius=track_h // 2)
            pygame.draw.rect(screen, DARK_PURPLE, track_rect.inflate(-scaled(6), -scaled(6)),
                             border_radius=track_h // 2)

        inner_left = track_rect.left + int(track_rect.width * 0.075)
        inner_right = track_rect.right - int(track_rect.width * 0.075)
        inner_w = max(1, inner_right - inner_left)
        fill_w = int(inner_w * music_volume)
        fill_h = max(4, int(track_h * 0.34))
        fill_rect = pygame.Rect(inner_left, track_rect.centery - fill_h // 2,
                                max(1, fill_w), fill_h)
        if fill_w > 0:
            if volume_slider_fill_image is not None:
                fill_img = pygame.transform.smoothscale(
                    volume_slider_fill_image, fill_rect.size
                )
                screen.blit(fill_img, fill_rect)
            else:
                pygame.draw.rect(screen, (255, 190, 35), fill_rect,
                                 border_radius=fill_h // 2)

        knob_x = inner_left + fill_w
        knob_size = max(button_size, int(track_h * 1.08))
        knob_rect = pygame.Rect(0, 0, knob_size, knob_size)
        knob_rect.center = (knob_x, track_rect.centery)
        if volume_slider_knob_image is not None:
            knob_img = pygame.transform.smoothscale(
                volume_slider_knob_image, knob_rect.size
            )
            screen.blit(knob_img, knob_rect)
        else:
            pygame.draw.circle(screen, GOLD, knob_rect.center, knob_size // 2)
            pygame.draw.circle(screen, (190, 25, 220), knob_rect.center,
                               int(knob_size * 0.34))


    draw_button(
        back_settings_rect,
        "",
        DARK_PURPLE,
        font=FONT_SMALL,
        image_key="back",
    )


def load_confirm_popup_image():
    candidates = [
        os.path.join(BASE_DIR, "assets", "images", "confirm_leave_level.png"),
        os.path.join(BASE_DIR, "assets", "buttons", "confirm_leave_level.png"),
        os.path.join(BASE_DIR, "confirm_leave_level.png"),
    ]
    for candidate in candidates:
        try:
            return pygame.image.load(candidate).convert_alpha()
        except (pygame.error, FileNotFoundError):
            continue
    return None


confirm_popup_image = load_confirm_popup_image()


def draw_back_confirm_popup():
    screen.blit(overlay, (0, 0))

    panel_width = min(WIDTH - scaled(20), scaled(900))
    panel_height = min(HEIGHT - scaled(20), scaled(510))
    panel = pygame.Rect(
        (WIDTH - panel_width) // 2,
        (HEIGHT - panel_height) // 2,
        panel_width,
        panel_height,
    )

    if confirm_popup_image is not None:
        fitted = pygame.transform.smoothscale(confirm_popup_image, panel.size)
        screen.blit(fitted, panel.topleft)
    else:
        pygame.draw.rect(screen, DARK_PURPLE, panel, border_radius=scaled(22))
        pygame.draw.rect(
            screen, GOLD, panel, width=max(1, scaled(3)),
            border_radius=scaled(22),
        )
        draw_text(
            "LEAVE THIS LEVEL?",
            get_font(25, True),
            GOLD,
            (panel.centerx, panel.y + scaled(48)),
        )
        draw_text(
            "Your game progress in this round will be lost.",
            get_font(13),
            WHITE,
            (panel.centerx, panel.y + scaled(88)),
        )


    button_y = panel.y + int(panel_height * 0.72)
    button_w = int(panel_width * 0.36)
    button_h = int(panel_height * 0.22)
    continue_game_rect.update(
        panel.x + int(panel_width * 0.12),
        button_y - button_h // 2,
        button_w,
        button_h,
    )
    confirm_back_rect.update(
        panel.x + int(panel_width * 0.52),
        button_y - button_h // 2,
        button_w,
        button_h,
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
        f"LEVEL {current_level}  •  {STAGE_NAMES[stage_index]}",
        get_font(20),
        GOLD,
        (WIDTH // 2, scaled(17)),
    )

    draw_text(
        f"♥ {progress.get('hearts', 5)}",
        get_font(17),
        RED,
        (WIDTH * 0.30, scaled(43)),
    )

    elapsed = get_elapsed_time()
    draw_text(
        f"TIME {elapsed // 60:02d}:{elapsed % 60:02d}",
        get_font(17),
        WHITE,
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
        f"Groups: {matched_pairs}/{TOTAL_PAIRS}  |  Match {STAGE_GROUP_SIZES[stage_index]}",
        get_font(15),
        WHITE,
        (WIDTH * 0.73, scaled(68)),
    )

    frozen_remaining = sum(
        1 for tile_id in frozen_tile_requirements
        if tile_id not in unlocked_frozen_tiles
    )
    if frozen_tile_requirements:
        if frozen_remaining:
            next_goal = min(
                requirement for tile_id, requirement in frozen_tile_requirements.items()
                if tile_id not in unlocked_frozen_tiles
            )
            objective_text = f"ICE: {frozen_remaining} group(s) locked • Match {next_goal} group(s) to unlock"
        else:
            objective_text = "ICE CLEARED! All frozen groups unlocked"
        draw_text(objective_text, get_font(12, True), SKY,
                  (WIDTH // 2, GRID_TOP - scaled(2)))

    for index in range(len(cards)):
        draw_card(index)

    if stage_complete:
        draw_win_popup()
    elif game_lost:
        draw_lose_popup()

    if show_back_confirm:
        draw_back_confirm_popup()


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

    slider_left = music_rect.x + int(music_rect.width * 0.075)
    slider_width = max(1, int(music_rect.width * 0.85))
    music_volume = max(0.0, min(1.0, (x - slider_left) / slider_width))

    try:
        if music_enabled:
            pygame.mixer.music.set_volume(music_volume)
    except pygame.error:
        pass


def change_volume(amount):
    global music_volume

    music_volume = max(0.0, min(1.0, round(music_volume + amount, 2)))

    try:
        if music_enabled:
            pygame.mixer.music.set_volume(music_volume)
    except pygame.error:
        pass


def handle_card_click(position):
    global moves, match_time, matched_pairs, game_lost
    global selected_cards, first_card, second_card

    if game_won or game_lost or stage_complete or second_card is not None:
        return

    group_size = STAGE_GROUP_SIZES[stage_index]
    for index in range(len(cards)):
        if not get_card_rect(index).collidepoint(position):
            continue
        if index in matched or index in revealed:
            return
        if get_frozen_tile_id(index) is not None:
            return

        selected_cards.append(index)
        revealed.add(index)
        if len(selected_cards) == 1:
            first_card = selected_cards[0]
        if len(selected_cards) == group_size:
            moves += 1
            values = [cards[i] for i in selected_cards]
            if all(value == values[0] for value in values):
                matched.update(selected_cards)
                for card_index in selected_cards:
                    revealed.discard(card_index)
                matched_pairs += 1
                update_frozen_unlocks()
                selected_cards = []
                first_card = None
                second_card = None
                if matched_pairs >= TOTAL_PAIRS:
                    finish_level()
            else:
                first_card = selected_cards[0]
                second_card = selected_cards[-1]
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
    global current_page, show_back_confirm, back_confirm_opened_at
    global game_start_ticks, match_time, stage_index

    if current_page == "menu":
        if play_rect.collidepoint(position):
            start_level(get_current_unlocked_level())

        elif menu_stats_rect.collidepoint(position):
            current_page = "stats"

        elif menu_shop_rect.collidepoint(position):
            current_page = "shop"

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

        if map_heart_plus_rect.collidepoint(position) or map_coin_plus_rect.collidepoint(position):
            current_page = "shop"
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

    elif current_page == "stats":
        if stats_back_rect.collidepoint(position):
            current_page = "menu"

    elif current_page == "shop":
        if shop_back_rect.collidepoint(position):
            current_page = "menu"

    elif current_page == "settings":
        if back_settings_rect.collidepoint(position):
            current_page = "menu"

        elif music_toggle_rect.collidepoint(position):
            toggle_music()

        elif volume_down_rect.collidepoint(position):
            change_volume(-0.05)

        elif volume_up_rect.collidepoint(position):
            change_volume(0.05)

        elif music_rect.inflate(
            scaled(20),
            scaled(30),
        ).collidepoint(position):
            update_volume(position[0])

    elif current_page == "game":
        if show_back_confirm:
            if continue_game_rect.collidepoint(position):
                paused_for = pygame.time.get_ticks() - back_confirm_opened_at
                game_start_ticks += paused_for
                run_start_ticks += paused_for
                stage_start_ticks += paused_for
                if second_card is not None:
                    match_time += paused_for
                show_back_confirm = False

            elif confirm_back_rect.collidepoint(position):
                show_back_confirm = False
                current_page = "map"

            return None

        if stage_complete:
            if win_restart_rect.collidepoint(position):
                restart_game()
            elif win_continue_rect.collidepoint(position):
                if stage_index < len(STAGE_GROUP_SIZES) - 1:
                    global_stage_next = stage_index + 1
                    stage_index = global_stage_next
                    restart_game(new_run=False)
                else:
                    current_page = "map"

        elif game_lost:
            if lose_retry_rect.collidepoint(position):
                restart_game(new_run=False)

            elif lose_map_rect.collidepoint(position):
                current_page = "map"

        elif restart_rect.collidepoint(position):
            restart_game()

        elif game_back_rect.collidepoint(position):
            show_back_confirm = True
            back_confirm_opened_at = pygame.time.get_ticks()

        else:
            handle_card_click(position)

    return None


restart_game()

last_click_position = None
last_click_time = 0

while running:
    now = pygame.time.get_ticks()
    for animated_tile, animation_start in list(frozen_unlock_animations.items()):
        if now - animation_start >= FROZEN_UNLOCK_ANIMATION_MS:
            frozen_unlock_animations.pop(animated_tile, None)

    if (
        not show_back_confirm
        and second_card is not None
        and now - match_time >= 800
    ):
        for card_index in list(selected_cards):
            revealed.discard(card_index)
        selected_cards = []
        first_card = None
        second_card = None

        if (
            not game_won
            and not stage_complete
            and not game_lost
            and moves >= LEVEL_MAX_MOVES[current_level]
            and matched_pairs < TOTAL_PAIRS
        ):
            completed_time = max(0, (pygame.time.get_ticks() - run_start_ticks) // 1000)
            run_completed_time = completed_time
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
    elif current_page == "stats":
        draw_stats()
    elif current_page == "shop":
        draw_shop()
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
