"""
Assemble complete house sprites from the Houses_Pack spritesheet.
Finds individual sprite pieces and composes them into complete front-view houses.
"""
import pygame
import os

pygame.init()
screen = pygame.display.set_mode((100, 100))

sheet = pygame.image.load(os.path.join(os.path.dirname(__file__), "houses.png")).convert_alpha()
SW, SH = sheet.get_size()


def extract(x, y, w, h):
    """Extract a region from the spritesheet."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.blit(sheet, (0, 0), (x, y, w, h))
    return surf


def content_bounds(surface):
    """Find the non-transparent bounding box of a surface."""
    w, h = surface.get_size()
    min_x, min_y, max_x, max_y = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            if surface.get_at((x, y))[3] > 10:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if max_x < min_x:
        return 0, 0, w, h
    return min_x, min_y, max_x - min_x + 1, max_y - min_y + 1


def crop(surface):
    """Crop surface to non-transparent content."""
    bx, by, bw, bh = content_bounds(surface)
    cropped = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cropped.blit(surface, (0, 0), (bx, by, bw, bh))
    return cropped


def find_sprites_in_region(rx, ry, rw, rh, min_area=500):
    """Find individual sprite bounding boxes by scanning for transparent column gaps."""
    # Find non-empty column spans
    col_has_content = []
    for x in range(rx, rx + rw):
        has = False
        for y in range(ry, ry + rh):
            if sheet.get_at((x, y))[3] > 10:
                has = True
                break
        col_has_content.append(has)

    # Group consecutive content columns into spans
    spans = []
    in_span = False
    for i, has in enumerate(col_has_content):
        if has and not in_span:
            span_start = i
            in_span = True
        elif not has and in_span:
            spans.append((rx + span_start, rx + i))
            in_span = False
    if in_span:
        spans.append((rx + span_start, rx + len(col_has_content)))

    # For each span, find vertical bounds and tighten horizontal
    sprites = []
    for cx_s, cx_e in spans:
        piece = extract(cx_s, ry, cx_e - cx_s, rh)
        bx, by, bw, bh = content_bounds(piece)
        if bw * bh >= min_area:
            sprites.append((cx_s + bx, ry + by, bw, bh))

    sprites.sort(key=lambda s: s[2] * s[3], reverse=True)
    return sprites


# Row boundaries from visual analysis of the 1024x1024 sheet
row_bounds = [0, 75, 335, 555, 655, 815, 1024]
col_width = SW // 3
color_names = ["purple", "gray", "red"]
output_dir = os.path.dirname(__file__)

for col_idx, color in enumerate(color_names):
    cx = col_idx * col_width

    print(f"\n=== {color.upper()} ===")

    # Find pieces in each row section
    ridge_pieces = find_sprites_in_region(cx, 0, col_width, 75)
    gable_pieces = find_sprites_in_region(cx, 335, col_width, 220)
    upper_pieces = find_sprites_in_region(cx, 555, col_width, 100)
    lower_pieces = find_sprites_in_region(cx, 655, col_width, 160)
    found_pieces = find_sprites_in_region(cx, 815, col_width, 209)

    # Main pieces (largest in each section)
    ridge = gable = upper = lower = foundation = None

    if ridge_pieces:
        ridge = extract(*ridge_pieces[0])
        print(f"  Ridge: {ridge_pieces[0]}")
    if gable_pieces:
        # The gable piece may contain a dormer (top) and main roof (bottom)
        # with transparent space between them. We keep it as-is since
        # overlapping with the upper section will fill the gap.
        gable = extract(*gable_pieces[0])
        print(f"  Gable: {gable_pieces[0]}")
    if upper_pieces:
        upper = extract(*upper_pieces[0])
        print(f"  Upper: {upper_pieces[0]}")
    if lower_pieces:
        lower = extract(*lower_pieces[0])
        print(f"  Lower: {lower_pieces[0]}")
    if found_pieces:
        foundation = extract(*found_pieces[0])
        print(f"  Foundation: {found_pieces[0]}")

    # Get side wall pieces from the gable row (chimney stacks, side panels)
    side_pieces_gable = gable_pieces[1:] if len(gable_pieces) > 1 else []
    side_pieces_upper = upper_pieces[1:] if len(upper_pieces) > 1 else []

    # ---- ASSEMBLE FRONT-VIEW HOUSE ----
    # Strategy: overlay the pieces so they connect properly.
    # The gable's bottom overlaps slightly with the upper's top.
    # The upper's bottom overlaps slightly with the lower's top.

    gable_w, gable_h = gable.get_size()
    upper_w, upper_h = upper.get_size()
    lower_w, lower_h = lower.get_size()

    # Find where content actually ends/starts vertically in each piece
    # to determine proper overlap
    def bottom_content_y(surf):
        """Y position of the lowest non-transparent pixel."""
        w, h = surf.get_size()
        for y in range(h - 1, -1, -1):
            for x in range(w):
                if surf.get_at((x, y))[3] > 10:
                    return y
        return h - 1

    def top_content_y(surf):
        """Y position of the highest non-transparent pixel."""
        w, h = surf.get_size()
        for y in range(h):
            for x in range(w):
                if surf.get_at((x, y))[3] > 10:
                    return y
        return 0

    # The gable piece has internal transparency between dormer and main roof.
    # We need to find the sub-pieces within the gable.
    # Split gable into horizontal bands by finding transparent rows.
    def split_vertical(surf, min_height=10):
        """Split a surface into vertical sub-pieces separated by fully transparent rows."""
        w, h = surf.get_size()
        bands = []
        in_band = False
        band_start = 0
        for y in range(h):
            has_content = False
            for x in range(w):
                if surf.get_at((x, y))[3] > 10:
                    has_content = True
                    break
            if has_content and not in_band:
                band_start = y
                in_band = True
            elif not has_content and in_band:
                if y - band_start >= min_height:
                    bands.append((band_start, y))
                in_band = False
        if in_band and h - band_start >= min_height:
            bands.append((band_start, h))
        return bands

    gable_bands = split_vertical(gable, min_height=15)
    print(f"  Gable bands: {gable_bands}")

    if len(gable_bands) >= 2:
        # Dormer (top band) and main roof (bottom band)
        dormer_y_start, dormer_y_end = gable_bands[0]
        roof_y_start, roof_y_end = gable_bands[-1]

        dormer_surf = pygame.Surface((gable_w, dormer_y_end - dormer_y_start), pygame.SRCALPHA)
        dormer_surf.blit(gable, (0, 0), (0, dormer_y_start, gable_w, dormer_y_end - dormer_y_start))

        roof_surf = pygame.Surface((gable_w, roof_y_end - roof_y_start), pygame.SRCALPHA)
        roof_surf.blit(gable, (0, 0), (0, roof_y_start, gable_w, roof_y_end - roof_y_start))

        # Now assemble: dormer overlaps onto top of main roof
        # The dormer's bottom should overlap with the main roof's top by ~20px
        # The dormer (81px) and roof (117px) had a 22px gap in the spritesheet.
        # Stacking them removes the gap; overlap makes them connect visually.
        overlap_dormer_roof = 38
        overlap_roof_upper = 5
        overlap_upper_lower = 5

        dormer_w, dormer_h = dormer_surf.get_size()
        roof_w, roof_h = roof_surf.get_size()

        # Total dimensions
        total_w = max(dormer_w, roof_w, upper_w, lower_w)
        total_h = (dormer_h + roof_h - overlap_dormer_roof +
                   upper_h - overlap_roof_upper +
                   lower_h - overlap_upper_lower)

        house = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

        y = 0
        # Dormer
        dx = (total_w - dormer_w) // 2
        house.blit(dormer_surf, (dx, y))
        y += dormer_h - overlap_dormer_roof

        # Main roof
        rx = (total_w - roof_w) // 2
        house.blit(roof_surf, (rx, y))
        y += roof_h - overlap_roof_upper

        # Upper facade
        ux = (total_w - upper_w) // 2
        house.blit(upper, (ux, y))
        y += upper_h - overlap_upper_lower

        # Lower facade
        lx = (total_w - lower_w) // 2
        house.blit(lower, (lx, y))

    else:
        # Gable is a single piece, just stack
        total_w = max(gable_w, upper_w, lower_w)
        total_h = gable_h + upper_h + lower_h
        house = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        house.blit(gable, ((total_w - gable_w) // 2, 0))
        house.blit(upper, ((total_w - upper_w) // 2, gable_h))
        house.blit(lower, ((total_w - lower_w) // 2, gable_h + upper_h))

    out_path = os.path.join(output_dir, f"house_{color}.png")
    pygame.image.save(house, out_path)
    hw, hh = house.get_size()
    print(f"  -> Saved house_{color}.png ({hw}x{hh})")

    # ---- WIDE VERSION with side walls ----
    if len(side_pieces_gable) >= 2:
        side_pieces_gable.sort(key=lambda s: s[0])  # sort by x position
        left_sp = side_pieces_gable[0]
        right_sp = side_pieces_gable[-1]
        left_wall = crop(extract(*left_sp))
        right_wall = crop(extract(*right_sp))

        # Also grab side pieces from upper row if available
        left_upper = right_upper = None
        if len(side_pieces_upper) >= 2:
            side_pieces_upper.sort(key=lambda s: s[0])
            left_upper = crop(extract(*side_pieces_upper[0]))
            right_upper = crop(extract(*side_pieces_upper[-1]))

        lw_w = left_wall.get_width()
        rw_w = right_wall.get_width()
        ext_w = lw_w + hw + rw_w + 4  # small padding

        ext_house = pygame.Surface((ext_w, hh), pygame.SRCALPHA)

        # Main house in center
        ext_house.blit(house, (lw_w + 2, 0))

        # Side walls - position vertically to align with the wall sections
        # They should align with where the upper facade starts
        if len(gable_bands) >= 2:
            wall_y = gable_bands[0][1] - gable_bands[0][0] - 20 + gable_bands[-1][1] - gable_bands[-1][0] - 2
        else:
            wall_y = gable_h

        left_wall_h = left_wall.get_height()
        ext_house.blit(left_wall, (0, wall_y))
        ext_house.blit(right_wall, (lw_w + 2 + hw + 2, wall_y))

        # Side upper pieces below the side walls
        if left_upper and right_upper:
            ext_house.blit(left_upper, (0, wall_y + left_wall_h))
            ext_house.blit(right_upper, (lw_w + 2 + hw + 2, wall_y + left_wall_h))

        ext_house = crop(ext_house)
        out_path = os.path.join(output_dir, f"house_{color}_wide.png")
        pygame.image.save(ext_house, out_path)
        ew, eh = ext_house.get_size()
        print(f"  -> Saved house_{color}_wide.png ({ew}x{eh})")

    # ---- FULL VERSION with ridge cap ----
    if ridge:
        ridge_w, ridge_h = ridge.get_size()
        full_w = max(hw, ridge_w)
        full_h = ridge_h + hh - 25  # ridge overlaps with house top dormer
        full_house = pygame.Surface((full_w, full_h), pygame.SRCALPHA)
        full_house.blit(ridge, ((full_w - ridge_w) // 2, 0))
        full_house.blit(house, ((full_w - hw) // 2, ridge_h - 25))
        full_house = crop(full_house)
        out_path = os.path.join(output_dir, f"house_{color}_full.png")
        pygame.image.save(full_house, out_path)
        fw, fh = full_house.get_size()
        print(f"  -> Saved house_{color}_full.png ({fw}x{fh})")

print("\nDone! Assembled houses saved to Houses_Pack/")
pygame.quit()
