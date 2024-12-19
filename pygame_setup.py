import pygame

# Kleur-definities
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CARD_COLOR = (240, 240, 240)  # Kleur van kaarten
FONT_COLOR = (0, 0, 0)
TABLE_GREEN = (0, 100, 0)

# Kaart Class
class Kaart:
    def __init__(self, kleur, waarde):
        """
        kleur: str, bijv. "harten", "klaveren"
        waarde: str, bijv. "A", "K", "10"
        """
        self.kleur = kleur
        self.waarde = waarde

    def draw(self, screen, x, y, liggend=False):
        """
        Tekent een kaart op het scherm.
        x, y: positie waar de kaart wordt getekend.
        liggend: boolean, True = liggend, False = staand.
        """
        # Afmetingen
        width, height = (60, 90) if not liggend else (90, 60)

        # Teken de rechthoekige kaart
        pygame.draw.rect(screen, CARD_COLOR, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)  # Rand

        # Tekst op de kaart
        font = pygame.font.SysFont(None, 24)
        font = pygame.font.SysFont("Ariel", 24)
        text = font.render(f"{self.waarde} {self.kleur[0]}", True, FONT_COLOR)
        screen.blit(text, (x + 5, y + 5))


# Functie om de spelers en kaarten te tekenen
def draw_game_state(screen, game_state):
    """
    Tekent de gehele tafel met spelers en kaarten.
    screen: pygame display surface
    game_state: een fictieve class met spelinformatie (maximaal 8 spelers)
    """
    # Afmetingen
    screen_width, screen_height = screen.get_size()
    vertical_spacing = 100
    horizontal_spacing = 200
    start_x = 50
    start_y = 50

    # Fonts
    font = pygame.font.SysFont(None, 28)

    # Loop door maximaal 8 spelers
    for i in range(8):
        row = i % 4
        col = i // 4

        x = start_x + col * horizontal_spacing
        y = start_y + row * vertical_spacing

        # Spelervak tekenen
        pygame.draw.rect(screen, WHITE, (x, y, 150, 80))
        pygame.draw.rect(screen, BLACK, (x, y, 150, 80), 2)

        # Spelerdata
        if i < len(game_state.players):
            player = game_state.players[i]
            name_text = font.render(player["naam"], True, FONT_COLOR)
            screen.blit(name_text, (x + 10, y + 10))

            coins_text = font.render(f"Coins: {player['coins']}", True, FONT_COLOR)
            screen.blit(coins_text, (x + 10, y + 35))

            # Kaarten tekenen
            kaart1 = Kaart(player["kaart1"]["kleur"], player["kaart1"]["waarde"])
            kaart2 = Kaart(player["kaart2"]["kleur"], player["kaart2"]["waarde"])

            kaart1.draw(screen, x + 160, y + 10)
            kaart2.draw(screen, x + 230, y + 10)

        else:
            # Leeg vak
            pass


# Test GameState Class
class GameState:
    def __init__(self):
        # Een lijst van spelers met kaarten en coins
        self.players = [
            {"naam": "Speler1", "coins": 500, "kaart1": {"kleur": "harten", "waarde": "A"}, "kaart2": {"kleur": "schoppen", "waarde": "K"}},
            {"naam": "Speler2", "coins": 400, "kaart1": {"kleur": "ruiten", "waarde": "5"}, "kaart2": {"kleur": "klaveren", "waarde": "7"}},
            {"naam": "Speler3", "coins": 300, "kaart1": {"kleur": "harten", "waarde": "3"}, "kaart2": {"kleur": "klaveren", "waarde": "4"}},
            {"naam": "Speler4", "coins": 200, "kaart1": {"kleur": "schoppen", "waarde": "Q"}, "kaart2": {"kleur": "ruiten", "waarde": "J"}},
            {"naam": "Speler5", "coins": 0, "kaart1": {"kleur": "harten", "waarde": "2"}, "kaart2": {"kleur": "schoppen", "waarde": "3"}},
        ]


# Main game loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Poker Tafel")
    clock = pygame.time.Clock()

    # GameState aanmaken
    game_state = GameState()

    # Game Loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Scherm vullen
        screen.fill(TABLE_GREEN)

        # Tekenen van de spelers en kaarten
        draw_game_state(screen, game_state)

        # Update het scherm
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
