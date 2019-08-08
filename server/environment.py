import random
import math
from .world import Tile

def generate_random_map(width, height):
    random.seed(9001)
    def get_noise(width, height):
        noise = [[r for r in range(width)] for i in range(height)]

        for i in range(height):
            for j in range(width):
                noise[i][j] = random.randint(0,5)

        return noise

    noise = get_noise(width,height)

    grid = [[e for e in range(width)] for i in range(height)]
    for y in range(height):
        for x in range(width):
            value = noise[y][x]
            if value == 0:
                grid[y][x] = Tile(tile_id="tree", is_dense=True)
            elif value < 3:
                grid[y][x] = Tile(tile_id="grass", is_dense=False)
            else:
                grid[y][x] = Tile(tile_id="ground", is_dense=False)
                
    return grid
