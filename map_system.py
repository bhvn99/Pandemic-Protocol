import os
import random
import pygame

# -----------------------------------------------------------------------------
# World data import (single source of truth)
# -----------------------------------------------------------------------------
# REGION_CONFIG + LAND_CONNECTIONS belong in region_data.py because they are
# “content/balancing data”, not algorithms. This keeps your simulation code stable
# even if you rebalance populations or borders later.

# The try statement is used to attempt operations that may fail and to handle predictable
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
        region_names: list[str],
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
        region_colours: dict[str, tuple[int, int, int, int]],
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
        airports_open: bool = True,
    ):
        self.name = name
        self.population = int(population)

        # Compartments are floats internally so small per-tick changes do not get lost to int() rounding.
        # The HUD can still render int(...) values for readability.
        self.susceptible = float(population)
        self.exposed = 0.0
        self.infected = 0.0
        self.recovered = 0.0
        self.dead = 0.0


        # Healthcare score 0..1 (higher = stronger system). Used later for resistance/cure.
        self.healthcare_score = max(0.0, min(1.0, float(healthcare_score)))

        # Airport flag used later for air travel spread.
        self.airports_open = bool(airports_open)

        # Visual colour is derived by Simulation.
        self.colour_rgba = (68, 111, 0, 255)

    def visual_severity_ratio(self):
        if self.population <= 0:
            return 0.0

        infected_ratio = self.infected / self.population
        dead_ratio = self.dead / self.population

        # Infections give early visual feedback; deaths dominate late-game severity.
        # Scaling infected_ratio avoids the map looking "stuck green" when infected is still a small share.
        v = (0.2 * min(1.0, infected_ratio * 3.0)) + (0.8 * (dead_ratio ** 3))

        if dead_ratio >= 0.96:
            t = (dead_ratio - 0.96) / 0.04  # 0 at 96% dead, 1 at 100% dead
            if t < 0.0:
                t = 0.0
            if t > 1.0:
                t = 1.0
            v = (v * (1.0 - t)) + (1.0 * t)

        if v < 0.0:
            v = 0.0
        if v > 1.0:
            v = 1.0

        return v

    def set_airports_open(self, is_open: bool):
        self.airports_open = bool(is_open)


def region_status_colour(ratio: float):
    """Map a 0..1 severity ratio to a clear game-style gradient.

    Intent:
    - Most of the game stays in green/yellow/red.
    - Dark red is reached at ~80%.
    - After 80%, fade into grey to signal a region is effectively dead.

    This is deliberately simple to tune.
    """

    # Clamp
    if ratio < 0.0:
        ratio = 0.0
    if ratio > 1.0:
        ratio = 1.0

    def lerp(a: int, b: int, t: float) -> int:
        return int(a + (b - a) * t)

    # Key colours (RGBA)
    green = (0, 120, 0, 255)
    yellow = (255, 210, 0, 255)
    red = (220, 0, 0, 255)
    dark_red = (120, 0, 0, 255)
    death_grey = (40, 40, 40, 255)

    # Front-loaded thresholds (earlier visual feedback):
    # 0.00 -> 0.12 : green -> yellow
    if ratio < 0.12:
        t = ratio / 0.12
        return (
            lerp(green[0], yellow[0], t),
            lerp(green[1], yellow[1], t),
            lerp(green[2], yellow[2], t),
            255,
        )

    # 0.12 -> 0.40 : yellow -> red
    if ratio < 0.40:
        t = (ratio - 0.12) / 0.28
        return (
            lerp(yellow[0], red[0], t),
            lerp(yellow[1], red[1], t),
            lerp(yellow[2], red[2], t),
            255,
        )

    # 0.40 -> 0.70 : red -> dark red
    if ratio < 0.70:
        t = (ratio - 0.40) / 0.30
        return (
            lerp(red[0], dark_red[0], t),
            lerp(red[1], dark_red[1], t),
            lerp(red[2], dark_red[2], t),
            255,
        )

    # 0.70 -> 1.00 : dark red -> death grey
    t = (ratio - 0.70) / 0.30
    return (
        lerp(dark_red[0], death_grey[0], t),
        lerp(dark_red[1], death_grey[1], t),
        lerp(dark_red[2], death_grey[2], t),
        255,
    )


class Simulation:
    """
    Simulation scaffold.

    What it does now:
    - tracks time as ticks
    - keeps region colours consistent with current visual severity (infections + weighted deaths)
    - advances per-region SEIRD state once per in-game day (update_one_day)

    What it does NOT do yet:
    - no air travel spread yet
    - no cure effort system yet
    """

    def __init__(self, regions: dict[str, Region]):
        self.regions = regions
        self.sim_time_ticks = 0

        # These counters let the same update method support either:
        # - daily updates (called once per day)
        # - smooth updates (called multiple times per day)
        self.day_count = 0
        self._tick_in_day = 0
        self._assumed_ticks_per_day = 20

        # Export cooldown (region -> last day it successfully exported).
        self.last_export_day: dict[str, int] = {}

    def land_neighbours(self, region_name: str) -> list[str]:
        # Kept ready for later land spread.
        return LAND_CONNECTIONS.get(region_name, [])

    def update_one_tick(self):
        self.sim_time_ticks += 1

    def update_one_day(
        self,
        infectivity_rate,
        severity_rate,
        lethality_rate,
        incubation_days,
        immunity_decay_rate=0.01,
        min_pressure=0.03,
        export_base_chance=0.04,
        export_cooldown_days=8,
        export_seed_base=25,
    ):
        if incubation_days <= 0:
            incubation_days = 1

        # Auto-detect whether the caller is passing per-tick rates (small) or per-day rates (large).
        # If you divide your rates in main.py to get smoother motion, this keeps behaviour consistent.
        # Detect smoothing mode based on infectivity/severity only.
        # Lethality is a fraction of resolving cases, so it should NOT affect tick/day detection.
        per_tick_mode = (infectivity_rate < 0.5 and severity_rate < 0.5)

        ticks_per_day = self._assumed_ticks_per_day if per_tick_mode else 1
        day_fraction = 1.0 / ticks_per_day

        # Advance time. Only bump day_count when a full day has elapsed.
        if per_tick_mode:
            self._tick_in_day += 1
            if self._tick_in_day >= ticks_per_day:
                self._tick_in_day = 0
                self.day_count += 1
        else:
            self.day_count += 1

        day_boundary = (not per_tick_mode) or (self._tick_in_day == 0)

        # Global activity check: keeps the disease “alive” while there are still cases anywhere.
        # This prevents the simulation stalling because pressure collapses to ~0 late-game.
        global_active = 0.0
        for rgn in self.regions.values():
            global_active += (rgn.exposed + rgn.infected)
        disease_exists = global_active > 0.0

        for region in self.regions.values():
            pop = region.population
            if pop <= 0:
                continue

            s = region.susceptible
            e = region.exposed
            i = region.infected
            r = region.recovered

            # Mild healthcare effect (kept intentionally small for now; easy to tune later).
            spread_scale = 1.0 - (0.25 * region.healthcare_score)
            death_scale = 1.0 - (0.25 * region.healthcare_score)
            eff_infectivity = infectivity_rate * spread_scale
            eff_lethality = lethality_rate * death_scale

            pressure = 0.0
            if pop > 0:
                pressure = i / pop

            # Persistence floor (eradication still possible):
            # - Only applies while disease exists somewhere globally.
            # - Only applies to regions that already have local cases (E or I), so it does not
            #   “spawn” infection in clean regions.
            if disease_exists and (i > 0.0 or e > 0.0) and pressure < min_pressure:
                pressure = min_pressure

            # S -> E
            new_e = s * eff_infectivity * pressure
            if new_e > s:
                new_e = s
            if new_e < 0.0:
                new_e = 0.0

            # E -> I (incubation)
            new_i = e / (incubation_days * ticks_per_day)
            if new_i > e:
                new_i = e
            if new_i < 0.0:
                new_i = 0.0

            # I -> resolved (R or D)
            resolving = i * severity_rate
            if resolving > i:
                resolving = i
            if resolving < 0.0:
                resolving = 0.0

            # resolved -> deaths
            new_d = resolving * eff_lethality
            if new_d > resolving:
                new_d = resolving
            if new_d < 0.0:
                new_d = 0.0

            new_r = resolving - new_d

            # Immunity decay (R -> S). Default is 0.01 unless overridden by caller.
            # Treat immunity_decay_rate as "per day" and scale it down when updating multiple times per day.
            lost_immunity = r * (immunity_decay_rate * day_fraction)
            if lost_immunity > r:
                lost_immunity = r
            if lost_immunity < 0.0:
                lost_immunity = 0.0

            region.susceptible = (s - new_e) + lost_immunity
            region.exposed = e + new_e - new_i
            region.infected = i + new_i - resolving


            region.recovered = (r + new_r) - lost_immunity
            region.dead += new_d

            # Guard against tiny negative drift from float ops.
            if region.susceptible < 0.0:
                region.susceptible = 0.0
            if region.exposed < 0.0:
                region.exposed = 0.0
            if region.infected < 0.0:
                region.infected = 0.0
            if region.recovered < 0.0:
                region.recovered = 0.0

        # Land transmission (event-based): occasional export attempts that seed Exposed.
        # Run exports once per simulated day, even if disease dynamics are updated multiple times per day.
        if day_boundary:
            for src_name, src in self.regions.items():
                # Allow exports during incubation so spread doesn't feel "stuck".
                if (src.exposed + src.infected) <= 0.0:
                    continue

                neighbours = self.land_neighbours(src_name)
                if not neighbours:
                    continue

                last = self.last_export_day.get(src_name, -10_000)
                if (self.day_count - last) < export_cooldown_days:
                    continue

                # Threshold-triggered exports (Plague Inc pacing):
                # A region only starts exporting once it has a meaningful outbreak.
                active = (src.exposed + src.infected)

                # Daily-scale infectivity keeps exports consistent when main.py smooths rates.
                daily_infectivity = infectivity_rate * ticks_per_day

                # Base chance is set by outbreak size; infectivity then scales it.
                # Bands are tuned for gradual "country-by-country" spread.
                if active < 2000.0:
                    continue
                elif active < 20000.0:
                    base = 0.01
                elif active < 100000.0:
                    base = 0.03
                else:
                    base = 0.06

                chance = base * daily_infectivity
                if chance > 0.18:
                    chance = 0.18

                if random.random() >= chance:
                    continue

                dst_name = random.choice(neighbours)
                dst = self.regions.get(dst_name)
                if dst is None or dst.susceptible <= 0.0:
                    continue

                # Seed a small Exposed foothold so the neighbour ramps up after incubation.
                seed = export_seed_base * daily_infectivity
                if seed < 1.0:
                    seed = 1.0
                if seed > 250.0:
                    seed = 250.0

                if seed > dst.susceptible:
                    seed = dst.susceptible

                dst.susceptible -= seed
                dst.exposed += seed

                if dst.susceptible < 0.0:
                    dst.susceptible = 0.0

                self.last_export_day[src_name] = self.day_count

        for region in self.regions.values():
            region.colour_rgba = region_status_colour(region.visual_severity_ratio())


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