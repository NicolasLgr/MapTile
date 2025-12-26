import random
from PIL import Image

# =========================
# CONFIG
# =========================

WIDTH = 15
HEIGHT = 15
TILE_SIZE = 64
OUTPUT = "labyrinthe.png"
IMG = "image/"

# =========================
# DIRECTIONS
# =========================

DIRS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

# =========================
# GENERATION DU LABYRINTHE (DFS)
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

    dfs(0, 0)
    return maze

# =========================
# FORCER UNE CROIX AU DÉPART
# =========================

def force_start_cross(maze, x, y):
    for d, (dx, dy) in DIRS.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
            maze[y][x][d] = True
            maze[ny][nx][OPPOSITE[d]] = True

# =========================
# TILE MAP
# =========================

TILE_MAP = {
    # Droites
    frozenset({"N","S"}): ("tout_droit.png", 0),
    frozenset({"E","W"}): ("tout_droit.png", 90),

    # Courbes (déjà orientées)
    frozenset({"S","W"}): ("tourne-S-W.png", 0),
    frozenset({"N","W"}): ("tourne-N-W.png", 0),
    frozenset({"N","E"}): ("tourne-N-E.png", 0),
    frozenset({"S","E"}): ("tourne-S-E.png", 0),

    # T (forme_T ouvert S-W-E par défaut)
    frozenset({"S","E","W"}): ("forme_T.png", 0),    # fermé N
    frozenset({"N","E","W"}): ("forme_T.png", 180),  # fermé S
    frozenset({"N","S","W"}): ("forme_T.png", 270),  # fermé E
    frozenset({"N","S","E"}): ("forme_T.png", 90),   # fermé W

    # Croix
    frozenset({"N","E","S","W"}): ("croix.png", 0),

    # Cul-de-sac (ouvert S par défaut)
    frozenset({"S"}): ("cul_de_sac.png", 0),
    frozenset({"E"}): ("cul_de_sac.png", 90),
    frozenset({"N"}): ("cul_de_sac.png", 180),
    frozenset({"W"}): ("cul_de_sac.png", 270),
}

# =========================
# RENDER
# =========================

def render(maze, start_pos, end_pos):
    img = Image.new("RGBA", (WIDTH*TILE_SIZE, HEIGHT*TILE_SIZE))

    for y in range(HEIGHT):
        for x in range(WIDTH):
            opens = {d for d, v in maze[y][x].items() if v}

            tile_file, rot = TILE_MAP[frozenset(opens)]
            tile = Image.open(IMG + tile_file).resize((TILE_SIZE, TILE_SIZE))

            if (
                "forme_T" in tile_file or
                "tout_droit" in tile_file or
                "cul_de_sac" in tile_file
            ):
                tile = tile.rotate(rot, expand=True)

            img.paste(tile, (x*TILE_SIZE, y*TILE_SIZE), tile)

    # Overlay départ
    sx, sy = start_pos
    depart = Image.open(IMG + "depart.png").resize((TILE_SIZE, TILE_SIZE))
    img.paste(depart, (sx*TILE_SIZE, sy*TILE_SIZE), depart)

    # Overlay arrivée
    ex, ey = end_pos
    arrive = Image.open(IMG + "arrive.png").resize((TILE_SIZE, TILE_SIZE))
    img.paste(arrive, (ex*TILE_SIZE, ey*TILE_SIZE), arrive)

    img.save(OUTPUT)
    print(f"✅ Labyrinthe généré : {OUTPUT}")

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    maze = generate_maze()

    # Départ au centre
    start_x, start_y = WIDTH // 2, HEIGHT // 2
    force_start_cross(maze, start_x, start_y)

    # Arrivée dans le coin opposé
    end_x, end_y = WIDTH - 1, HEIGHT - 1

    render(maze, (start_x, start_y), (end_x, end_y))
