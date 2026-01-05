import pygame, sys, hashlib, os, json

# Global setup (window, fonts, colours)
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pandemic Protocol")
font = pygame.font.Font(None, 36)
font2big = pygame.font.Font("assets/BR.ttf", 75)
font2 = pygame.font.Font("assets/BR.ttf", 40)
BLACK = (0, 0, 0)

# Hashed credentials (could later come from a file/database)
USERNAME = "user123"
HASH_PASSWORD = hashlib.sha256("pass123".encode()).hexdigest()

def login_screen():
    # Displays login UI and handles user input until valid credentials are entered
    text_user, text_pass = "", ""
    active_user = True
    message = ""

    user_box = pygame.Rect(200, 350, 200, 40)
    pass_box = pygame.Rect(200, 410, 200, 40)

    background = pygame.image.load("assets/background.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    while True:
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if user_box.collidepoint(event.pos):
                    active_user = True
                elif pass_box.collidepoint(event.pos):
                    active_user = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if active_user:
                        text_user = text_user[:-1]
                    else:
                        text_pass = text_pass[:-1]

                elif event.key == pygame.K_RETURN:
                    hashed_input = hashlib.sha256(text_pass.encode()).hexdigest()
                    if text_user == USERNAME and hashed_input == HASH_PASSWORD:
                        return True
                    else:
                        message = "Login Failed!"

                else:
                    if active_user:
                        text_user += event.unicode
                    else:
                        text_pass += event.unicode

        pygame.draw.rect(screen, (0, 0, 0), user_box, 2)
        pygame.draw.rect(screen, (0, 0, 0), pass_box, 2)

        screen.blit(font.render(text_user, True, (0, 0, 0)), (user_box.x + 5, user_box.y + 5))
        screen.blit(font.render("*" * len(text_pass), True, (0, 0, 0)), (pass_box.x + 5, pass_box.y + 5))

        screen.blit(font.render("Username:", True, (0, 0, 0)), (50, 355))
        screen.blit(font.render("Password:", True, (0, 0, 0)), (50, 415))
        screen.blit(font2big.render("Pandemic Protocol", True, (0, 0, 0)), (55, 100))

        if message:
            screen.blit(font.render(message, True, (255, 0, 0)), (100, 220))

        pygame.display.flip()

def Play():

    def difficultyselect():
        background3 = pygame.image.load("assets/background3.png")
        background3 = pygame.transform.scale(background3, (WIDTH, HEIGHT))
        # Default to None so the function always returns a valid value (prevents UnboundLocalError on ESC).
        difficulty = None

        # Rectangle settings
        rect_width = 250
        rect_height = 300
        spacing = 50
        total_width = 3 * rect_width + 2 * spacing
        start_x = (WIDTH - total_width) // 2
        y_pos = HEIGHT // 3

        difficulties = [
        {"name": "Easy", "color": (0, 200, 0), "desc": "Arcade: No cure effort"},
        {"name": "Medium", "color": (255, 165, 0), "desc": "Normal"},
        {"name": "Hard", "color": (200, 0, 0), "desc": "Hardcore"}
        ]

        for i, diff in enumerate(difficulties):
            x = start_x + i * (rect_width + spacing)
            diff["rect"] = pygame.Rect(x, y_pos, rect_width, rect_height)

        running = True
        while running:
            screen.blit(background3, (0, 0))   
            text = font2big.render("Select Difficulty", True, (255, 255, 255))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 20))
            for diff in difficulties:
                pygame.draw.rect(screen, diff["color"], diff["rect"])
                name_text = font2.render(diff["name"], True, (255, 255, 255))
                screen.blit(name_text, (diff["rect"].centerx - name_text.get_width()//2,
                                    diff["rect"].centery - name_text.get_height()//2))
                desc_text = font.render(diff["desc"], True, (255, 255, 255))
                screen.blit(desc_text, (diff["rect"].centerx - desc_text.get_width()//2,
                                    diff["rect"].bottom + 10))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    difficulty = None
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for diff in difficulties:
                        if diff["rect"].collidepoint(mouse_pos):
                            print(f"{diff['name']} selected")
                            if diff['name'] == "Easy":
                                difficulty = "easy"
                                running = False
                            elif diff['name'] == "Medium":
                                difficulty = "medium"
                                running = False
                            elif diff['name'] == "Hard":
                                difficulty = "hard"
                                running = False
        return difficulty
    
    def diseasesetup():
        background4 = pygame.image.load("assets/background4.png")
        background4 = pygame.transform.scale(background4, (WIDTH, HEIGHT)) 

        dnamebox = pygame.Rect(0, 0, 400, 40)
        dnamebox.center = (WIDTH // 2, HEIGHT // 2)
        color_inactive = (150, 150, 150)
        color_active = (255, 255, 255)
        color = color_inactive
        active = False
        text_input = ""

        difficulty_presets = {
            "easy": {
                "infected": 1000,          # fast visible start (useful for testing)
                "infectivity_rate": 3,  # fast spread
                "severity_rate": 0.5,    # resolves quickly (more turnover)
                "lethality_rate": 0.5    # visible deaths without instant wipe
            },
            "medium": {
                "infected": 300,
                "infectivity_rate": 1.4,
                "severity_rate": 0.12,
                "lethality_rate": 0.08
            },
            "hard": {
                "infected": 100,
                "infectivity_rate": 0.95,
                "severity_rate": 0.08,
                "lethality_rate": 0.05
            }
        }

        running = True
        while running:
            screen.blit(background4, (0, 0))   
            text = font2big.render("Name Your Disease", True, (255, 255, 255))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 20))

            pygame.draw.rect(screen, color, dnamebox, 2)
            text_surface = font.render(text_input, True, (255, 255, 255))
            screen.blit(text_surface, (dnamebox.x + 5, dnamebox.y + 5))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # If the user clicked inside the input box
                    if dnamebox.collidepoint(event.pos):
                        active = True
                        color = color_active
                    else:
                        active = False
                        color = color_inactive

                elif event.type == pygame.KEYDOWN and active:
                    if event.key == pygame.K_RETURN:
                        disease_name = text_input.strip()

                        if disease_name:  # only save if non-empty
                            save_folder = "SavedDiseases"
                            os.makedirs(save_folder, exist_ok=True) # ensures folder exists
                            safe_name = "".join(c for c in disease_name if c.isalnum() or c in (" ", "_", "-")).rstrip() # sanitises file name
                            file_path = os.path.join(save_folder, f"{safe_name}.json") # creates file in /diseases

                            preset = difficulty_presets[difficulty]

                            disease_data = {
                                "name": disease_name,
                                "difficulty": difficulty,
                                "initial_infected": preset["infected"],
                                "log_interval_days": 5,
                                "history": [],
                                "wiped_out_order": [],

                                # Disease stats (dynamic during game)
                                "infectivity_rate": preset["infectivity_rate"],
                                "severity_rate": preset["severity_rate"],
                                "lethality_rate": preset["lethality_rate"],
                                "incubation_days": 3,
                                "timestamp_created": 0
                            }

                            with open(file_path, "w") as f:
                                json.dump(disease_data, f, indent=4)

                            print(f"[+] Disease file created: {file_path}")
                            return file_path
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    elif len(text_input) < 20:  # character limit
                        text_input += event.unicode

        return None

    difficulty = difficultyselect()
    if difficulty:
        disease_file_path = diseasesetup()
        if disease_file_path:
            run_map_test(disease_file_path)

    return True

def H2P():
    background2 = pygame.image.load("assets/background2.png")
    background2 = pygame.transform.scale(background2, (WIDTH, HEIGHT))
    running = True



    h2ptext = [
    "Strategically evolve your disease to infect the entire world before a cure is developed.",
    "Use mutations to increase infectivity, severity, and lethality while adapting to global responses.",
    "",
    "Getting Started:",
    "1. Choose a difficulty level: Easy, Normal, or Hard.",
    "2. Select your disease name and the country to start your outbreak.",
    "",
    "Gameplay Basics:",
    "- Mutations: Unlock mutations to affect disease stats. Some require prerequisite mutations.",
    "- Spread: Disease spreads via land and air between connected regions.",
    "- Cure Effort: Track the cure progress and act to outpace it.",
    "- News Feed: Real-time updates guide your strategic decisions.",
    "",
    "Tips for Success:",
    "- Balance infectivity, severity, and lethality.",
    "- Unlock mutations that work with your current stats.",
    "- Focus on high population regions.",
    "",
    "- Review statistics and graphs after game completion.",
    "",
    "Press ESC to return to the main menu."
    ]

    while running:
        screen.blit(background2, (0, 0)) 
        text = font2.render("How To Play", True, (0, 0, 0))
        screen.blit(text, (8, 0))

        # Formatting loop 
        y_offset = 65
        for line in h2ptext:
            text_surface = font.render(line, True, BLACK)
            screen.blit(text_surface, (20, y_offset))
            y_offset += text_surface.get_height() + 5

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

def Achievements():
    # empty for now until variables are known

    running = True
    while running:
        screen.fill((220, 180, 180))  
        text = font2.render("Achievements", True, (0, 0, 0))
        screen.blit(text, (8, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

def main_menu():
    # Main navigation screen (Iteration 1 evidence). Used as the entry point for the game flow.
    background = pygame.image.load("assets/background1.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    buttons = {
        "Play": pygame.Rect(540, 300, 200, 60),
        "How to Play": pygame.Rect(540, 380, 200, 60),
        "Achievements": pygame.Rect(540, 460, 200, 60)
    }

    while True:
        screen.blit(background, (0, 0))
        title = font2.render("Pandemic Protocol", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for name, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        # These functions are implemented in later iterations.
                        if name == "Play":
                            Play()
                        elif name == "Achievements":
                            Achievements()
                        elif name == "How to Play":
                            H2P()

        for name, rect in buttons.items():
            pygame.draw.rect(screen, (0, 100, 200), rect)
            label = font.render(name, True, (255, 255, 255))
            screen.blit(
                label,
                (rect.centerx - label.get_width() // 2,
                 rect.centery - label.get_height() // 2)
            )

        pygame.display.flip()

def run_map_test(disease_file_path):
    from map_system import MapRenderer, Simulation, build_regions_from_config
    from region_data import REGION_CONFIG
    with open(disease_file_path, "r") as f:
        disease_data = json.load(f)

    infectivity_rate = disease_data["infectivity_rate"]
    severity_rate = disease_data["severity_rate"]
    lethality_rate = disease_data["lethality_rate"]
    incubation_days = disease_data.get("incubation_days", 3)
    initial_infected = disease_data.get("initial_infected", 1)
    difficulty_label = str(disease_data.get("difficulty", "")).upper()

    # Single source of truth: REGION_CONFIG keys must match <key>_mask.png
    region_names = list(REGION_CONFIG.keys())
    regions = build_regions_from_config()

    # Simulation scaffold: tick loop exists now; disease rules come next.
    simulation = Simulation(regions=regions)
    map_renderer = MapRenderer(
        assets_dir="assets",
        map_size=(WIDTH, HEIGHT),
        region_names=region_names
    )

    clock = pygame.time.Clock()

    selected_region = None
    start_region = None
    simulation_started = False

    start_message = ""
    start_message_timer = 0

    HUD_H = 90
    HUD_Y = HEIGHT - HUD_H
    PROGRESS_H = 16
    TICKS_PER_SECOND = 10
    TICK_INTERVAL = 1.0 / TICKS_PER_SECOND
    TICKS_PER_DAY = 20

    accumulator = 0.0
    tick_count = 0
    day_count = 0

    def handle_events():
        """Input handling. First land click selects the outbreak start and begins the tick clock."""
        nonlocal selected_region, start_region, simulation_started, start_message, start_message_timer

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_region = map_renderer.get_region_at(event.pos)
                selected_region = clicked_region

                if (not simulation_started) and (clicked_region is not None):
                    start_region = clicked_region
                    simulation_started = True

                    region_obj = regions[start_region]
                    seed = min(initial_infected, region_obj.susceptible)
                    region_obj.susceptible -= seed
                    region_obj.infected += seed

                    start_message = f"Outbreak starts in {start_region.replace('_',' ').title()}"
                    start_message_timer = 180
        return True

    def update_simulation(dt):
        """Tick pacing + day counter. Time only advances once a start region is chosen."""
        nonlocal accumulator, tick_count, day_count

        accumulator += dt

        if simulation_started:
            while accumulator >= TICK_INTERVAL:
                # simulation.update_one_tick()  # Removed as per instruction
                tick_count += 1

                # Run one small disease step every tick so stats/colours move smoothly.
                simulation.update_one_day(
                    infectivity_rate / TICKS_PER_DAY,
                    severity_rate / TICKS_PER_DAY,
                    lethality_rate,
                    incubation_days,
                )

                if tick_count % TICKS_PER_DAY == 0:
                    day_count += 1

                accumulator -= TICK_INTERVAL
        else:
            accumulator = 0.0

    def resolve_display_stats():
        """Returns the label + infected/dead/alive values for the HUD (region view or global totals)."""
        if selected_region is None:
            display_region = "Global"
            # Simulation uses floats internally; HUD uses ints for readability.
            display_infected = int(sum(r.infected for r in regions.values()))
            display_dead = int(sum(r.dead for r in regions.values()))
            display_population = int(
                sum((r.susceptible + r.exposed + r.infected + r.recovered) for r in regions.values())
            )
            return display_region, display_infected, display_dead, display_population

        r = regions[selected_region]
        display_region = selected_region.replace("_", " ").title()
        # Simulation uses floats internally; HUD uses ints for readability.
        display_infected = int(r.infected)
        display_dead = int(r.dead)
        display_population = int(r.susceptible + r.exposed + r.infected + r.recovered)
        return display_region, display_infected, display_dead, display_population

    def draw_frame(display_region, display_infected, display_dead, display_population):
        """Draws the map, prompts/messages, day box, and HUD. Layout remains hard-coded."""
        nonlocal start_message_timer

        region_colours = {name: r.colour_rgba for name, r in regions.items()}
        map_renderer.draw(screen, region_colours)

        # Start prompt (shown until the player chooses a start region)
        if not simulation_started:
            prompt = font.render("Select a country to start the outbreak", True, (255, 255, 255))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 580))

        # Start message (fades out)
        if start_message_timer > 0:
            alpha = int(255 * (start_message_timer / 180))
            surf = font.render(start_message, True, (255, 255, 255))
            surf.set_alpha(alpha)
            screen.blit(surf, (20, 20))
            start_message_timer -= 1

        # Day box
        pygame.draw.rect(screen, (40, 40, 40), (1080, 10, 190, 50))
        pygame.draw.rect(screen, (0, 0, 0), (1080, 10, 190, 50), 2)
        day_text = f"Day {day_count}" if simulation_started else "Day 0"
        screen.blit(font.render(day_text, True, (255, 255, 255)), (1090, 22))

        # Bottom HUD boxes
        mut_box = pygame.Rect(0, HUD_Y, 180, HUD_H)
        inf_box = pygame.Rect(180, HUD_Y, 240, HUD_H)
        region_box = pygame.Rect(420, HUD_Y, 360, HUD_H)
        pop_box = pygame.Rect(780, HUD_Y, 200, HUD_H)
        death_box = pygame.Rect(980, HUD_Y, 200, HUD_H)
        cure_box = pygame.Rect(1180, HUD_Y, 100, HUD_H)

        region_text_h = HUD_H - PROGRESS_H
        region_text_box = pygame.Rect(region_box.x, region_box.y, region_box.width, region_text_h)
        region_progress_box = pygame.Rect(region_box.x, region_box.y + region_text_h, region_box.width, PROGRESS_H)

        pygame.draw.rect(screen, (120, 40, 40), mut_box)
        pygame.draw.rect(screen, (80, 80, 80), inf_box)
        pygame.draw.rect(screen, (80, 80, 80), region_text_box)
        pygame.draw.rect(screen, (40, 40, 40), region_progress_box)
        pygame.draw.rect(screen, (80, 80, 80), pop_box)
        pygame.draw.rect(screen, (80, 80, 80), death_box)
        pygame.draw.rect(screen, (40, 120, 160), cure_box)

        for box in (mut_box, inf_box, region_box, pop_box, death_box, cure_box):
            pygame.draw.rect(screen, (0, 0, 0), box, 2)

        pygame.draw.rect(screen, (0, 0, 0), region_progress_box, 2)

        screen.blit(font.render("Mutations", True, (255, 255, 255)), (mut_box.x + 10, mut_box.y + 10))
        screen.blit(font.render("Infections", True, (255, 255, 255)), (inf_box.x + 10, inf_box.y + 10))
        screen.blit(font.render(f"{display_infected:,}", True, (255, 255, 255)), (inf_box.x + 10, inf_box.y + 40))
        screen.blit(font.render("Region", True, (255, 255, 255)), (region_text_box.x + 10, region_text_box.y + 10))
        screen.blit(font.render(display_region, True, (255, 255, 255)), (region_text_box.x + 10, region_text_box.y + 40))
        # Difficulty label (top-right of the Region box)
        diff_colours = {"EASY": (0, 220, 0), "MEDIUM": (255, 165, 0), "HARD": (220, 0, 0)}
        if difficulty_label:
            diff_surf = font.render(difficulty_label, True, diff_colours.get(difficulty_label, (255, 255, 255)))
            screen.blit(diff_surf, (region_text_box.right - diff_surf.get_width() - 10, region_text_box.y + 10))

        screen.blit(font.render("Population", True, (255, 255, 255)), (pop_box.x + 10, pop_box.y + 10))
        screen.blit(font.render(f"{display_population:,}", True, (255, 255, 255)), (pop_box.x + 10, pop_box.y + 40))

        screen.blit(font.render("Deaths", True, (255, 255, 255)), (death_box.x + 10, death_box.y + 10))
        screen.blit(font.render(f"{display_dead:,}", True, (255, 255, 255)), (death_box.x + 10, death_box.y + 40))
        screen.blit(font.render("Cure", True, (255, 255, 255)), (cure_box.x + 10, cure_box.y + 10))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        running = handle_events()
        update_simulation(dt)

        display_region, display_infected, display_dead, display_population = resolve_display_stats()
        draw_frame(display_region, display_infected, display_dead, display_population)

        pygame.display.flip()

    return



main_menu()
