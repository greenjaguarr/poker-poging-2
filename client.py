import pygame
import asyncio
import json
import websockets.asyncio.connection


pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Poker Tafel")
clock = pygame.time.Clock()


# Kleur-definities
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CARD_COLOR = (240, 240, 240)  # Kleur van kaarten
FONT_COLOR = (0, 0, 0)
TABLE_GREEN = (0, 100, 0)
font = pygame.font.Font(None, 36)
BLUE = (0, 0, 255)
LIGHTBLUE = (173, 216, 230)
GREY = (150,150,150)

# Kaart Class
class Kaart:
    SUIT_SYMBOLS = {"harten": "♥", "ruiten": "♦", "klaveren": "♣", "schoppen": "♠"}

    def __init__(self, kleur, waarde):
        """
        kleur: str, bijv. "harten", "klaveren"
        waarde: str, bijv. "A", "K", "T"
        """
        self.kleur = kleur
        self.waarde = waarde

    def __str__(self):
        # lmao waarom niet
        return f"{self.waarde}{self.SUIT_SYMBOLS[self.kleur]}"

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

    font = pygame.font.SysFont("arial", 24)

    # draw pot
    screen.blit(font.render(f"Pot: {game_state.pot}", True, FONT_COLOR), (screen_width - 250, 10))
    screen.blit(font.render(f"Highest bid: {game_state.highest_bet}", True, FONT_COLOR), (screen_width - 250, 25))
    
    for stoelnummer, speler in game_state.stoelen.items():
        row = (stoelnummer-1) % 4
        col = (stoelnummer-1) // 4

        # Posities bepalen
        x = start_x + col * horizontal_spacing * 2
        y = start_y + row * vertical_spacing

        # Spelervak tekenen
        if speler.is_Gepast:
            color = GREY
        elif speler.is_AanDeBeurt:
            color = LIGHTBLUE
        else:
            color = WHITE
        pygame.draw.rect(screen, color, (x, y, 150, 90))
        pygame.draw.rect(screen, BLACK, (x, y, 150, 90), 2)

        # Naam en coins weergeven
        name_text = font.render(speler.naam, True, FONT_COLOR)
        screen.blit(name_text, (x + 10, y + 10))

        coins_text = font.render(f"Coins: {speler.coins}", True, FONT_COLOR)
        screen.blit(coins_text, (x + 10, y + 35))

        current_bet_text = font.render(f"Current bet: {speler.current_bet}", True, FONT_COLOR)
        screen.blit(current_bet_text, (x + 10, y + 60))

        # Kaarten tekenen (open of dicht)
        for j, kaart in enumerate(speler.hand):
            kaart_x = x + 160 + j * 70
            if not kaart:
                continue
            kaart.draw(screen, kaart_x, y, dicht=False)


def draw_buttons(screen:pygame.Surface,buttons:tuple[Button]):
    for button in buttons:
        button.draw(screen)

class Speler:
    def __init__(self, naam: str, coins: int, hand: list[tuple[Kaart, bool]] = None):
        """
        Parameters:
        - naam: Name of the player.
        - coins: The number of coins the player has.
        - hand: A list of tuples, each containing a Kaart instance and a boolean for face-down status.
        """
        self.naam: str = naam
        self.coins: int = coins
        self.hand: list[tuple[Kaart, bool]] = hand or []
        self.is_AanDeBeurt: bool = False
        self.is_Gepast: bool = False
        self.current_bet: int = 0

class GameState:
    def __init__(self) -> None:
        self.MAXSPELERS = 8
        self.stoelen:dict = {}  # {stoelnummer: speler_object}
        # self.AanDeBerut:str = None # uuid of player whos turn it is
        self.river = [None, None, None, None, None] # List of cards in river. None represents no card
        self.pot:int = 0
        self.highest_bet:int = 0

STATE_LOCK = asyncio.Lock()
global state
state = GameState()

shutdown_event = asyncio.Event()

async def startup_handshake(websocket: websockets.asyncio.connection.Connection, naam: str) -> str:
    print('[DEBUG] startup handshake client side started')
    try:
        await websocket.send(json.dumps({"type": "connect", "name": naam}))
        await asyncio.sleep(1)
        msg = await websocket.recv()
        event: dict = json.loads(msg)
        if not "type" in event:
            raise RuntimeError("Invalid message received during handshake")
        if event["type"] == 'error':
            errormessage = event['message']
            print(f"[ERROR] {errormessage}")
            exit()
        elif event["type"] == 'register':
            my_uuid: str = event['uuid']
        else:
            print("[ERROR] Unexpected message type during handshake.")
            exit()
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[ERROR] Connection closed unexpectedly during handshake: {e}")
        exit()
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to decode JSON during handshake: {e}")
        exit()
    except Exception as e:
        print(f"[ERROR] Unexpected error during handshake: {e}")
        exit()
    
    print('[DEBUG] startup handshake client side finished')
    return my_uuid


async def read_messages(websocket,client_uuid)->None:
    '''This function reads the incoming messages. It modifies the gamestate'''
    global state
    async for message in websocket:
        if shutdown_event.is_set():
            break  # Stop de lus als het shutdown-event is ingesteld
        await asyncio.sleep(0.01)
        try:
            event: dict = json.loads(message)
            if not isinstance(event, dict):
                raise ValueError("Received message is not a valid dictionary.")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to decode message: {message}, Error: {str(e)}")
            continue  # Skip processing for this invalid message

        if not "type" in event:
            print(f"[ERROR] Received message with no 'type' field: {event}")
            continue

        if event["type"] == 'register': continue


        elif event["type"] == 'gamestate':
            print(f"Received gamestate update")
            try:
                nieuwe_state = GameState()
                # download gamestate
                # nieuwe_state.AanDeBeurt = event["aanDeBeurt"]
                nieuwe_state.river = [
                    Kaart(kaart["kleur"], kaart["waarde"]) if kaart else None
                    for kaart in event["river"]
                ]
                nieuwe_state.spelersdata = event["spelers"]
                
                nieuwe_state.stoelen = {}
                for stoelnummer, spelerdict in nieuwe_state.spelersdata.items():
                    stoelnummer = int(stoelnummer)
                    hand = []
                    for kaart in spelerdict["hand"]:
                        if kaart:
                            hand.append(Kaart(kaart["kleur"], kaart["waarde"]))
                        else:
                            hand.append(None)
                    speler = Speler(
                        naam=spelerdict["naam"],
                        coins=spelerdict["coins"],
                        hand=hand
                    )
                    speler.is_AanDeBeurt = spelerdict["isAanDeBeurt"]
                    speler.is_Gepast = spelerdict["isGepast"]
                    speler.current_bet = spelerdict["current_bet"]
                    nieuwe_state.stoelen[stoelnummer] = speler
                    nieuwe_state.pot = event["pot"]
                    nieuwe_state.highest_bet = event["highest bid"]
                async with STATE_LOCK:
                    state = nieuwe_state
            except KeyError as e:
                print(f"[ERROR] Missing key in gamestate update: {e}")
            except Exception as e:
                print(f"[ERROR] Unexpected error while updating gamestate: {e}")

        elif event["type"] == 'info':
            print(event['message'])
        elif event['type'] == 'error':
            print(event['message'])
        else:
            print(f'received event of type {event["type"]} which is not supported')
        pass # handle messages

# Function to handle sending messages from the queue
async def send_messages(websocket, queue, my_uuid:str)->None:
    uuid = {'uuid': my_uuid}
    while True:
        await asyncio.sleep(0)
        if shutdown_event.is_set():
            break  # Stop de lus als het shutdown-event is ingesteld
        try:
            message:dict = await queue.get()
            message.update(uuid)
            await websocket.send(json.dumps(message))
            queue.task_done()
        except websockets.ConnectionClosed:
            print("Connection to server lost.")
            break
        except Exception as e:
            print(f"Error sending message: {e}")

    
async def handle_networking(websocket: websockets.asyncio.connection.Connection, naam: str, queue: asyncio.Queue):
    try:
        client_uuid = await startup_handshake(websocket, naam)
        read_task = asyncio.create_task(read_messages(websocket, client_uuid))
        send_task = asyncio.create_task(send_messages(websocket, queue, client_uuid))
        await asyncio.gather(read_task, send_task)
    except websockets.exceptions.InvalidURI as e:
        print(f"[ERROR] Invalid WebSocket URI: {e}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[ERROR] WebSocket connection was closed unexpectedly: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error during networking: {e}")



# async def send_action(websocket, action):
#     message = json.dumps({"type": "action", "action": action})
#     await websocket.send(message)


# Raise Amount Input
async def get_raise_amount(screen, font):
    """Prompt user to enter a raise amount."""
    input_box = pygame.Rect(300, 500, 200, 50)
    color = (255, 255, 255)
    text = ''
    active = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    return int(text) if text.isdigit() else None
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        screen.fill((0, 0, 0), input_box)
        pygame.draw.rect(screen, color, input_box)
        txt_surface = font.render(text, True, (0, 0, 0))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.display.flip()
        await asyncio.sleep(0)

# Main game loop
async def game_loop(websocket,queue:asyncio.Queue):

    pass_button = Button(50,600,200,150,"Pass",font,BLUE,LIGHTBLUE,BLACK)
    check_button = Button(300,600,200,150,"Check",font,BLUE,LIGHTBLUE,BLACK)
    raise_button = Button(550,600,200,150,"Raise",font,BLUE,LIGHTBLUE,BLACK)

    counter = 0
    request_gamestate = {"type":'request gamestate'}

    running = True
    while running:
        counter+=1
        if counter%50 == 0:
            await queue.put(request_gamestate)
        async with STATE_LOCK:
            game_state = state

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                shutdown_event.set()
                await queue.put({'type':'disconnect'})
            elif pass_button.is_clicked(event):
                await queue.put({"type": "action", "action": "pass"})
            elif check_button.is_clicked(event):
                await queue.put({"type": "action", "action": "check"})
            elif raise_button.is_clicked(event):
                print("raise button clicked")
                await queue.put({"type": "action", "action": "raise", "amount": 10})
                
                # pass # its fucking broken
                # raise_amount = await get_raise_amount(screen, font)
                # if raise_amount:
                #     await queue.put({"type": "action", "action": "raise", "amount": raise_amount})

        screen.fill((0, 100, 0))
        draw_game_state(screen, game_state)
        draw_buttons(screen, (pass_button,check_button,raise_button))
        draw_river(screen,game_state.river)
        pass_button.draw(screen)
        check_button.draw(screen)
        raise_button.draw(screen)

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(30)

    await websocket.close()
    pygame.quit()


async def main():
    naam:str = input("Wat is jouw naam? Maximaal 10 characters ")[:10]
    if any(c in naam for c in ["'", '"', ",", ".", "\\", "/"]):
        print("Ongeldige karakters in naam.")
        exit()
    
    queue = asyncio.Queue() # this queue stores all messages to bne sent.

    async with websockets.connect("ws://192.168.178.110:8000") as websocket:
        # Create tasks for Pygame and receiving messages
        pygame_task = asyncio.create_task(game_loop(websocket,queue))
        network_task = asyncio.create_task(handle_networking(websocket,naam,queue))

        # Run both tasks concurrently
        await asyncio.gather(pygame_task, network_task)

if __name__ == "__main__":
    asyncio.run(main())