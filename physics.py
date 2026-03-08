def apply_gravity(entity, max_vel=10):
    entity.vel_y += 1
    if entity.vel_y > max_vel:
        entity.vel_y = max_vel
    entity.dy += entity.vel_y


def check_tile_collisions(entity, tile_list):
    entity.in_air = True
    for tile in tile_list:
        if not tile[2]:
            continue

        # x direction
        if tile[1].colliderect(
            entity.rect.x + entity.dx, entity.rect.y,
            entity.width, entity.height
        ):
            entity.dx = 0

        # y direction
        if tile[1].colliderect(
            entity.rect.x, entity.rect.y + entity.dy,
            entity.width, entity.height
        ):
            if entity.vel_y < 0:
                entity.dy = tile[1].bottom - entity.rect.top
                entity.vel_y = 0
            elif entity.vel_y >= 0:
                entity.dy = tile[1].top - entity.rect.bottom
                entity.vel_y = 0
                entity.in_air = False
                if hasattr(entity, 'jumped'):
                    entity.jumped = False
