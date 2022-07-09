# %%
import random
from math import sin, cos, pi
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Circle
from matplotlib.backends.backend_pdf import PdfPages
import argparse

DEFAULT_MAP_SIZE = (10, 10)
MAP_CHOICES = ["RECTANGLE", "TRIANGLE", "DIAMOND"]
DEFAULT_MAP_TYPE = MAP_CHOICES[0]
FISH_ALPHA = 0.5
FISH_ANGLES = {i: [j / i * 2 * pi for j in range(i)] for i in range(2, 6)}
FISH_COLORS = ["white", "green", "purple", "orange", "red", "blue"]
FISH_GROUP_RADIUS = 0.2
FISH_RADIUS = [0, 0.13, 0.12, 0.11, 0.10, 0.09]
FIVE_TILE_CHANCE = 0.05
TILES_PERCENTAGE = [-1, 50, 33, 16, -1, -1]
VERTICLE_SPACING = 0.866667
ZERO_PERCENTAGES = (1, 10)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--rows", type=int, help="Map size in rows", default=DEFAULT_MAP_SIZE[0]
)
parser.add_argument(
    "--cols", type=int, help="Map size in columns", default=DEFAULT_MAP_SIZE[1]
)
parser.add_argument(
    "--shape",
    help="Shape of the map. DEFAULT: RANDOM",
    choices=MAP_CHOICES,
    default="RANDOM",
)
parser.add_argument("--no", help="Number of maps to generate", default=1, type=int)
parser.add_argument("--out", help="Output file name", default="map.pdf")
args = parser.parse_args()


class MapObject:
    def __init__(self, type=DEFAULT_MAP_TYPE, size=DEFAULT_MAP_SIZE) -> None:
        self.size = size
        self.type = type
        self._ratio = None
        self._map = None
        if type == "RECTANGLE":
            self._map = self._generate_rect_map()
        elif type == "TRIANGLE":
            self._map = self._generate_tri_map()
        elif type == "DIAMOND":
            self._map = self._generate_diamond_map()

    @property
    def map(self) -> list:
        return self._map

    @property
    def R(self) -> int:
        return self.size[0]

    @property
    def C(self) -> int:
        if self.type == "TRIANGLE":
            return self.R + 1
        elif self.type == "DIAMOND":
            return int(self.R * 1.5 + 1)
        return self.size[1]

    @property
    def ratio(self) -> float:
        return self._ratio

    @property
    def tiles_cnt(self) -> tuple:
        return sum(self._ratio[1:])

    def _generate_rect_map(self) -> None:
        """Generate map."""
        R, C = self.R, self.C
        pts = self._generate_pts(R * C)
        return [(r, c, pts.pop()) for r in range(R) for c in range(C)]

    def _generate_tri_map(self) -> None:
        """Generate map."""
        R, C = self.R, self.C
        pts = self._generate_pts(R * (R + 1) // 2)
        rv = []
        for r in range(R):
            for c in range(C):
                fish = pts.pop() if c * 2 > r and c * 2 + r <= R * 2 else 0
                rv.append((r, c, fish))
        return rv

    def _generate_diamond_map(self) -> None:
        """Generate map."""
        R, C = self.R, self.C
        pts = self._generate_pts(R * R)
        rv = []
        for r in range(R):
            for c in range(C):
                fish = pts.pop() if c * 2 > r and c * 2 <= r + R * 2 else 0
                rv.append((r, c, fish))
        return rv

    def _generate_pts(self, area) -> None:
        """Generate random amount of fish for the map."""
        zeroes = random.randint(*ZERO_PERCENTAGES) * area // 100
        fives = 1 if random.randint(0, 100) <= FIVE_TILE_CHANCE * 100 else 0
        area = area - zeroes - fives
        ones = TILES_PERCENTAGE[1] * area // 100
        twos = TILES_PERCENTAGE[2] * area // 100
        threes = TILES_PERCENTAGE[3] * area // 100
        fours = area - ones - twos - threes
        pts = (
            [0] * zeroes
            + [1] * ones
            + [2] * twos
            + [3] * threes
            + [4] * fours
            + [5] * fives
        )
        random.shuffle(pts)
        self._ratio = [zeroes, ones, twos, threes, fours, fives]
        return pts


def add_fishes(ax, x, y, amt, color):
    """Add a number of fishes to a tile"""

    if amt == 1:
        ax.add_patch(Circle((x, y), FISH_RADIUS[amt], color=color, alpha=FISH_ALPHA))
    elif amt in FISH_ANGLES:
        for deg in FISH_ANGLES[amt]:
            cx = FISH_GROUP_RADIUS * cos(deg) + x
            cy = FISH_GROUP_RADIUS * sin(deg) + y
            ax.add_patch(
                Circle((cx, cy), FISH_RADIUS[amt], color=color, alpha=FISH_ALPHA)
            )


def add_tile(ax, x, y, value, color):
    """Add a tile to the map"""
    ax.add_patch(
        RegularPolygon(
            (x, y),
            numVertices=6,
            radius=0.56,
            facecolor=color,
            alpha=0.2,
            edgecolor="black" if value else "none",
            linewidth=0.2,
        )
    )


def generate_map(pdf, i, map_obj: MapObject):
    """Generate a map and save it to a pdf"""
    _, ax = plt.subplots(1)
    ax.set_aspect("equal")
    for row, col, value in map_obj.map:
        x = col + 0.5 if row % 2 else col
        y = row * VERTICLE_SPACING
        color = FISH_COLORS[value]
        add_tile(ax, x, y, value, color)
        add_fishes(ax, x, y, value, color)
    plt.xlim([-1, map_obj.C])
    plt.ylim([-1, map_obj.R])
    plt.axis("off")
    plt.title(
        f"""Map {i}. Type: {map_obj.type}. Size: {map_obj.size}. Ratio: {map_obj.ratio}. Tiles: {map_obj.tiles_cnt}. \n
        Ref: bit.ly/fish-map-gen""",
        fontsize=7,
    )
    plt
    pdf.savefig()
    plt.close()


def generate_maps(args):
    """Generate a number of maps and save them to a pdf"""
    print(f"Generating {args.no} {args.shape} maps with size {args.rows}x{args.cols}")
    with PdfPages(f"./{args.out}") as pdf:
        for i in range(1, args.no + 1):
            shape = args.shape
            if shape == "RANDOM":
                shape = random.choice(MAP_CHOICES)
            map_obj = MapObject(shape, (args.rows, args.cols))
            generate_map(pdf, i, map_obj)
            print(f"Generated {i} map")
    print("Done. File saved to ./" + args.out)


if __name__ == "__main__":
    generate_maps(args)
