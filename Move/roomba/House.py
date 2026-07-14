"""
House layout simulator: 3 rooms + a hallway, each room >= 16 tiles,
with one room dirtier than the others.
"""

import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import to_rgba


class Tile:
    """A single floor tile. Belongs to a room (or the hallway) and can be dirty or clean."""

    def __init__(self, room, dirty_chance):
        self.room = room                # name of the room/hallway this tile belongs to
        self.dirty_chance = dirty_chance  # probability this tile becomes dirty on a roll
        self.dirty = False
        self.hasRoomba = False  # whether a Roomba is currently on this tile
        self.isCharger = False  # whether this tile is a charging station for the Roomba

    def roll_dirt(self):
        """Randomly decide if this tile becomes dirty, weighted by its room's dirty_chance."""
        # Charging stations are always clean, and don't get dirty.
        if not self.isCharger:
            self.dirty = random.random() < self.dirty_chance

    def clean(self):
        self.dirty = False


class House:
    """
    Grid-based house made of 3 rooms (each >= 16 tiles) and a connecting hallway.

    Layout (row, col) on a 9-row x 13-col grid:

        Room A (top-left, 4x4=16)      Room B (top-right, 4x4=16)
                     \\                        /
                      ------ Hallway (row 4) ------
                                  |
                          Room C (bottom, 4x4=16)   <- the messy one

    room_dirt_chances lets you control how likely each room is to get dirty.
    Room C defaults to a much higher chance than A, B, or the hallway.
    """

    WALL = None  # grid cells that aren't part of any room/hallway

    def __init__(self, room_dirt_chances=None):
        self.width = 13
        self.height = 9

        # Default: Room C is the "messy" room -- 3x more likely to get dirty.
        self.room_dirt_chances = room_dirt_chances or {
            "Room A": 0.15,
            "Room B": 0.15,
            "Room C": 0.55,   # <-- the dirtier room
            "Hallway": 0.05,
        }

        # room_name -> (row_start, col_start, row_end, col_end) inclusive
        self.room_bounds = {
            "Room A": (0, 0, 3, 3),     # 4x4 = 16 tiles
            "Room B": (0, 9, 3, 12),    # 4x4 = 16 tiles
            "Room C": (5, 4, 8, 7),     # 4x4 = 16 tiles
        }
        # Hallway: a corridor connecting all three rooms
        self.charger_position = (4, 6)  # row, col of the charging station in the hallway
        self.hallway_cells = (
            [(4, c) for c in range(0, 13)] +   # horizontal corridor, row 4
            [(r, 5) for r in range(4, 5)] +    # (kept simple/explicit below)
            [(r, 6) for r in range(4, 8)]      # vertical drop down into Room C
        )

        self.grid = [[self.WALL for _ in range(self.width)] for _ in range(self.height)]
        
        self._build_rooms()
        self._build_hallway()
        self.grid[self.charger_position[0]][self.charger_position[1]].isCharger = True
        self.roll_all_dirt()
        

    def _build_rooms(self):
        for room_name, (r0, c0, r1, c1) in self.room_bounds.items():
            chance = self.room_dirt_chances[room_name]
            tile_count = 0
            for r in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    self.grid[r][c] = Tile(room_name, chance)
                    tile_count += 1
            assert tile_count >= 16, f"{room_name} has only {tile_count} tiles (< 16)"

    def _build_hallway(self):
        chance = self.room_dirt_chances["Hallway"]
        for (r, c) in self.hallway_cells:
            if self.grid[r][c] is self.WALL:
                self.grid[r][c] = Tile("Hallway", chance)

    def roll_all_dirt(self):
        """Simulate a moment in time: every tile independently rolls for dirt."""
        for row in self.grid:
            for tile in row:
                if tile is not None:
                    tile.roll_dirt()

    def clean_all(self):
        for row in self.grid:
            for tile in row:
                if tile is not None:
                    tile.clean()

    def stats(self):
        """Return dirty-tile counts per room."""
        counts = {name: {"dirty": 0, "total": 0} for name in self.room_dirt_chances}
        for row in self.grid:
            for tile in row:
                if tile is not None:
                    counts[tile.room]["total"] += 1
                    if tile.dirty:
                        counts[tile.room]["dirty"] += 1
        return counts

    def print_ascii(self):
        """Quick text view: '.' clean, 'X' dirty, ' ' wall/exterior, 'ø' charger, 'O' roomba."""
        # 
        for row in self.grid:
            line = ""
            for tile in row:
                if tile is None:
                    line += " "
                elif tile.isCharger:
                    line += "ø"
                elif tile.hasRoomba: # the tile is roomba is on can be dirty or clean, but we want to show the roomba
                    line += "O"
                elif tile.dirty:
                    line += "X"
                else:
                    line += "."
            print(line)

    def display(self, save_path=None):
        """Render the house with matplotlib: rooms colored, dirty tiles marked."""
        room_colors = {
            "Room A": "#a8d5ba",
            "Room B": "#a8c5d5",
            "Room C": "#e8b4a0",
            "Hallway": "#dcdcdc",
        }

        fig, ax = plt.subplots(figsize=(9, 6.2))

        for r in range(self.height):
            for c in range(self.width):
                tile = self.grid[r][c]
                if tile is None:
                    continue
                x, y = c, self.height - 1 - r  # flip so row 0 is at top
                face = to_rgba(room_colors[tile.room], alpha=0.9 if tile.dirty else 0.35)
                rect = patches.Rectangle((x, y), 1, 1, facecolor=room_colors[tile.room],
                                          alpha=0.85 if not tile.dirty else 0.5,
                                          edgecolor="white", linewidth=1)
                ax.add_patch(rect)
                if tile.dirty:
                    ax.plot(x + 0.5, y + 0.5, marker="o", markersize=10,
                            markerfacecolor="#5c3a21", markeredgecolor="#3b2414")

        # Room labels
        for room_name, (r0, c0, r1, c1) in self.room_bounds.items():
            cx = (c0 + c1 + 1) / 2
            cy = self.height - 1 - (r0 + r1) / 2 + 0.5
            chance = self.room_dirt_chances[room_name]
            ax.text(cx, cy + 1.8, f"{room_name}\n(dirt chance: {chance:.0%})",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

        ax.text(6.5, self.height - 1 - 4 + 0.5, "Hallway", ha="center", va="center",
                fontsize=9, style="italic", color="#555")

        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_aspect("equal")
        ax.axis("off")

        legend_clean = patches.Patch(facecolor="#cccccc", alpha=0.35, label="Clean tile")
        legend_dirty = patches.Patch(facecolor="#5c3a21", label="Dirty tile")
        ax.legend(handles=[legend_clean, legend_dirty], loc="upper center",
                  bbox_to_anchor=(0.5, -0.02), ncol=2, frameon=False)

        plt.title("House Layout: 3 Rooms + Hallway", fontsize=13, fontweight="bold")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved to {save_path}")
        plt.show()
        return fig


if __name__ == "__main__":
    house = House()
    print("ASCII view:")
    house.print_ascii()
    print("\nDirty tile stats:")
    for room, s in house.stats().items():
        print(f"  {room}: {s['dirty']} / {s['total']} dirty")
    # house.display(save_path="/mnt/user-data/outputs/house_layout.png")