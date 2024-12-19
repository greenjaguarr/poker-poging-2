import pygame
import asyncio
import json
import websockets.asyncio.connection


# Kleur-definities
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CARD_COLOR = (240, 240, 240)  # Kleur van kaarten
FONT_COLOR = (0, 0, 0)
TABLE_GREEN = (0, 100, 0)

# Kaart Class
class Kaart:
    SUIT_SYMBOLS = {"harten": "♥", "ruiten": "♦", "klaveren": "♣", "schoppen": "♠"}

    def __init__(self, kleur, waarde):
        """
        kleur: str, bijv. "harten", "klaveren"
        waarde: str, bijv. "A", "K", "10"
        """
        self.kleur = kleur
        self.waarde = waarde

    def draw(self, screen, x, y, liggend=False, dicht=False):
        """
        Tekent een kaart op het scherm.
        x, y: positie waar de kaart wordt getekend.
        liggend: boolean, True = liggend, False = staand.
        dicht: boolean, True = kaart ligt dicht (geen waarde of symbool).
        """
        # Afmetingen
        width, height = (60, 90) if not liggend else (90, 60)

        # Teken de rechthoekige kaart
        pygame.draw.rect(screen, CARD_COLOR, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)  # Rand

        if not dicht:
            # Tekst op de kaart (waarde + symbool)
            font = pygame.font.SysFont("arial", 28)
            suit_symbol = self.SUIT_SYMBOLS.get(self.kleur, "?")
            text = font.render(f"{self.waarde} {suit_symbol}", True, FONT_COLOR)
            screen.blit(text, (x + 5, y + 5))
        else:
            # Optionele dichte kaart stijl: schuin gestreept of een effen kleur
            pygame.draw.rect(screen, BLACK, (x + 5, y + 5, width - 10, height - 10))

class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, text_color):
        self.rect:pygame.Rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, screen)->None:
        # Check if the mouse is over the button
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        # Draw the text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event)->bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def draw_river(screen, river):
    """
    Tekent de river (gemeenschappelijke kaarten) bovenaan de tafel.
    """
    start_y = 50
    x = 360
    spacing = 100

    for i, kaart in enumerate(river):
        y = start_y + i * spacing
        if kaart:  # Controleer of er een kaart is
            kaart.draw(screen, x, y)
        else:
            # Teken lege kaart
            pygame.draw.rect(screen, CARD_COLOR, (x, y, 60, 90))
            pygame.draw.rect(screen, BLACK, (x, y, 60, 90), 2)

def draw_game_state(screen, game_state):
    """
    Tekent de gehele tafel met spelers en kaarten.
    """
    screen_width, screen_height = screen.get_size()
    vertical_spacing = 100
    horizontal_spacing = 235
    start_x = 20
    start_y = 50

    font = pygame.font.SysFont("arial", 28)

    for i, speler in enumerate(game_state.players):
        row = i % 4
        col = i // 4

        # Posities bepalen
        x = start_x + col * horizontal_spacing * 2
        y = start_y + row * vertical_spacing

        # Spelervak tekenen
        pygame.draw.rect(screen, WHITE, (x, y, 150, 90))
        pygame.draw.rect(screen, BLACK, (x, y, 150, 90), 2)

        # Naam en coins weergeven
        name_text = font.render(speler.naam, True, FONT_COLOR)
        screen.blit(name_text, (x + 10, y + 10))

        coins_text = font.render(f"Coins: {speler.coins}", True, FONT_COLOR)
        screen.blit(coins_text, (x + 10, y + 35))

        # Kaarten tekenen (open of dicht)
        for j, (kaart, dicht) in enumerate(speler.hand):
            kaart_x = x + 160 + j * 70
            kaart.draw(screen, kaart_x, y, dicht=dicht)

def draw_buttons(screen:pygame.Surface,buttons:tuple[Button]):
    for button in buttons:
        button.draw(screen)

class Speler:
    def __init__(self, naam, coins, kaart1, kaart2, kaart1_dicht=True, kaart2_dicht=True):
        self.naam: str = naam
        self.coins: int = coins
        self.hand: list[tuple[Kaart, bool]] = [
            (kaart1, kaart1_dicht),
            (kaart2, kaart2_dicht)
        ]
        self.is_AanDeBeurt: bool = False
        self.is_Gepast: bool = False

class GameState:
    def __init__(self):
        self.players = [
            Speler("Speler1", 500, Kaart("harten", "A"), Kaart("schoppen", "K"), kaart1_dicht=False, kaart2_dicht=True),
            Speler("Speler2", 400, Kaart("ruiten", "5"), Kaart("klaveren", "7"), kaart1_dicht=True, kaart2_dicht=True),
            Speler("Speler3", 300, Kaart("harten", "3"), Kaart("klaveren", "4"), kaart1_dicht=False, kaart2_dicht=False),
            Speler("Speler4", 450, Kaart("schoppen", "9"), Kaart("harten", "2"), kaart1_dicht=True, kaart2_dicht=True),
            Speler("Speler5", 350, Kaart("ruiten", "K"), Kaart("klaveren", "5"), kaart1_dicht=False, kaart2_dicht=False),
            Speler("Speler6", 600, Kaart("klaveren", "J"), Kaart("harten", "7"), kaart1_dicht=True, kaart2_dicht=False),
        ]
        self.river = [
            Kaart("harten", "A"),
            Kaart("schoppen", "10"),
            Kaart("klaveren", "2"),
            Kaart("ruiten", "V"),
            None  # Lege plek voor een mogelijke kaart
        ]



# Networking
async def startup_handshake(websocket:websockets.asyncio.connection.Connection,naam:str)->str:
    websocket.send(json.dumps({"type": "connect", "name":naam}))
    asyncio.sleep(1)
    msg = await websocket.recv()
    event:dict = json.loads(msg)
    if not "type" in event:
        raise RuntimeError
    if event["type"] == 'error':
        errormessage = event['message']
        print(errormessage)
        exit() # boeie

    elif event["type"] == 'register':
        my_uuid:str = event['uuid']
    else:
        print("huh")
        exit()

    return my_uuid

async def read_messages(websocket)->None:
    '''This function reads the incoming messages. It modifies the gamestate'''
    async for message in websocket:
        event:dict = json.loads(message)
        pass # handle messages

# Function to handle sending messages from the queue
async def send_messages(websocket, queue)->None:
    while True:
        # Wait for a message to be available in the queue
        message = await queue.get()
        
        # Send the message over the websocket
        await websocket.send(message)
        # print(f"Sent message: {message}")
        
        # Mark the task as done
        queue.task_done()
    
async def handle_networking(websocket:websockets.asyncio.connection.Connection,naam:str,queue:asyncio.Queue):
    client_uuid:str = await startup_handshake(websocket,naam)

    read_task = asyncio.create_task(read_messages(websocket))
    send_task = asyncio.create_task(send_messages(websocket,queue))


# async def send_action(websocket, action):
#     message = json.dumps({"type": "action", "action": action})
#     await websocket.send(message)


# Main game loop
async def main_pygame(websocket,queue:asyncio.Queue):
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Poker Tafel")
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 36)
    BLUE = (0, 0, 255)
    LIGHTBLUE = (173, 216, 230)


    # GameState aanmaken
    game_state = GameState()

    pass_button = Button(50,600,200,150,"Pass",font,BLUE,LIGHTBLUE,BLACK)
    check_button = Button(300,600,200,150,"Check",font,BLUE,LIGHTBLUE,BLACK)
    raise_button = Button(550,600,200,150,"Raise",font,BLUE,LIGHTBLUE,BLACK)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif pass_button.is_clicked(event):
                # add message to the queue
                # await queue.put(message) 
                pass
            elif check_button.is_clicked(event):
                # add message to the queue
                pass
            elif raise_button.is_clicked(event):
                # handle raise
                # add message to the queue
                pass
        # Scherm vullen
        screen.fill(TABLE_GREEN)

        # Tekenen van de spelers en hun kaarten
        draw_game_state(screen, game_state)

        # Tekenen van de river (gemeenschappelijke kaarten)
        draw_river(screen, game_state.river)

        draw_buttons(screen,(pass_button,check_button,raise_button))
        # Update het scherm
        pygame.display.flip()
        asyncio.sleep(0)
        clock.tick(30)


    # add message to the queue, telling the server that I want to disconnect
    # for now just close the websocket
    await websocket.close()

    pygame.quit()


async def main():
    naam:str = input("Wat is jouw naam? Maximaal 10 characters")[:10]
    if ["'",'"',',','.','\\','/'] in naam:
        print("feut")
        exit()
    
    queue = asyncio.Queue() # this queue stores all messages to bne sent.

    async with websockets.connect("ws://localhost:8000") as websocket:
        # Create tasks for Pygame and receiving messages
        pygame_task = asyncio.create_task(main_pygame(websocket,queue))
        network_task = asyncio.create_task(handle_networking(websocket,naam,queue))

        # Run both tasks concurrently
        await asyncio.gather(pygame_task, network_task)

if __name__ == "__main__":
    asyncio.run(main())