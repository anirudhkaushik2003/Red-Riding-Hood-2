import opensimplex
import random
import numpy as np
from collections import deque
from constants import (SURFACE, GROUND, TREE, BOX, SCARECROW, FLOWER,
                       MINOTAUR, WIZARD, EYE, BUSH_SMALL, BUSH_MEDIUM,
                       CART, WHEEL, FLOWER_3, LOGS, WELL, OBSTACLE,
                       POLE, LAMP, POWERUP_ARROW_REFILL, POWERUP_TRIPLE_SHOT,
                       POWERUP_DAMAGE_X4, EMPTY, DIFFICULTY_SETTINGS, DIFF_HARD,
                       CHUNK_COLS, SHOP, GRANNY_HOUSE, BARRIER,
                       SHOPKEEPER, GRANNY_NPC)


def base_connect(data):
    test = np.array(data)
    height = 0
    for i in test[:, 8]:
        if i == SURFACE:
            for col in range(7, -1, -1):
                test[height][col] = SURFACE
                height += 1
                if height > 16:
                    height = 16
                test[height][col] = GROUND
                if height > 16:
                    height = 16
            break
        height += 1
    return list(test)


def _gen_terrain(num_samples, start_col, prev_y, difficulty=DIFF_HARD):
    """Generate terrain columns from noise samples. Returns (world_data, last_y, total_cols)."""
    diff = DIFFICULTY_SETTINGS[difficulty]

    arr = []
    for _ in range(num_samples):
        tmp = opensimplex.OpenSimplex(random.randint(0, 10000000))
        y = int(((tmp.noise2(1, 2) + 1) ** 0.25) * random.randint(5, 8))
        arr.append(y)

    total_cols = (num_samples * 5) + 5 + start_col
    world_data = [[EMPTY for _ in range(total_cols)] for _ in range(17)]

    i = start_col
    val = prev_y if prev_y is not None else arr[0]
    # Columns since last spawn of each type (for spacing)
    cols_since_eye = 0
    cols_since_mino = 0
    cols_since_wiz = 0
    cols_since_any = diff['min_spacing']  # allow spawn immediately at start
    terrain_col = 0  # count of terrain columns placed

    for y in arr:
        flatline = random.randint(2, 5)
        j = 0
        value = y

        while True:
            if abs(value - val) > 1:
                if value - val > 1:
                    val += 1
                if value - val < -1:
                    val -= 1
            else:
                val = value

            j += 1
            if i < total_cols and 16 - val >= 0:
                world_data[16 - val][i] = GROUND
                world_data[16 - val - 1][i] = SURFACE

                spawned = False
                can_spawn = (16 - val - 4 >= 0 and
                             cols_since_any >= diff['min_spacing'])

                # Eye spawn check
                if (can_spawn and not spawned and
                        cols_since_eye >= diff['eye_interval'] and
                        random.random() < diff['eye_chance']):
                    world_data[16 - val - 4][i] = EYE
                    cols_since_eye = 0
                    cols_since_any = 0
                    spawned = True

                # Minotaur spawn check
                if (can_spawn and not spawned and
                        cols_since_mino >= diff['mino_interval'] and
                        random.random() < diff['mino_chance']):
                    world_data[16 - val - 4][i] = MINOTAUR
                    cols_since_mino = 0
                    cols_since_any = 0
                    spawned = True

                # Wizard spawn check (hard only)
                if (can_spawn and not spawned and diff['spawn_wizards'] and
                        cols_since_wiz >= diff['wiz_interval'] and
                        random.random() < diff['wiz_chance']):
                    world_data[16 - val - 4][i] = WIZARD
                    cols_since_wiz = 0
                    cols_since_any = 0
                    spawned = True

                if not spawned:
                    _place_decorations(world_data, i, val)

                cols_since_eye += 1
                cols_since_mino += 1
                cols_since_wiz += 1
                cols_since_any += 1
                terrain_col += 1

            i += 1
            if j >= flatline:
                break

    return world_data, val, i


def _place_decorations(world_data, i, val):
    if 16 - val - 2 >= 0:
        if random.randint(0, 10) == 5:
            world_data[16 - val - 2][i] = TREE
        if random.randint(0, 50) == 5:
            world_data[16 - val - 2][i] = SCARECROW
        if random.randint(0, 18) == 5:
            world_data[16 - val - 2][i] = FLOWER
    if 16 - val - 3 >= 0:
        if random.randint(0, 20) == 7:
            world_data[16 - val - 3][i] = random.choice([
                POWERUP_ARROW_REFILL, POWERUP_TRIPLE_SHOT, POWERUP_DAMAGE_X4
            ])


def _append_ending(world_data, last_y):
    """Append a 20-column flat ending with Granny's house after the last terrain.
    Matches normal terrain: 1 SURFACE row + 1 GROUND row, nothing else."""
    ending_cols = 22  # 20 walkable + 2 for barrier
    # Match normal terrain layout: SURFACE at (16 - last_y - 1), GROUND at (16 - last_y)
    surface_row = 16 - last_y - 1
    ground_row = 16 - last_y
    cur_cols = len(world_data[0])

    # Append new columns — just 1 surface + 1 ground, like normal terrain
    for r in range(17):
        for c in range(ending_cols):
            if r == surface_row:
                world_data[r].append(SURFACE)
            elif r == ground_row:
                world_data[r].append(GROUND)
            else:
                world_data[r].append(EMPTY)

    # Place granny house one row ABOVE surface so it sits on the ground
    house_col = cur_cols + 8
    world_data[surface_row - 1][house_col] = GRANNY_HOUSE

    # Place granny NPC next to the house (same row as house)
    granny_col = house_col + 6
    if granny_col < cur_cols + ending_cols - 2:
        world_data[surface_row - 1][granny_col] = GRANNY_NPC

    # Clear any shops/shopkeepers from the last 30 columns before granny's house
    clear_start = max(0, cur_cols - 30)
    for r in range(17):
        for c in range(clear_start, cur_cols):
            if world_data[r][c] in (SHOP, SHOPKEEPER):
                world_data[r][c] = EMPTY

    # Barrier wall at the very end
    barrier_col = cur_cols + ending_cols - 1
    for r in range(17):
        if r < surface_row:
            world_data[r][barrier_col] = BARRIER

    return world_data


def _add_start_barrier(world_data):
    """Add invisible barrier at column 0 so player can't fall back."""
    for r in range(17):
        if world_data[r][0] == EMPTY:
            world_data[r][0] = BARRIER
    return world_data


def gen_new_world(difficulty=DIFF_HARD):
    """Generate a classic-mode world."""
    world_data, last_y, last_col = _gen_terrain(CHUNK_COLS, 8, None, difficulty)

    # Clear spawn area
    for r in range(15, 17):
        for c in range(4):
            world_data[r][c] = EMPTY

    # Trim trailing empty columns so the world ends where terrain ends
    trimmed = [row[:last_col] for row in world_data]

    # Append flat ending with Granny's house (20 columns after terrain ends)
    trimmed = _append_ending(trimmed, last_y)

    # Add start barrier
    trimmed = _add_start_barrier(trimmed)

    return trimmed, last_y


def gen_chunk(prev_y, difficulty=DIFF_HARD):
    """Generate a chunk for infinite mode. Returns (chunk_data_rows, last_y, num_cols).
    chunk_data_rows is 17 rows of just the new columns."""
    world_data, last_y, last_col = _gen_terrain(CHUNK_COLS, 0, prev_y, difficulty)

    # Trim trailing empty columns
    actual_cols = last_col
    trimmed = []
    for row in world_data:
        trimmed.append(row[:actual_cols])

    return trimmed, last_y, actual_cols


def place_items(world, difficulty=DIFF_HARD):
    diff = DIFFICULTY_SETTINGS[difficulty]
    world_data = np.array(world)
    p = 0
    height_list = []
    q = deque()
    # Shops only start spawning after 1/3 of the world
    total_world_cols = len(world_data[0]) if len(world_data) > 0 else 300
    cols_since_shop = -(total_world_cols // 3)

    for i in world_data.T:
        height = 0
        for x in i:
            if x == SURFACE:
                break
            if height == 16:
                break
            height += 1
        height_list.append((p, height))
        p += 1

    i = 0
    while i < len(height_list):
        if height_list[i][1] != 16:
            q.append(height_list[i])
            n = 1
            for j in range(i + 1, len(height_list)):
                temp = q[-1]
                if temp[1] == height_list[j][1]:
                    q.append(height_list[j])
                    n += 1
                else:
                    # Try placing a shop on flat segments >= 6 wide
                    shop_placed = False
                    if (n >= 6 and
                            cols_since_shop >= diff['shop_interval'] and
                            random.random() < diff['shop_chance']):
                        temp = q.pop()
                        # Place shop tile at the middle of the flat segment
                        shop_col = i + n // 2 - 1
                        world[temp[1] - 1][shop_col] = SHOP
                        # Place shopkeeper 1 block to the right on same surface row
                        sk_col = shop_col + 1
                        if sk_col < len(world[0]):
                            world[temp[1] - 1][sk_col] = SHOPKEEPER
                        cols_since_shop = 0
                        shop_placed = True

                    if not shop_placed:
                        if n == 4 or n == 5:
                            if random.random() >= 0.5:
                                temp = q.pop()
                                world[temp[1] - 1][i] = CART
                                world[temp[1] - 1][i + 1] = WHEEL
                            elif random.random() <= 0.4:
                                temp = q.pop()
                                world[temp[1] - 1][i + 1] = LOGS
                        elif n == 3:
                            if random.random() >= 0.2:
                                temp = q.pop()
                                world[temp[1] - 1][i] = BUSH_MEDIUM
                        elif n == 2:
                            if random.random() >= 0.4:
                                temp = q.pop()
                                if random.choice([BUSH_SMALL, FLOWER_3]) == BUSH_SMALL:
                                    world[temp[1] - 1][i] = BUSH_SMALL
                                else:
                                    world[temp[1] - 1][i + 1] = FLOWER_3
                            else:
                                temp = q.pop()
                                world[temp[1] - 1][i] = POLE
                                world[temp[1] - 1][i + 1] = LAMP
                        elif 6 <= n < 8:
                            if random.random() >= 0.2:
                                temp = q.pop()
                                world[temp[1] - 1][i + 1] = random.choice([BOX, OBSTACLE])
                                world[temp[1] - 1][i + 2] = WELL
                                world[temp[1] - 1][i + 4] = random.choice([BOX, OBSTACLE])
                        elif n >= 8:
                            if random.random() >= 0.3:
                                temp = q.pop()
                                if temp[1] >= 5:
                                    world[temp[1] - 1][i + 1] = random.choice([GROUND, SURFACE])
                                    world[temp[1] - 1][i + 2] = random.choice([GROUND, SURFACE])
                                    world[temp[1] - 2][i + 2] = random.choice([GROUND, SURFACE])
                                    world[temp[1] - 1][i + 3] = random.choice([GROUND, SURFACE])
                                    world[temp[1] - 2][i + 3] = random.choice([GROUND, SURFACE])
                                world[temp[1] - 3][i + 3] = random.choice([GROUND, SURFACE])
                                world[temp[1] - 3][i + 4] = random.choice([GROUND, SURFACE])
                                world[temp[1] - 4][i + 4] = FLOWER
                                world[temp[1] - 3][i + 5] = random.choice([GROUND, SURFACE])

                    q.clear()
                    cols_since_shop += (j - i)
                    i = j - 1
                    break
        i += 1

    return world
