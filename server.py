#!/usr/bin/env python

import asyncio
import json
import logging
import uuid
from websockets.asyncio.server import broadcast, serve
# import websockets
import random

logging.basicConfig()

USERS = {}  # Slaat de websocket en bijbehorende UUID op

USERS_LOCK = asyncio.Lock()

class Kaart:
    SUIT_SYMBOLS = {"harten": "♥", "ruiten": "♦", "klaveren": "♣", "schoppen": "♠"}

    def __init__(self, kleur, waarde):
        """
        kleur: str, bijv. "harten", "klaveren"
        waarde: str, bijv. "A", "K", "10"
        """
        self.kleur = kleur
        self.waarde = waarde

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
        self.stoelnummer:int

class GameState:
    def __init__(self) -> None:
        self.MAXSPELERS = 8
        self.spelers:dict = {}  # {client_uuid: speler_object}
        self.AanDeBerut:str = None # uuid of player whos turn it is
        self.river = [None, None, None, None, None] # List of cards in river. None represents no card
        self.is_stoel_bezet = [False,False,False,False,False,False,False,False]

    def create_state_message(self, target_uuid) -> str:
        """
        Genereer een gamestate die alleen informatie bevat die zichtbaar is voor de gevraagde client.
        """
        spelers_data = {}
        for uuid, speler in self.spelers.items():
            # spelers_data[uuid] = {
            if speler.stoelnummer in spelers_data:
                raise ValueError(f"Duplicate stoelnummer detected: {speler.stoelnummer}")
            
            spelers_data[speler.stoelnummer] = {
                "naam": speler.naam,
                "coins": speler.coins,
                "hand": [
                    {"kleur": kaart.kleur, "waarde": kaart.waarde} if (uuid == target_uuid or not dicht) and kaart is not None else None
                    for kaart, dicht in speler.hand
                ],
                "isAanDeBeurt": speler.is_AanDeBeurt,
                "isGepast": speler.is_Gepast,
                "stoelnummer": speler.stoelnummer
            }
        return json.dumps({
            "type": "gamestate",
            "spelers": spelers_data,
            "river": [
                {"kleur": kaart.kleur, "waarde": kaart.waarde} if kaart else None
                for kaart in self.river
            ],
            "aanDeBeurt": self.AanDeBerut,
        })
    

    def handle_client_input(self, event:dict, client_uuid:str)->None:
        # assert that client is allowed to make this action
        # update the gamestate, for example if the action is pass, then set the next player's is_AanDeBeurt to True. 
        logging.info(f"Speler {client_uuid} heeft actie: {event['action']} uitgevoerd.")
        if event["action"] == "pass":
            self.spelers[client_uuid].is_Gepast = True
            self.volgende_beurt()
        elif event["action"] == "check":
            # Voeg logica toe voor check
            self.volgende_beurt()
        elif event["action"] == "raise":
            bedrag = event.get("amount", 0)
            self.spelers[client_uuid].coins -= bedrag
            # Voeg raise-logica toe
            self.volgende_beurt()
        else:
            raise ValueError("Onbekende actie")



    def voeg_speler_toe(self, client_uuid, speler):
        if len(self.spelers) >= self.MAXSPELERS:
            raise ValueError("Maximale aantal spelers bereikt.")
        for i,stoel in enumerate(self.is_stoel_bezet):
            if stoel==False:
                speler.stoelnummer = i+1
                self.is_stoel_bezet[i] = True
                break
        self.spelers[client_uuid] = speler

    def verwijder_speler(self, client_uuid):
        if client_uuid in self.spelers:
            stoel = self.spelers[client_uuid].stoelnummer
            self.is_stoel_bezet[stoel-1] = False
            del self.spelers[client_uuid]
        
    def volgende_beurt(self):
        uuids = list(self.spelers.keys())
        huidige_index = uuids.index(self.AanDeBerut)
        self.AanDeBerut = uuids[(huidige_index + 1) % len(uuids)]


    def schud_kaarten(self):
        # take all of the cards away from all players and the river.
        self.river = [None,None,None,None,None] # None represents the lack of a card.
        for uuid, speler in self.spelers.items():
            speler.hand = [None,None]
            self.kaarten = [Kaart(kleur, waarde) for kleur in self.SUIT_SYMBOLS.keys() for waarde in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "B", "V" "K"]]
        random.shuffle(self.kaarten)

    def deel_kaarten(self):
        for uuid, speler in self.spelers.items():
            speler.hand = [self.kaarten.pop(), self.kaarten.pop()]



state = GameState()


async def startup_handshake(websocket):
    """
    Registreer de client, geef een unieke UUID terug en voeg een speler toe aan de game.
    """
    client_uuid:str = str(uuid.uuid4())  # Genereer unieke UUID
    async with USERS_LOCK:  # Voorkom race conditions
        USERS[client_uuid] = websocket  # Bewaar websocket met UUID

    print(f"[INFO] Client verbonden met UUID: {client_uuid}")

    msg = await websocket.recv()
    event:dict = json.loads(msg)
    if "naam" in event:
        speler_naam = event["naam"]
    
    else:
    # Voeg een nieuwe speler toe aan de game met een standaardnaam en startcoins
        speler_naam = f"Speler_{len(state.spelers) + 1}"  # Dynamisch gegenereerde naam
        print("Er is iets fout gegaan bij het ontvangen van de naam van deze speler")
    speler_start_coins = 100  # Standaard aantal coins
    nieuwe_speler = Speler(naam=speler_naam, coins=speler_start_coins)
    
    try:
        state.voeg_speler_toe(client_uuid, nieuwe_speler)
        print(f"[INFO] {speler_naam} toegevoegd aan het spel.")
        # Stuur de UUID naar de client
        await websocket.send(json.dumps({"type": "register", "uuid": client_uuid}))
    except ValueError as e:
        await websocket.send(json.dumps({"type": "error", "message": str(e)}))
        return  # Stop als er te veel spelers zijn
    return client_uuid



async def handle_message(websocket, client_uuid):
    """
    Verwerkt berichten van een client.
    """
    try:
        async for message in websocket:
            event = json.loads(message)

            # Controleer of de client zijn UUID meestuurt
            if event.get("uuid") != client_uuid:
                await websocket.send(json.dumps({"type": "error", "message": "Ongeldige UUID"}))
                continue

            # controleer of er een type zit in de boodschap. Iedere geldige boodschap bevat "type"
            if "type" not in event:
                await websocket.send(json.dumps({"type": "error", "message": "Ongeldig bericht"}))
                continue
            # Verwerk acties
            elif event["type"] == "action":
                try:
                    state.handle_client_input(event, client_uuid)
                except ValueError as e:
                    await websocket.send(json.dumps({"type": "error", "message": str(e)}))

            if event['type'] == 'request gamestate':
                msg = state.create_state_message(client_uuid) # use uuid or websocket to refer to a specific player?
                await websocket.send(msg)


                        # Verwerk een disconnect event
            if event["type"] == "disconnect":
                logging.info(f"[INFO] Client {client_uuid} heeft verbinding verbroken via disconnect-event.")
                async with USERS_LOCK:
                    USERS.pop(client_uuid, None)  # Verwijder websocket uit USERS
                state.verwijder_speler(client_uuid)  # Verwijder speler uit de game state
                await websocket.send(json.dumps({"type": "info", "message": "Je bent succesvol afgemeld."}))
                return  # Beëindig de communicatie met deze clien
            

    finally:
        async with USERS_LOCK:
            del USERS[client_uuid]
        if client_uuid in state.spelers:
            del state.spelers[client_uuid]
        logging.info(f"[INFO] Client {client_uuid} is verbroken.")



async def network_manager(websocket):
    """
    De main handler per client:
    - Startup handshake
    - Steady state processing
    """
    client_uuid = await startup_handshake(websocket)
    await handle_message(websocket, client_uuid)


async def main():
    async with serve(network_manager, "localhost", 8000):
        print("[INFO] Server gestart op ws://localhost:8000")
        await asyncio.get_running_loop().create_future()  # Houd de server actief


if __name__ == "__main__":
    asyncio.run(main())
