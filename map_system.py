import os
import pygame

# -----------------------------------------------------------------------------
# World data import (single source of truth)
# -----------------------------------------------------------------------------
# REGION_CONFIG + LAND_CONNECTIONS belong in region_data.py because they are
# “content/balancing data”, not algorithms. This keeps your simulation code stable
# even if you rebalance populations or borders later.

#The try statement is used to attempt operations that may fail and to handle predictable
# errors gracefully, preventing the program from crashing while providing meaningful feedback.
try:
    from region_data import REGION_CONFIG, LAND_CONNECTIONS, REGION_ID_HEX
except ImportError as e:
    raise ImportError(
        "Could not import REGION_CONFIG / LAND_CONNECTIONS from region_data.py. "
        "Ensure region_data.py is in the same folder as main.py and map_system.py."
    ) from e

def hex_to_rgba(hex_rgba: str):
    if len(hex_rgba) != 8:
        raise ValueError(f"Expected 8-char hex RGBA, got: '{hex_rgba}'")

    r = int(hex_rgba[0:2], 16)
    g = int(hex_rgba[2:4], 16)
    b = int(hex_rgba[4:6], 16)
    a = int(hex_rgba[6:8], 16)
    return (r, g, b, a)


class MapRenderer:
    """
    Draws the world map.

    It only renders:
    - base map image
    - per-region mask overlays tinted to colours you provide

    It does NOT run disease logic. That stays in Simulation.
    """

    def __init__(
            self,
            assets_dir: str,
            map_size: tuple[int, int],
            region_names: list[str]
    ):
        

        self.assets_dir = assets_dir
        self.map_size = map_size

        self.maps_dir = os.path.join(self.assets_dir, "maps")
        self.masks_dir = os.path.join(self.maps_dir, "masks")

        # Base map is static (ocean + default land look). Drawn first each frame.
        self.base_map = self._load_image(os.path.join(self.maps_dir, "map_base.png"))

        # ID map is a colour-coded reference image used for click detection.
        # It is never displayed to the player.
        #
        # Requirement:
        # - assets/maps/map_id.png must be the same size as map_base.png
        self.id_map = self._load_image(os.path.join(self.maps_dir, "map_id.png"))

        # Reverse lookup: (r, g, b) -> region key
        # Alpha is ignored because some exports can introduce minor alpha variation.
        self._id_lookup = {}
        for region_key, hex_rgba in REGION_ID_HEX.items():
            r, g, b, _a = hex_to_rgba(hex_rgba)
            self._id_lookup[(r, g, b)] = region_key

        # Masks define each region’s shape (white on transparent).
        # File naming is hard-coded by convention: <region>_mask.png
        self.region_names = region_names
        self.region_masks: dict[str, pygame.Surface] = {}

        for region in self.region_names:
            mask_path = os.path.join(self.masks_dir, f"{region}_mask.png")
            if not os.path.exists(mask_path):
                raise FileNotFoundError(
                    f"Missing mask for region '{region}': {mask_path}\n"
                    f"Expected filename: {region}_mask.png"
                )
            self.region_masks[region] = self._load_image(mask_path)

        # Tint cache avoids re-tinting surfaces every frame (performance).
        self._tint_cache: dict[tuple[str, tuple[int, int, int, int]], pygame.Surface] = {}

    def draw(
            self,
            screen: pygame.Surface,
            region_colours: dict[str, tuple[int, int, int, int]]
    ):
        
        # Draw base first.
        screen.blit(self.base_map, (0, 0))

        # Then overlay tinted masks.
        for region in self.region_names:
            # Hard-coded default land green:
            # This matches your exported base map land colour so regions don’t flicker
            # if the simulation hasn’t assigned a colour yet.
            rgba = region_colours.get(region, (68, 111, 0, 255))
            overlay = self._get_tinted_overlay(region, rgba)
            screen.blit(overlay, (0, 0))

    def get_region_at(self, screen_pos: tuple[int, int]):
        """Return the region key at screen_pos using the ID map; None if ocean/unknown."""

        x, y = screen_pos

        # Outside the map surface -> treat as no region selected (global view).
        if x < 0 or y < 0 or x >= self.map_size[0] or y >= self.map_size[1]:
            return None

        r, g, b, _a = self.id_map.get_at((x, y))
        return self._id_lookup.get((r, g, b))

    def _load_image(self, path: str):
        image = pygame.image.load(path).convert_alpha()
        if image.get_size() != self.map_size:
            image = pygame.transform.smoothscale(image, self.map_size)
        return image

    def _get_tinted_overlay(self, region: str, rgba: tuple[int, int, int, int]):
        key = (region, rgba)
        if key in self._tint_cache:
            return self._tint_cache[key]

        tinted = self.region_masks[region].copy()
        tinted.fill(rgba, special_flags=pygame.BLEND_RGBA_MULT)
        self._tint_cache[key] = tinted
        return tinted


class Region:
    def __init__(
            self,
            name: str,
            population: int,
            healthcare_score: float,
            airports_open: bool = True
    ):
     
        self.name = name
        self.population = int(population)

        # SIRD counts (kept ready for later model decisions).
        self.susceptible = int(population)
        self.infected = 0
        self.recovered = 0
        self.dead = 0

        # Healthcare score 0..1 (higher = stronger system). Used later for resistance/cure.
        self.healthcare_score = max(0.0, min(1.0, float(healthcare_score)))

        # Airport flag used later for air travel spread.
        self.airports_open = bool(airports_open)

        # Visual colour is derived by Simulation.
        self.colour_rgba = (68, 111, 0, 255)

    def infection_ratio(self):
        if self.population <= 0:
            return 0.0
        return self.infected / self.population

    def set_airports_open(self, is_open: bool):
        self.airports_open = bool(is_open)


def colour_from_infection_ratio(ratio: float):
    """
    Converts infection ratio (0..1) into a colour gradient.

    Hard-coded thresholds (0.33 / 0.66):
    - gives three clear bands while still allowing smooth transitions
    - easy to tune later if pacing feels wrong
    """
    ratio = max(0.0, min(1.0, ratio))

    # Green -> Yellow
    if ratio <= 0.33:
        t = ratio / 0.33
        r = int(255 * t)
        g = int(160 + (95 * t))
        return (r, g, 0, 255)

    # Yellow -> Red
    if ratio <= 0.66:
        t = (ratio - 0.33) / 0.33
        g = int(255 - (255 * t))
        return (255, g, 0, 255)

    # Red -> Dark Red
    t = (ratio - 0.66) / 0.34
    r = int(255 - (135 * t))
    return (r, 0, 0, 255)


class Simulation:
    """
    Simulation scaffold.

    What it does now:
    - tracks time as ticks
    - keeps region colours consistent with current infection ratio

    What it does NOT do yet:
    - no disease spread logic
    - no SIRD update rules
    - no land/air spread (we design those properly next)
    """

    def __init__(self, regions: dict[str, Region]):
        self.regions = regions
        self.sim_time_days = 0

    def land_neighbours(self, region_name: str) -> list[str]:
        # Kept ready for later land spread.
        return LAND_CONNECTIONS.get(region_name, [])

    def update_one_tick(self):
        self.sim_time_days += 1

        # For now: ONLY visual sync (so your map system is stable while we design rules).
        for region in self.regions.values():
            region.colour_rgba = colour_from_infection_ratio(region.infection_ratio())


def build_regions_from_config() -> dict[str, Region]:
    """
    Builds Region objects using REGION_CONFIG.

    Hard requirement:
    - REGION_CONFIG keys must match mask filenames
      e.g. "china" -> assets/maps/masks/china_mask.png
    """
    regions: dict[str, Region] = {}
    for name, cfg in REGION_CONFIG.items():
        regions[name] = Region(
            name=name,
            population=cfg["population"],
            healthcare_score=cfg["healthcare_score"],
            airports_open=cfg["airports_open"],
        )
    return regions