import random
from collections import deque
import pygame
from PIL import Image

# =========================
# CONFIG
# =========================

WIDTH = 15
HEIGHT = 15
TILE_SIZE = 36  # réduit pour tenir à l'écran
IMG = "image/"

PLAYERS_COLOR = [(255, 0, 0), (91, 245, 39), (0, 0, 255)]
PLAYER_RADIUS = 6  # point plus petit

# =========================
# DIRECTIONS
# =========================

DIRS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

# =========================
# GENERATION LABYRINTHE
# =========================

def generate_maze():
    maze = [[{d: False for d in DIRS} for _ in range(WIDTH)] for _ in range(HEIGHT)]
    visited = [[False]*WIDTH for _ in range(HEIGHT)]
    def dfs(x, y):
        visited[y][x] = True
        dirs = list(DIRS.keys())
        random.shuffle(dirs)
        for d in dirs:
            dx, dy = DIRS[d]
            nx, ny = x + dx, y + dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and not visited[ny][nx]:
                maze[y][x][d] = True
                maze[ny][nx][OPPOSITE[d]] = True
                dfs(nx, ny)
    dfs(0,0)
    return maze

def add_loops(maze, chance=0.15):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            for d, (dx, dy) in DIRS.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                    if not maze[y][x][d] and random.random() < chance:
                        maze[y][x][d] = True
                        maze[ny][nx][OPPOSITE[d]] = True

# =========================
# TILE MAP
# =========================

TILE_MAP = {
    frozenset({"N","S"}): ("tout_droit.png", 0),
    frozenset({"E","W"}): ("tout_droit.png", 90),
    frozenset({"S","W"}): ("tourne-S-W.png", 0),
    frozenset({"N","W"}): ("tourne-N-W.png", 0),
    frozenset({"N","E"}): ("tourne-N-E.png", 0),
    frozenset({"S","E"}): ("tourne-S-E.png", 0),
    frozenset({"S","E","W"}): ("forme_T.png", 0),
    frozenset({"N","E","W"}): ("forme_T.png", 180),
    frozenset({"N","S","W"}): ("forme_T.png", 270),
    frozenset({"N","S","E"}): ("forme_T.png", 90),
    frozenset({"N","E","S","W"}): ("croix.png", 0),
    frozenset({"S"}): ("cul_de_sac.png", 0),
    frozenset({"E"}): ("cul_de_sac.png", 90),
    frozenset({"N"}): ("cul_de_sac.png", 180),
    frozenset({"W"}): ("cul_de_sac.png", 270),
}

# =========================
# MOUVEMENTS JOUEURS
# =========================

def get_available_moves(maze, pos):
    x, y = pos
    moves = {}
    for d, (dx, dy) in DIRS.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and maze[y][x][d]:
            moves[d] = (nx, ny)
    return moves

def find_far_end(maze, start):
    sx, sy = start
    queue = deque([(sx, sy)])
    dist = {(sx, sy): 0}
    while queue:
        x, y = queue.popleft()
        for d, open_ in maze[y][x].items():
            if open_:
                dx, dy = DIRS[d]
                nx, ny = x + dx, y + dy
                if (nx, ny) not in dist:
                    dist[(nx, ny)] = dist[(x, y)] + 1
                    queue.append((nx, ny))
    max_d = max(dist.values())
    far = [p for p, d in dist.items() if d >= max_d * 0.8]
    return random.choice(far)

# =========================
# GENERATION IMAGE COMPLETE
# =========================

def generate_full_image(maze, start, end):
    img = Image.new("RGBA", (WIDTH*TILE_SIZE, HEIGHT*TILE_SIZE))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if (x, y) == start:
                tile_file = "depart.png"
                rot = 0
            elif (x, y) == end:
                tile_file = "arrive.png"
                rot = 0
            else:
                opens = {d for d,v in maze[y][x].items() if v}
                tile_file, rot = TILE_MAP[frozenset(opens)]
            tile = Image.open(IMG + tile_file).resize((TILE_SIZE, TILE_SIZE))
            if "forme_T" in tile_file or "tout_droit" in tile_file or "cul_de_sac" in tile_file:
                tile = tile.rotate(rot)
            img.paste(tile, (x*TILE_SIZE, y*TILE_SIZE), tile)
    img.save("labyrinthe_complete.png")
    print("✅ Image complète du labyrinthe générée : labyrinthe_complete.png")

# =========================
# INITIALISATION PYGAME
# =========================

pygame.init()
screen = pygame.display.set_mode((WIDTH*TILE_SIZE, HEIGHT*TILE_SIZE + 60))
pygame.display.set_caption("Labyrinthe Tour par Tour")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)

maze = generate_maze()
add_loops(maze, 0.15)

# =========================
# FORCER DEPART COMME CROIX
# =========================

start = (WIDTH//2, HEIGHT//2)
sx, sy = start
maze[sy][sx] = {d: True for d in DIRS}  # toutes directions ouvertes
for d, (dx, dy) in DIRS.items():
    nx, ny = sx + dx, sy + dy
    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
        maze[ny][nx][OPPOSITE[d]] = True

end = find_far_end(maze, start)

# Génération image complète
generate_full_image(maze, start, end)

players = [{"color": c, "pos": start} for c in PLAYERS_COLOR]
current_player = 0
visited_tiles = [[False]*WIDTH for _ in range(HEIGHT)]
visited_tiles[start[1]][start[0]] = True

# =========================
# BOUCLE PRINCIPALE
# =========================

running = True
while running:
    screen.fill((0,0,0))

    # Affichage carte explorée
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if visited_tiles[y][x]:
                if (x, y) == start:
                    tile_file = "depart.png"
                    rot = 0
                elif (x, y) == end:
                    tile_file = "arrive.png"
                    rot = 0
                else:
                    opens = {d for d,v in maze[y][x].items() if v}
                    tile_file, rot = TILE_MAP[frozenset(opens)]
                tile = pygame.image.load(IMG + tile_file).convert_alpha()
                tile = pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))
                if "forme_T" in tile_file or "tout_droit" in tile_file or "cul_de_sac" in tile_file:
                    tile = pygame.transform.rotate(tile, rot)
                screen.blit(tile, (x*TILE_SIZE, y*TILE_SIZE))

    # Dessiner tous les joueurs
    for i, p in enumerate(players):
        px, py = p["pos"]
        offset = [-10, 0, 10]
        pygame.draw.circle(screen, p["color"],
                           (px*TILE_SIZE + TILE_SIZE//2 + offset[i], py*TILE_SIZE + TILE_SIZE//2),
                           PLAYER_RADIUS)

    # Joueur actif
    player_color = players[current_player]["color"]
    pygame.draw.rect(screen, player_color, (10, HEIGHT*TILE_SIZE + 5, 20, 20))
    screen.blit(font.render("Joueur actif", True, (255,255,255)), (35, HEIGHT*TILE_SIZE + 5))

    # Boutons directionnels
    btns = {
        "N": pygame.Rect(WIDTH*TILE_SIZE//2 - TILE_SIZE//2, HEIGHT*TILE_SIZE + 5, TILE_SIZE, 20),
        "S": pygame.Rect(WIDTH*TILE_SIZE//2 - TILE_SIZE//2, HEIGHT*TILE_SIZE + 35, TILE_SIZE, 20),
        "W": pygame.Rect(WIDTH*TILE_SIZE//2 - TILE_SIZE - 5, HEIGHT*TILE_SIZE + 20, TILE_SIZE, 20),
        "E": pygame.Rect(WIDTH*TILE_SIZE//2 + 5, HEIGHT*TILE_SIZE + 20, TILE_SIZE, 20)
    }
    for d, rect in btns.items():
        pygame.draw.rect(screen, (200,200,200), rect)
        screen.blit(font.render(d, True, (0,0,0)), (rect.x + 5, rect.y + 2))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            player = players[current_player]
            moves = get_available_moves(maze, player["pos"])
            for d, rect in btns.items():
                if rect.collidepoint(mx, my) and d in moves:
                    player["pos"] = moves[d]
                    visited_tiles[player["pos"][1]][player["pos"][0]] = True
                    if player["pos"] == end:
                        print(f"Joueur de couleur {player_color} a gagné !")
                        running = False
                    current_player = (current_player + 1) % len(players)

    clock.tick(30)

pygame.quit()
