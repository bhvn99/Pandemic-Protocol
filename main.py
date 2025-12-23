import pygame, sys, hashlib, os, json, time

# initialises window, fonts, caption, dimensions,difficulty and other prerequisites
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pandemic Protocol")
font = pygame.font.Font(None, 36)
font2big = pygame.font.Font("assets/BR.ttf", 75) 
font2 = pygame.font.Font("assets/BR.ttf", 40) 
BLACK = (0, 0, 0)
difficulty = "" 


  

# Hashed credentials ( which could later come from a file/database )
USERNAME = "user123"
HASH_PASSWORD = hashlib.sha256("pass123".encode()).hexdigest()


def login_screen():
    # Displays login UI and handles user inputs - loops until valid login
    text_user, text_pass = "", ""
    active_user = True
    message = ""

    # Rectangles for input boxes
    user_box = pygame.Rect(200, 350, 200, 40)
    pass_box = pygame.Rect(200, 410, 200, 40)

    # Load and scales the background image
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
                    hashedinput = hashlib.sha256(text_pass.encode()).hexdigest()
                    if text_user == USERNAME and hashedinput == HASH_PASSWORD:
                        return True   # Successful Hash - leave function
                    else:
                        message = "Login Failed!"
                else:
                    if active_user:
                        text_user += event.unicode
                    else:
                        text_pass += event.unicode

        # Draws input boxes
        pygame.draw.rect(screen, (0,0,0), user_box, 2)
        pygame.draw.rect(screen, (0,0,0), pass_box, 2)

        # Draws text
        screen.blit(font.render(text_user, True, (0,0,0)), (user_box.x+5, user_box.y+5))
        screen.blit(font.render("*"*len(text_pass), True, (0,0,0)), (pass_box.x+5, pass_box.y+5))

        # Login Labels
        screen.blit(font.render("Username:", True, (0,0,0)), (50, 355))
        screen.blit(font.render("Password:", True, (0,0,0)), (50, 415))
        screen.blit(font2big.render("Pandemic Protocol", True, (0,0,0)), (55, 100))

        # Status Message
        if message:
            screen.blit(font.render(message, True, (255,0,0)), (100, 220))

        pygame.display.flip()

def main_menu():
    background1 = pygame.image.load("assets/background1.png")
    background1 = pygame.transform.scale(background1, (WIDTH, HEIGHT))

    buttons = {
        "Play": pygame.Rect(540, 300, 200, 60),
        "How to Play": pygame.Rect(540, 380, 200, 60),
        "Achievements": pygame.Rect(540, 460, 200, 60)
    }

    while True:
        title = font2.render("Pandemic Protocol", True, (0,0,0))
        screen.blit(background1, (0, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        # self-centres the title
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for name, rect in buttons.items():
                    if rect.collidepoint(event.pos): # links button clicked with respective function
                        print(f"{name} clicked!")
                        if name == "Play":
                            Play()
                        elif name == "Achievements":
                            Achievements()
                        elif name == "How to Play":  
                            H2P()

        # Draws buttons
        for name, rect in buttons.items():
            pygame.draw.rect(screen, (0, 100, 200), rect)
            text = font.render(name, True, (255,255,255))
            screen.blit(text, (rect.x + rect.width//2 - text.get_width()//2,
                               rect.y + rect.height//2 - text.get_height()//2))

        pygame.display.flip()

def Play():

    def difficultyselect():
        background3 = pygame.image.load("assets/background3.png")
        background3 = pygame.transform.scale(background3, (WIDTH, HEIGHT))

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
                "infected": 1000,         # starts with a large outbreak
                "infectivity_rate": 1.3,  # spreads fast
                "severity_rate": 0.15,    # symptoms appear quickly
                "lethality_rate": 0.08    # kills more easily
            },
            "medium": {
                "infected": 100,
                "infectivity_rate": 1.0,
                "severity_rate": 0.1,
                "lethality_rate": 0.05
            },
            "hard": {
                "infected": 10,           
                "infectivity_rate": 0.8,  
                "severity_rate": 0.05,   
                "lethality_rate": 0.02    
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
                                "susceptible": 7_800_000_000 - preset["infected"],
                                "infected": preset["infected"],
                                "recovered": 0,
                                "dead": 0,

                                # Disease stats (dynamic during game)
                                "infectivity_rate": preset["infectivity_rate"],
                                "severity_rate": preset["severity_rate"],
                                "lethality_rate": preset["lethality_rate"],

                                # Logging + metadata
                                "timestamp_created": 0,
                                "history": []
                            }


                            with open(file_path, "w") as f:
                                json.dump(disease_data, f, indent=4)

                            print(f"[+] Disease file created: {file_path}")
                            running = False



                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    elif len(text_input) < 20:  # character limit
                        text_input += event.unicode
                 
            
    difficulty = difficultyselect()
    if difficulty:  
        diseasesetup()

    return True

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


# Main Program Flow


if login_screen():
    main_menu()


