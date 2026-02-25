"""
SUPER ZEBRA - Um jogo platformer estilo Super Mario
Personagem principal: uma zebra!
Controles: Setas ← → para mover, Espaço/↑ para pular
"""

import pygame
import sys
import math
import random
import struct
import array

# ─────────────────────────────────────────────
# Inicialização
# ─────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

SCREEN_W, SCREEN_H = 800, 600
TILE = 40
FPS = 60

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("🦓 SUPER ZEBRA 🦓")
clock = pygame.time.Clock()

# ─────────────────────────────────────────────
# Cores
# ─────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
SKY_BLUE    = (107, 140, 255)
GROUND_BR   = (139, 90, 43)
GROUND_TOP  = (34, 139, 34)
BRICK_COL   = (200, 80, 50)
BRICK_LINE  = (160, 60, 35)
QBLOCK_COL  = (255, 200, 50)
QBLOCK_DARK = (200, 150, 20)
COIN_COL    = (255, 215, 0)
COIN_DARK   = (200, 170, 0)
PIPE_GREEN  = (0, 160, 50)
PIPE_LIGHT  = (50, 200, 80)
PIPE_DARK   = (0, 120, 30)
CLOUD_WHITE = (245, 245, 255)
BUSH_GREEN  = (40, 180, 60)
BUSH_DARK   = (30, 140, 45)
CASTLE_GRAY = (180, 180, 180)
CASTLE_DARK = (130, 130, 130)
RED         = (220, 50, 50)
ORANGE      = (255, 140, 0)
ZEBRA_WHITE = (240, 240, 240)
ZEBRA_BLACK = (30, 30, 30)
ZEBRA_GRAY  = (80, 80, 80)
TURTLE_GREEN = (30, 160, 60)
TURTLE_DARK  = (20, 120, 40)
TURTLE_SHELL = (50, 180, 80)
TURTLE_BELLY = (230, 220, 180)
FLAG_GREEN   = (0, 200, 60)
FLAG_POLE    = (160, 160, 160)
HILL_GREEN   = (60, 170, 60)
HILL_DARK    = (40, 140, 40)

# ─────────────────────────────────────────────
# Geração de Sons (sintetizados)
# ─────────────────────────────────────────────
def generate_sound(frequency, duration_ms, volume=0.3, wave_type='square'):
    """Gera um som sintetizado."""
    sample_rate = 22050
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array.array('h', [0] * n_samples)
    max_amp = int(32767 * volume)
    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == 'square':
            val = max_amp if math.sin(2 * math.pi * frequency * t) >= 0 else -max_amp
        elif wave_type == 'sine':
            val = int(max_amp * math.sin(2 * math.pi * frequency * t))
        else:
            val = int(max_amp * (2 * (t * frequency - math.floor(t * frequency + 0.5))))
        # Fade out
        fade = max(0, 1 - (i / n_samples) * 1.5)
        buf[i] = int(val * min(fade, 1.0))
    sound = pygame.mixer.Sound(buffer=buf)
    return sound

def generate_jump_sound():
    sample_rate = 22050
    duration = 0.15
    n = int(sample_rate * duration)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / sample_rate
        freq = 300 + (800 * t / duration)
        val = int(8000 * math.sin(2 * math.pi * freq * t))
        fade = 1 - t / duration
        buf[i] = int(val * fade)
    return pygame.mixer.Sound(buffer=buf)

def generate_coin_sound():
    sample_rate = 22050
    duration = 0.2
    n = int(sample_rate * duration)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / sample_rate
        if t < 0.1:
            freq = 988
        else:
            freq = 1319
        val = int(6000 * math.sin(2 * math.pi * freq * t))
        fade = 1 - t / duration
        buf[i] = int(val * fade)
    return pygame.mixer.Sound(buffer=buf)

def generate_stomp_sound():
    sample_rate = 22050
    duration = 0.12
    n = int(sample_rate * duration)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / sample_rate
        freq = 400 - (300 * t / duration)
        val = int(8000 * math.sin(2 * math.pi * freq * t))
        fade = 1 - t / duration
        buf[i] = int(val * fade)
    return pygame.mixer.Sound(buffer=buf)

def generate_die_sound():
    sample_rate = 22050
    duration = 0.6
    n = int(sample_rate * duration)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / sample_rate
        freq = 400 - (350 * t / duration)
        val = int(7000 * math.sin(2 * math.pi * freq * t))
        fade = 1 - (t / duration)
        buf[i] = int(val * fade * fade)
    return pygame.mixer.Sound(buffer=buf)

def generate_powerup_sound():
    sample_rate = 22050
    duration = 0.4
    n = int(sample_rate * duration)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / sample_rate
        freq = 500 + 600 * (t / duration)
        val = int(5000 * math.sin(2 * math.pi * freq * t))
        fade = 1 - (t / duration) * 0.5
        buf[i] = int(val * fade)
    return pygame.mixer.Sound(buffer=buf)

try:
    snd_jump = generate_jump_sound()
    snd_coin = generate_coin_sound()
    snd_stomp = generate_stomp_sound()
    snd_die = generate_die_sound()
    snd_powerup = generate_powerup_sound()
    snd_flag = generate_sound(523, 600, 0.2, 'sine')
except Exception:
    snd_jump = snd_coin = snd_stomp = snd_die = snd_powerup = snd_flag = None


# ─────────────────────────────────────────────
# Desenho de Sprites
# ─────────────────────────────────────────────

def draw_zebra_sprite(w, h, frame=0, facing_right=True, jumping=False):
    """Desenha a zebra pixel-art."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    body_w = int(w * 0.7)
    body_h = int(h * 0.35)
    body_x = int(w * 0.15)
    body_y = int(h * 0.3)

    # Corpo (elipse branca com listras)
    pygame.draw.ellipse(surf, ZEBRA_WHITE, (body_x, body_y, body_w, body_h))
    pygame.draw.ellipse(surf, ZEBRA_BLACK, (body_x, body_y, body_w, body_h), 2)

    # Listras no corpo
    stripe_count = 5
    for i in range(stripe_count):
        sx = body_x + int(body_w * (i + 1) / (stripe_count + 1))
        sy1 = body_y + 4
        sy2 = body_y + body_h - 4
        pygame.draw.line(surf, ZEBRA_BLACK, (sx, sy1), (sx - 2, sy2), 3)

    # Cabeça
    head_w = int(w * 0.3)
    head_h = int(h * 0.25)
    if facing_right:
        head_x = body_x + body_w - int(head_w * 0.3)
    else:
        head_x = body_x - int(head_w * 0.7)
    head_y = body_y - int(head_h * 0.6)

    # Focinho (retângulo arredondado)
    pygame.draw.ellipse(surf, ZEBRA_WHITE, (head_x, head_y, head_w, head_h))
    pygame.draw.ellipse(surf, ZEBRA_BLACK, (head_x, head_y, head_w, head_h), 2)

    # Olho
    eye_r = 3
    if facing_right:
        eye_x = head_x + int(head_w * 0.65)
    else:
        eye_x = head_x + int(head_w * 0.35)
    eye_y = head_y + int(head_h * 0.35)
    pygame.draw.circle(surf, ZEBRA_BLACK, (eye_x, eye_y), eye_r)
    pygame.draw.circle(surf, WHITE, (eye_x + 1, eye_y - 1), 1)

    # Orelhas
    ear_h = int(h * 0.12)
    if facing_right:
        ear_x = head_x + int(head_w * 0.5)
    else:
        ear_x = head_x + int(head_w * 0.4)
    ear_y = head_y - ear_h + 2
    pygame.draw.polygon(surf, ZEBRA_WHITE, [
        (ear_x - 3, head_y + 2),
        (ear_x, ear_y),
        (ear_x + 3, head_y + 2)
    ])
    pygame.draw.polygon(surf, ZEBRA_BLACK, [
        (ear_x - 3, head_y + 2),
        (ear_x, ear_y),
        (ear_x + 3, head_y + 2)
    ], 1)

    # Crina (mane)
    mane_points = []
    if facing_right:
        mx = head_x + int(head_w * 0.2)
    else:
        mx = head_x + int(head_w * 0.7)
    for i in range(6):
        my = head_y + i * 4
        offset = 4 if i % 2 == 0 else -2
        mane_points.append((mx + offset, my))
    if len(mane_points) > 2:
        pygame.draw.lines(surf, ZEBRA_BLACK, False, mane_points, 3)

    # Pernas
    leg_w = 5
    leg_h = int(h * 0.3)
    leg_y = body_y + body_h - 4

    if jumping:
        # Pernas dobradas
        offsets = [0.2, 0.4, 0.6, 0.8]
        for i, ox in enumerate(offsets):
            lx = body_x + int(body_w * ox) - leg_w // 2
            angle = 10 if i < 2 else -10
            pygame.draw.line(surf, ZEBRA_BLACK, (lx + leg_w // 2, leg_y),
                             (lx + leg_w // 2 + angle, leg_y + leg_h - 5), 4)
            # Casco
            pygame.draw.circle(surf, ZEBRA_GRAY, (lx + leg_w // 2 + angle, leg_y + leg_h - 5), 3)
    else:
        offsets = [0.2, 0.4, 0.6, 0.8]
        for i, ox in enumerate(offsets):
            lx = body_x + int(body_w * ox) - leg_w // 2
            anim_offset = 0
            if frame > 0:
                anim_offset = int(math.sin((frame * 0.3) + i * math.pi * 0.5) * 6)
            foot_y = leg_y + leg_h
            pygame.draw.line(surf, ZEBRA_BLACK, (lx + leg_w // 2, leg_y),
                             (lx + leg_w // 2 + anim_offset, foot_y), 4)
            # Casco
            pygame.draw.circle(surf, ZEBRA_GRAY, (lx + leg_w // 2 + anim_offset, foot_y), 3)

    # Cauda
    if facing_right:
        tail_x = body_x
    else:
        tail_x = body_x + body_w
    tail_y = body_y + 5
    tail_wave = math.sin(frame * 0.2) * 5 if frame else 0
    tail_dir = -1 if facing_right else 1
    tail_points = [
        (tail_x, tail_y),
        (tail_x + tail_dir * 10, tail_y - 8 + tail_wave),
        (tail_x + tail_dir * 15, tail_y - 3 + tail_wave),
    ]
    if len(tail_points) > 2:
        pygame.draw.lines(surf, ZEBRA_BLACK, False, tail_points, 3)

    return surf


def draw_turtle_sprite(w, h, frame=0, alive=True):
    """Desenha o inimigo tartaruga."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if not alive:
        # Shell only (pisado)
        shell_h = h // 3
        pygame.draw.ellipse(surf, TURTLE_SHELL, (2, h - shell_h - 2, w - 4, shell_h))
        pygame.draw.ellipse(surf, TURTLE_DARK, (2, h - shell_h - 2, w - 4, shell_h), 2)
        return surf

    # Corpo / casco
    shell_w = int(w * 0.8)
    shell_h = int(h * 0.55)
    sx = (w - shell_w) // 2
    sy = int(h * 0.2)
    pygame.draw.ellipse(surf, TURTLE_SHELL, (sx, sy, shell_w, shell_h))
    pygame.draw.ellipse(surf, TURTLE_DARK, (sx, sy, shell_w, shell_h), 2)
    # Detalhes no casco
    pygame.draw.line(surf, TURTLE_DARK, (sx + shell_w // 2, sy + 2), (sx + shell_w // 2, sy + shell_h - 2), 2)

    # Cabeça
    head_r = int(w * 0.18)
    hx = sx + shell_w - head_r
    hy = sy + 2
    pygame.draw.circle(surf, TURTLE_GREEN, (hx, hy), head_r)
    pygame.draw.circle(surf, TURTLE_DARK, (hx, hy), head_r, 1)
    # Olho
    pygame.draw.circle(surf, WHITE, (hx + 3, hy - 2), 3)
    pygame.draw.circle(surf, BLACK, (hx + 4, hy - 2), 1)

    # Pernas
    leg_y = sy + shell_h - 2
    anim = int(math.sin(frame * 0.3) * 3)
    pygame.draw.ellipse(surf, TURTLE_GREEN, (sx + 4, leg_y, 8, 10 + anim))
    pygame.draw.ellipse(surf, TURTLE_GREEN, (sx + shell_w - 12, leg_y, 8, 10 - anim))

    return surf


def draw_coin_sprite(w, h, frame=0):
    """Desenha uma moeda giratória."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    squeeze = abs(math.sin(frame * 0.08))
    coin_w = max(4, int(w * 0.6 * squeeze))
    cx = w // 2 - coin_w // 2
    cy = h // 4
    coin_h = int(h * 0.6)
    pygame.draw.ellipse(surf, COIN_COL, (cx, cy, coin_w, coin_h))
    pygame.draw.ellipse(surf, COIN_DARK, (cx, cy, coin_w, coin_h), 2)
    if coin_w > 10:
        font_small = pygame.font.SysFont('Arial', 14, bold=True)
        txt = font_small.render("$", True, COIN_DARK)
        surf.blit(txt, (w // 2 - txt.get_width() // 2, h // 2 - txt.get_height() // 2))
    return surf


def draw_qblock_sprite(w, h, hit=False):
    """Desenha um bloco de interrogação."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if hit:
        pygame.draw.rect(surf, CASTLE_GRAY, (0, 0, w, h))
        pygame.draw.rect(surf, CASTLE_DARK, (0, 0, w, h), 2)
        return surf
    pygame.draw.rect(surf, QBLOCK_COL, (0, 0, w, h))
    pygame.draw.rect(surf, QBLOCK_DARK, (0, 0, w, h), 3)
    # Brilho
    pygame.draw.line(surf, WHITE, (2, 2), (w - 2, 2), 2)
    pygame.draw.line(surf, WHITE, (2, 2), (2, h - 2), 2)
    # "?"
    font = pygame.font.SysFont('Arial', int(h * 0.6), bold=True)
    txt = font.render("?", True, BRICK_COL)
    surf.blit(txt, (w // 2 - txt.get_width() // 2, h // 2 - txt.get_height() // 2))
    return surf


def draw_brick_sprite(w, h):
    """Desenha um bloco de tijolos."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, BRICK_COL, (0, 0, w, h))
    # Linhas de tijolo
    pygame.draw.line(surf, BRICK_LINE, (0, h // 3), (w, h // 3), 1)
    pygame.draw.line(surf, BRICK_LINE, (0, 2 * h // 3), (w, 2 * h // 3), 1)
    pygame.draw.line(surf, BRICK_LINE, (w // 2, 0), (w // 2, h // 3), 1)
    pygame.draw.line(surf, BRICK_LINE, (w // 4, h // 3), (w // 4, 2 * h // 3), 1)
    pygame.draw.line(surf, BRICK_LINE, (3 * w // 4, h // 3), (3 * w // 4, 2 * h // 3), 1)
    pygame.draw.line(surf, BRICK_LINE, (w // 2, 2 * h // 3), (w // 2, h), 1)
    pygame.draw.rect(surf, BRICK_LINE, (0, 0, w, h), 2)
    return surf


def draw_pipe_sprite(w, h):
    """Desenha um cano verde."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    top_h = min(20, h // 3)
    # Capô do cano
    pygame.draw.rect(surf, PIPE_GREEN, (-4, 0, w + 8, top_h))
    pygame.draw.rect(surf, PIPE_LIGHT, (-4, 0, (w + 8) // 3, top_h))
    pygame.draw.rect(surf, PIPE_DARK, (-4, 0, w + 8, top_h), 2)
    # Corpo
    pygame.draw.rect(surf, PIPE_GREEN, (0, top_h, w, h - top_h))
    pygame.draw.rect(surf, PIPE_LIGHT, (0, top_h, w // 3, h - top_h))
    pygame.draw.rect(surf, PIPE_DARK, (0, top_h, w, h - top_h), 2)
    return surf


def draw_flag_sprite(pole_h):
    """Desenha o poste de bandeira final."""
    surf = pygame.Surface((40, pole_h), pygame.SRCALPHA)
    # Poste
    pygame.draw.rect(surf, FLAG_POLE, (18, 0, 4, pole_h))
    pygame.draw.rect(surf, BLACK, (18, 0, 4, pole_h), 1)
    # Bola no topo
    pygame.draw.circle(surf, COIN_COL, (20, 6), 6)
    pygame.draw.circle(surf, COIN_DARK, (20, 6), 6, 1)
    # Bandeira
    flag_points = [(22, 12), (40, 22), (22, 32)]
    pygame.draw.polygon(surf, FLAG_GREEN, flag_points)
    pygame.draw.polygon(surf, BLACK, flag_points, 1)
    return surf


# ─────────────────────────────────────────────
# Desenho de Cenário (Background)
# ─────────────────────────────────────────────

def draw_cloud(surf, x, y, size=1.0):
    r = int(20 * size)
    pygame.draw.circle(surf, CLOUD_WHITE, (x, y), r)
    pygame.draw.circle(surf, CLOUD_WHITE, (x - int(18 * size), y + 5), int(r * 0.75))
    pygame.draw.circle(surf, CLOUD_WHITE, (x + int(18 * size), y + 5), int(r * 0.75))
    pygame.draw.circle(surf, CLOUD_WHITE, (x - int(8 * size), y - int(5 * size)), int(r * 0.6))
    pygame.draw.circle(surf, CLOUD_WHITE, (x + int(8 * size), y - int(5 * size)), int(r * 0.6))


def draw_bush(surf, x, y, size=1.0):
    r = int(18 * size)
    pygame.draw.circle(surf, BUSH_GREEN, (x, y), r)
    pygame.draw.circle(surf, BUSH_GREEN, (x - int(16 * size), y + 2), int(r * 0.7))
    pygame.draw.circle(surf, BUSH_GREEN, (x + int(16 * size), y + 2), int(r * 0.7))
    pygame.draw.circle(surf, BUSH_DARK, (x, y), r, 2)


def draw_hill(surf, x, y, w, h):
    points = [(x, y), (x + w // 2, y - h), (x + w, y)]
    pygame.draw.polygon(surf, HILL_GREEN, points)
    pygame.draw.polygon(surf, HILL_DARK, points, 2)


# ─────────────────────────────────────────────
# Nível (Level Data)
# ─────────────────────────────────────────────
# Legenda do mapa:
# G = chão,  B = tijolo, Q = bloco de interrogação
# P = pipe (2 tiles de largura, 2-3 de altura)
# E = inimigo tartaruga, C = moeda
# F = bandeira final
# . = vazio

LEVEL_MAP = [
    #         1111111111222222222233333333334444444444555555555566666666667777777777888888888899999999990000000000
    # 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
    "....................................................................................................",  # 0
    "....................................................................................................",  # 1
    "....................................................................................................",  # 2
    "....................................................................................................",  # 3
    "....................................................................................................",  # 4
    ".......................BQBQB............................................................F.........",  # 5
    "....................................................................................................",  # 6
    "....................................................................................................",  # 7
    "..........BBBQB..................................BQBBB..............................................",  # 8
    "...............................................C..C..C..............................................",  # 9
    "........................................E.........................................E.................",  # 10
    "...................................GGGGGGGG...GGGGGGGG.............BQBQB............................",  # 11
    "....................................................................................................",  # 12
    "...........................................E........................................................",  # 13
    "GGGGGGGGGGGGGGGGGG...GGGGGGGGGGGGGG........GGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGG...GGGGGGGGGGGGGGGGGGG",  # 14
]

LEVEL_W = len(LEVEL_MAP[0])
LEVEL_H = len(LEVEL_MAP)
WORLD_W = LEVEL_W * TILE
WORLD_H = LEVEL_H * TILE

# ─────────────────────────────────────────────
# Parsear o nível
# ─────────────────────────────────────────────
class Tile:
    def __init__(self, tile_type, x, y, w=TILE, h=TILE):
        self.type = tile_type
        self.rect = pygame.Rect(x, y, w, h)
        self.hit = False
        self.coin_given = False
        self.bounce_timer = 0

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.vx = -1.5
        self.vy = 0
        self.alive = True
        self.death_timer = 0
        self.on_ground = False
        self.frame = 0

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 8, y + 4, TILE - 16, TILE - 8)
        self.collected = False
        self.frame = random.randint(0, 100)
        self.x = x
        self.y = y

class SpawnedCoin:
    """Moeda que aparece ao bater num bloco Q."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = -6
        self.timer = 30

class FlagPole:
    def __init__(self, x, y, h):
        self.rect = pygame.Rect(x + 16, y, 8, h)
        self.x = x
        self.y = y
        self.h = h
        self.touched = False

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.timer = random.randint(15, 30)
        self.color = color


def parse_level():
    tiles = []
    enemies = []
    coins = []
    flag = None
    pipes = []  # Track pipe positions to draw them

    for row_i, row in enumerate(LEVEL_MAP):
        for col_i, ch in enumerate(row):
            x = col_i * TILE
            y = row_i * TILE
            if ch == 'G':
                tiles.append(Tile('ground', x, y))
            elif ch == 'B':
                tiles.append(Tile('brick', x, y))
            elif ch == 'Q':
                tiles.append(Tile('qblock', x, y))
            elif ch == 'E':
                enemies.append(Enemy(x, y))
            elif ch == 'C':
                coins.append(Coin(x, y))
            elif ch == 'F':
                flag = FlagPole(x, y, (LEVEL_H - 1 - row_i) * TILE)

    return tiles, enemies, coins, flag


# ─────────────────────────────────────────────
# Decoração do cenário (posições fixas)
# ─────────────────────────────────────────────
BG_CLOUDS = [
    (150, 80, 1.2), (500, 50, 0.8), (900, 100, 1.0), (1400, 60, 1.3),
    (2000, 90, 0.9), (2600, 55, 1.1), (3200, 75, 0.7), (3800, 85, 1.0),
]
BG_BUSHES = [
    (200, LEVEL_H * TILE - TILE - 10, 1.0), (700, LEVEL_H * TILE - TILE - 10, 1.3),
    (1500, LEVEL_H * TILE - TILE - 10, 0.8), (2500, LEVEL_H * TILE - TILE - 10, 1.1),
    (3500, LEVEL_H * TILE - TILE - 10, 1.0),
]
BG_HILLS = [
    (100, LEVEL_H * TILE - TILE, 200, 80),
    (800, LEVEL_H * TILE - TILE, 300, 100),
    (1800, LEVEL_H * TILE - TILE, 250, 90),
    (2800, LEVEL_H * TILE - TILE, 200, 70),
    (3600, LEVEL_H * TILE - TILE, 280, 95),
]


# ─────────────────────────────────────────────
# Sprites pré-renderizados
# ─────────────────────────────────────────────
brick_surf = draw_brick_sprite(TILE, TILE)
qblock_surf = draw_qblock_sprite(TILE, TILE, hit=False)
qblock_hit_surf = draw_qblock_sprite(TILE, TILE, hit=True)
flag_surf = None  # Will be created per flag


# ─────────────────────────────────────────────
# Classe do Jogador
# ─────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 44, 44)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True
        self.frame = 0
        self.walk_timer = 0
        self.alive = True
        self.death_timer = 0
        self.death_y = 0
        self.score = 0
        self.coins_count = 0
        self.lives = 3
        self.invincible = 0  # Invincibility frames
        self.won = False
        self.win_timer = 0

    GRAVITY = 1.0
    MAX_FALL = 10
    SPEED = 4
    JUMP_FORCE = -20
    ACCEL = 0.5
    FRICTION = 0.3

    def update(self, keys, tiles):
        if not self.alive:
            self.death_timer += 1
            if self.death_timer < 20:
                self.vy = -5
            else:
                self.vy += self.GRAVITY
            self.rect.y += int(self.vy)
            return

        if self.won:
            self.win_timer += 1
            return

        # Horizontal
        if keys[pygame.K_RIGHT]:
            self.vx = min(self.vx + self.ACCEL, self.SPEED)
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.vx = max(self.vx - self.ACCEL, -self.SPEED)
            self.facing_right = False
        else:
            if self.vx > 0:
                self.vx = max(0, self.vx - self.FRICTION)
            elif self.vx < 0:
                self.vx = min(0, self.vx + self.FRICTION)

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.vy = self.JUMP_FORCE
            self.on_ground = False
            if snd_jump:
                snd_jump.play()

        # Variable jump height
        if not (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.vy < -3:
            self.vy = max(self.vy, -3)

        # Gravity
        self.vy = min(self.vy + self.GRAVITY, self.MAX_FALL)

        # Move X
        self.rect.x += int(self.vx)
        self._collide_x(tiles)

        # Move Y
        self.rect.y += int(self.vy)
        self._collide_y(tiles)

        # World bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = 0
        if self.rect.top > WORLD_H + 100:
            self.die()

        # Animation
        if abs(self.vx) > 0.5 and self.on_ground:
            self.walk_timer += 1
            self.frame = self.walk_timer
        elif not self.on_ground:
            self.frame = 0

        if self.invincible > 0:
            self.invincible -= 1

    def _collide_x(self, tiles):
        for t in tiles:
            if self.rect.colliderect(t.rect):
                if self.vx > 0:
                    self.rect.right = t.rect.left
                    self.vx = 0
                elif self.vx < 0:
                    self.rect.left = t.rect.right
                    self.vx = 0

    def _collide_y(self, tiles):
        self.on_ground = False
        for t in tiles:
            if self.rect.colliderect(t.rect):
                if self.vy > 0:
                    self.rect.bottom = t.rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = t.rect.bottom
                    self.vy = 0
                    # Hit block from below
                    if t.type == 'qblock' and not t.hit:
                        t.hit = True
                        t.bounce_timer = 8
                        return t  # Signal that we hit a Q block
                    elif t.type == 'brick':
                        t.bounce_timer = 5
        return None

    def die(self):
        if self.invincible > 0:
            return
        self.alive = False
        self.vy = 0
        self.death_timer = 0
        self.death_y = self.rect.y
        if snd_die:
            snd_die.play()

    def draw(self, surf, cam_x):
        if not self.alive and self.death_timer > 60:
            return
        if self.invincible > 0 and self.invincible % 4 < 2:
            return  # Blinking
        sx = self.rect.x - cam_x
        sy = self.rect.y
        jumping = not self.on_ground
        zebra = draw_zebra_sprite(self.rect.w, self.rect.h, self.frame,
                                   self.facing_right, jumping)
        surf.blit(zebra, (sx, sy))


# ─────────────────────────────────────────────
# Game Class
# ─────────────────────────────────────────────
class Game:
    STATE_TITLE = 0
    STATE_PLAY = 1
    STATE_GAMEOVER = 2
    STATE_WIN = 3

    def __init__(self):
        self.state = self.STATE_TITLE
        self.font_big = pygame.font.SysFont('Arial', 52, bold=True)
        self.font_med = pygame.font.SysFont('Arial', 28, bold=True)
        self.font_sm = pygame.font.SysFont('Arial', 20)
        self.font_hud = pygame.font.SysFont('Arial', 22, bold=True)
        self.title_frame = 0
        self.init_level()

    def init_level(self):
        self.tiles, self.enemies, self.coins, self.flag = parse_level()
        self.player = Player(80, (LEVEL_H - 3) * TILE)
        self.cam_x = 0
        self.spawned_coins = []
        self.particles = []
        self.time_left = 400
        self.time_tick = 0
        self.global_frame = 0

    def restart(self):
        self.init_level()
        self.state = self.STATE_PLAY

    def run(self):
        running = True
        while running:
            dt = clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if self.state == self.STATE_TITLE:
                        if event.key == pygame.K_RETURN:
                            self.restart()
                    elif self.state == self.STATE_GAMEOVER:
                        if event.key == pygame.K_RETURN:
                            self.state = self.STATE_TITLE
                    elif self.state == self.STATE_WIN:
                        if event.key == pygame.K_RETURN:
                            self.state = self.STATE_TITLE

            if self.state == self.STATE_TITLE:
                self.draw_title()
            elif self.state == self.STATE_PLAY:
                self.update_play()
                self.draw_play()
            elif self.state == self.STATE_GAMEOVER:
                self.draw_gameover()
            elif self.state == self.STATE_WIN:
                self.draw_win()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # ─── TITLE ────────────────────────────
    def draw_title(self):
        self.title_frame += 1
        screen.fill(SKY_BLUE)

        # Ground
        ground_y = SCREEN_H - 80
        pygame.draw.rect(screen, GROUND_BR, (0, ground_y, SCREEN_W, 80))
        pygame.draw.rect(screen, GROUND_TOP, (0, ground_y, SCREEN_W, 8))

        # Clouds
        draw_cloud(screen, 150, 100, 1.2)
        draw_cloud(screen, 500, 70, 0.9)
        draw_cloud(screen, 700, 120, 1.0)

        # Hills
        draw_hill(screen, 50, ground_y, 200, 80)
        draw_hill(screen, 500, ground_y, 300, 100)

        # Bushes
        draw_bush(screen, 200, ground_y - 5, 1.2)
        draw_bush(screen, 650, ground_y - 5, 0.8)

        # Title
        bounce = math.sin(self.title_frame * 0.05) * 8
        title = self.font_big.render("SUPER ZEBRA", True, WHITE)
        shadow = self.font_big.render("SUPER ZEBRA", True, BLACK)
        tx = SCREEN_W // 2 - title.get_width() // 2
        ty = 100 + bounce
        screen.blit(shadow, (tx + 3, ty + 3))
        screen.blit(title, (tx, ty))

        # Subtitle
        sub = self.font_med.render("Uma aventura listrada!", True, QBLOCK_COL)
        screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 175))

        # Zebra no título
        zebra = draw_zebra_sprite(80, 80, self.title_frame, True, False)
        screen.blit(zebra, (SCREEN_W // 2 - 40, ground_y - 85))

        # Press enter
        if (self.title_frame // 30) % 2 == 0:
            press = self.font_med.render("Pressione ENTER para jogar", True, WHITE)
            screen.blit(press, (SCREEN_W // 2 - press.get_width() // 2, SCREEN_H - 140))

        # Controls
        ctrl1 = self.font_sm.render("← → para mover   |   ESPAÇO ou ↑ para pular", True, WHITE)
        screen.blit(ctrl1, (SCREEN_W // 2 - ctrl1.get_width() // 2, SCREEN_H - 50))

    # ─── PLAY UPDATE ─────────────────────
    def update_play(self):
        if self.player.won:
            self.player.update([], self.tiles)
            if self.player.win_timer > 120:
                self.state = self.STATE_WIN
            return

        if not self.player.alive:
            self.player.update([], self.tiles)
            if self.player.death_timer > 90:
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.state = self.STATE_GAMEOVER
                else:
                    lives_save = self.player.lives
                    score_save = self.player.score
                    coins_save = self.player.coins_count
                    self.init_level()
                    self.player.lives = lives_save
                    self.player.score = score_save
                    self.player.coins_count = coins_save
            return

        keys = pygame.key.get_pressed()
        self.global_frame += 1

        # Timer
        self.time_tick += 1
        if self.time_tick >= 24:
            self.time_tick = 0
            self.time_left -= 1
            if self.time_left <= 0:
                self.player.die()

        # Update player
        self.player.update(keys, self.tiles)

        # Check Q blocks hit from below
        for t in self.tiles:
            if t.type == 'qblock' and t.hit and not t.coin_given:
                t.coin_given = True
                self.player.coins_count += 1
                self.player.score += 200
                self.spawned_coins.append(SpawnedCoin(t.rect.x + 4, t.rect.y - TILE))
                if snd_coin:
                    snd_coin.play()

            # Bounce animation
            if t.bounce_timer > 0:
                t.bounce_timer -= 1

        # Update enemies
        for e in self.enemies:
            if not e.alive:
                e.death_timer += 1
                continue
            e.frame += 1
            e.vy += 0.5
            e.vy = min(e.vy, 8)
            e.rect.x += int(e.vx)

            # Enemy-tile collision X
            for t in self.tiles:
                if e.rect.colliderect(t.rect):
                    if e.vx > 0:
                        e.rect.right = t.rect.left
                    else:
                        e.rect.left = t.rect.right
                    e.vx *= -1

            # Fall
            e.rect.y += int(e.vy)
            e.on_ground = False
            for t in self.tiles:
                if e.rect.colliderect(t.rect):
                    if e.vy >= 0:
                        e.rect.bottom = t.rect.top
                        e.vy = 0
                        e.on_ground = True

            # Fall off world
            if e.rect.top > WORLD_H + 50:
                e.alive = False

            # Check if player stomp
            if self.player.alive and e.alive:
                if self.player.rect.colliderect(e.rect):
                    # Check if stomping (player falling, feet above enemy center)
                    if self.player.vy > 0 and self.player.rect.bottom < e.rect.centery + 10:
                        e.alive = False
                        e.death_timer = 0
                        self.player.vy = -8
                        self.player.score += 100
                        if snd_stomp:
                            snd_stomp.play()
                        # Particles
                        for _ in range(8):
                            self.particles.append(Particle(e.rect.centerx, e.rect.centery,
                                                           random.choice([TURTLE_GREEN, TURTLE_SHELL, WHITE])))
                    else:
                        self.player.die()

        # Collect coins
        for c in self.coins:
            if not c.collected and self.player.rect.colliderect(c.rect):
                c.collected = True
                self.player.coins_count += 1
                self.player.score += 100
                if snd_coin:
                    snd_coin.play()
                for _ in range(5):
                    self.particles.append(Particle(c.rect.centerx, c.rect.centery,
                                                   random.choice([COIN_COL, COIN_DARK, WHITE])))

        # Spawned coins animation
        for sc in self.spawned_coins[:]:
            sc.vy += 0.3
            sc.y += sc.vy
            sc.timer -= 1
            if sc.timer <= 0:
                self.spawned_coins.remove(sc)

        # Particles
        for p in self.particles[:]:
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.2
            p.timer -= 1
            if p.timer <= 0:
                self.particles.remove(p)

        # Flag
        if self.flag and not self.flag.touched:
            if self.player.rect.colliderect(self.flag.rect):
                self.flag.touched = True
                self.player.won = True
                self.player.score += self.time_left * 10
                self.player.vx = 0
                if snd_flag:
                    snd_flag.play()

        # Camera
        target_cam = self.player.rect.centerx - SCREEN_W // 3
        self.cam_x += (target_cam - self.cam_x) * 0.1
        self.cam_x = max(0, min(self.cam_x, WORLD_W - SCREEN_W))

    # ─── PLAY DRAW ───────────────────────
    def draw_play(self):
        screen.fill(SKY_BLUE)
        cx = int(self.cam_x)

        # Background decorations (parallax)
        for hx, hy, hw, hh in BG_HILLS:
            draw_hill(screen, hx - int(cx * 0.3), hy, hw, hh)

        for bx, by, bs in BG_CLOUDS:
            draw_cloud(screen, bx - int(cx * 0.2), by, bs)

        for bx, by, bs in BG_BUSHES:
            draw_bush(screen, bx - cx, by, bs)

        # Tiles
        for t in self.tiles:
            sx = t.rect.x - cx
            sy = t.rect.y
            if sx < -TILE or sx > SCREEN_W + TILE:
                continue
            bounce_off = 0
            if t.bounce_timer > 0:
                bounce_off = -int(math.sin(t.bounce_timer * 0.4) * 6)

            if t.type == 'ground':
                pygame.draw.rect(screen, GROUND_BR, (sx, sy + bounce_off, TILE, TILE))
                pygame.draw.rect(screen, GROUND_TOP, (sx, sy + bounce_off, TILE, 6))
                pygame.draw.rect(screen, (100, 65, 30), (sx, sy + bounce_off, TILE, TILE), 1)
            elif t.type == 'brick':
                screen.blit(brick_surf, (sx, sy + bounce_off))
            elif t.type == 'qblock':
                if t.hit:
                    screen.blit(qblock_hit_surf, (sx, sy + bounce_off))
                else:
                    screen.blit(qblock_surf, (sx, sy + bounce_off))

        # Coins
        for c in self.coins:
            if c.collected:
                continue
            c.frame += 1
            sx = c.x - cx
            sy = c.y
            if -TILE < sx < SCREEN_W + TILE:
                coin_s = draw_coin_sprite(TILE, TILE, c.frame)
                screen.blit(coin_s, (sx, sy))

        # Spawned coins
        for sc in self.spawned_coins:
            sx = sc.x - cx
            coin_s = draw_coin_sprite(TILE, TILE, self.global_frame)
            screen.blit(coin_s, (sx, sc.y))

        # Enemies
        for e in self.enemies:
            if not e.alive and e.death_timer > 30:
                continue
            sx = e.rect.x - cx
            sy = e.rect.y
            if -TILE < sx < SCREEN_W + TILE:
                ts = draw_turtle_sprite(TILE, TILE, e.frame, e.alive)
                screen.blit(ts, (sx, sy))

        # Flag
        if self.flag:
            sx = self.flag.x - cx
            sy = self.flag.y
            fs = draw_flag_sprite(self.flag.h)
            screen.blit(fs, (sx, sy))

        # Particles
        for p in self.particles:
            px = int(p.x - cx)
            py = int(p.y)
            pygame.draw.circle(screen, p.color, (px, py), 3)

        # Player
        self.player.draw(screen, cx)

        # HUD
        self.draw_hud()

    def draw_hud(self):
        # Semi-transparent bar
        hud_bar = pygame.Surface((SCREEN_W, 36), pygame.SRCALPHA)
        hud_bar.fill((0, 0, 0, 120))
        screen.blit(hud_bar, (0, 0))

        # Score
        score_txt = self.font_hud.render(f"SCORE: {self.player.score:06d}", True, WHITE)
        screen.blit(score_txt, (15, 7))

        # Coins
        coin_icon = draw_coin_sprite(22, 22, self.global_frame)
        screen.blit(coin_icon, (240, 5))
        coin_txt = self.font_hud.render(f"x {self.player.coins_count:02d}", True, COIN_COL)
        screen.blit(coin_txt, (265, 7))

        # Lives
        lives_txt = self.font_hud.render(f"VIDAS: {self.player.lives}", True, WHITE)
        screen.blit(lives_txt, (400, 7))

        # Time
        time_color = RED if self.time_left < 60 else WHITE
        time_txt = self.font_hud.render(f"TEMPO: {self.time_left:03d}", True, time_color)
        screen.blit(time_txt, (SCREEN_W - 170, 7))

        # World
        world_txt = self.font_hud.render("MUNDO 1-1", True, WHITE)
        screen.blit(world_txt, (SCREEN_W // 2 - world_txt.get_width() // 2 + 80, 7))

    # ─── GAME OVER ───────────────────────
    def draw_gameover(self):
        screen.fill(BLACK)
        go_txt = self.font_big.render("GAME OVER", True, RED)
        screen.blit(go_txt, (SCREEN_W // 2 - go_txt.get_width() // 2, SCREEN_H // 2 - 60))

        score_txt = self.font_med.render(f"Score Final: {self.player.score}", True, WHITE)
        screen.blit(score_txt, (SCREEN_W // 2 - score_txt.get_width() // 2, SCREEN_H // 2 + 20))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            retry = self.font_sm.render("Pressione ENTER para voltar ao menu", True, QBLOCK_COL)
            screen.blit(retry, (SCREEN_W // 2 - retry.get_width() // 2, SCREEN_H // 2 + 80))

        # Zebra triste
        zebra = draw_zebra_sprite(60, 60, 0, True, False)
        screen.blit(zebra, (SCREEN_W // 2 - 30, SCREEN_H // 2 - 150))

    # ─── WIN ─────────────────────────────
    def draw_win(self):
        screen.fill(SKY_BLUE)
        # Confetti
        for _ in range(30):
            px = random.randint(0, SCREEN_W)
            py = random.randint(0, SCREEN_H)
            color = random.choice([RED, COIN_COL, FLAG_GREEN, WHITE, ORANGE, QBLOCK_COL])
            size = random.randint(3, 8)
            pygame.draw.rect(screen, color, (px, py, size, size))

        win_txt = self.font_big.render("VOCÊ VENCEU!", True, COIN_COL)
        shadow = self.font_big.render("VOCÊ VENCEU!", True, BLACK)
        wx = SCREEN_W // 2 - win_txt.get_width() // 2
        wy = SCREEN_H // 2 - 80
        screen.blit(shadow, (wx + 3, wy + 3))
        screen.blit(win_txt, (wx, wy))

        score_txt = self.font_med.render(f"Score Final: {self.player.score}", True, WHITE)
        screen.blit(score_txt, (SCREEN_W // 2 - score_txt.get_width() // 2, SCREEN_H // 2))

        coins_txt = self.font_med.render(f"Moedas: {self.player.coins_count}", True, COIN_COL)
        screen.blit(coins_txt, (SCREEN_W // 2 - coins_txt.get_width() // 2, SCREEN_H // 2 + 40))

        zebra = draw_zebra_sprite(80, 80, pygame.time.get_ticks() // 50, True, True)
        screen.blit(zebra, (SCREEN_W // 2 - 40, SCREEN_H // 2 - 180))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            retry = self.font_sm.render("Pressione ENTER para voltar ao menu", True, WHITE)
            screen.blit(retry, (SCREEN_W // 2 - retry.get_width() // 2, SCREEN_H // 2 + 100))


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == "__main__":
    game = Game()
    game.run()
