#!/usr/bin/env python

import asyncio
import json
import logging
import uuid
from websockets.asyncio.server import broadcast, serve
# import websockets
import random
from itertools import cycle

logging.basicConfig()

USERS = {}  # Slaat de websocket en bijbehorende UUID op

USERS_LOCK = asyncio.Lock()

class Kaart:
    SUIT_SYMBOLS = {"harten": "♥", "ruiten": "♦", "klaveren": "♣", "schoppen": "♠"}

    def __init__(self, kleur, waarde):
        """
        kleur: str, bijv. "harten", "klaveren"
        waarde: str, bijv. "A", "K", "T"
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
        self.current_bet:int
        self.mostrecentaction = None

    async def wait_for_action(self):
        await self.action_event.wait()  # Wait for the player to take action
        self.action_event.clear()  # Reset the event for the next round

class GameState:
    SUIT_SYMBOLS = {"harten": "♥", "ruiten": "♦", "klaveren": "♣", "schoppen": "♠"}
    def __init__(self) -> None:
        self.MAXSPELERS = 8
        self.spelers:dict = {}  # {client_uuid: speler_object}
        self.AanDeBerut:str = None # uuid of player whos turn it is # of stoelnummer?
        self.river = [None, None, None, None, None] # List of cards in river. None represents no card
        self.is_stoel_bezet = [False,False,False,False,False,False,False,False]
        self.pot = 0       # Total coins in the pot
        self.current_bet = 0  # Current highest bet
        self.round_state = ""  # Describes the current phase of the game

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
            self.spelers[client_uuid].mostrecentaction = {"action":'pass'}
        elif event["action"] == "check":
            self.spelers[client_uuid].mostrecentaction = {"action":'check'}
        elif event["action"] == "raise":
            bedrag:int = event.get("amount")
            if bedrag is None: return
            self.spelers[client_uuid].mostrecentaction = {"action":'raise', 'amount': bedrag}
        else:
            raise ValueError("Onbekende actie")
        # Signal that the player has made their move
        self.spelers[client_uuid].action_event.set()



    def voeg_speler_toe(self, client_uuid, speler):
        if len(self.spelers) >= self.MAXSPELERS:
            raise ValueError("Maximale aantal spelers bereikt.")
        for i,stoel in enumerate(self.is_stoel_bezet):
            if stoel==False:
                speler.stoelnummer = i+1
                self.is_stoel_bezet[i] = True
                break
        print("[CONNECTION]",f'Beshcikbare stoelen {["X" if stoel else "O" for stoel in self.is_stoel_bezet]}')
        self.spelers[client_uuid] = speler

    def verwijder_speler(self, client_uuid):
        if client_uuid in self.spelers:
            stoel = self.spelers[client_uuid].stoelnummer
            self.is_stoel_bezet[stoel-1] = False
            del self.spelers[client_uuid]
        print("[DISCONNECTION]",f'Beshcikbare stoelen {["X" if stoel else "O" for stoel in self.is_stoel_bezet]}')

    def bezette_stoelen(self):
        l = []
        for i,stoel in enumerate(self.is_stoel_bezet):
            if stoel:
                l.append(i+1)
        return l
    
    def actieve_spelers(self):
        l = []
        for uuid,speler in self.spelers.items():
            if not speler.is_Gepast:
                l.append(uuid)
        return l

        
    def deel_kaarten(self):
        for uuid, speler in self.spelers.items():
            speler.hand = [self.kaarten.pop(), self.kaarten.pop()]


    def bet(self,player_uuid:str,amount:int)->None:
        player = self.spelers[player_uuid]
        self.pot+=amount
        player.coins+=-amount
        player.current_bet+=amount
        if player.current_bet > self.highest_bet:
            self.highest_bet = player.current_bet


    def eerste_fase(self,iterator):
        """Handle the initial blinds phase."""
        self.round_state = "eerste_fase"
        next_player = next(iterator)
        self.bet(next_player,1)
        next_player = next(iterator)
        self.bet(next_player,2)

    async def bied_fase(self, iterator):
        """Verwerkt de biedronde waar elke speler kan passen, checken of raisen."""
        self.round_state = "biedfase"
        self.current_bet = 0  # Start met een inzet van 0
        self.highest_bet = 0  # De hoogste inzet start op 0
        actieve_spelers = self.actieve_spelers()  # Alle actieve spelers (niet gepast)

        # Alle actieve spelers krijgen om beurten de kans om te handelen.
        while True:
            # 1 loop van deze loop is 1 beurt van 1 speler
            speler_uuid = next(iterator)
            speler:Speler = self.spelers[speler_uuid]
            print(speler.naam, ' is aan de beurt' )

            if speler.is_Gepast:
                continue  # Sla spelers over die gepast hebben

            await speler.wait_for_action()

            # # Wacht op de actie van de speler
            # if speler.mostrecentaction is None:  # Als de speler nog niets heeft gedaan
            #     continue  # Wacht op actie

            actie = speler.mostrecentaction["action"]
            if actie == "pass":
                speler.is_Gepast = True  # Markeer de speler als gepast
                logging.info(f"Speler {speler.naam} heeft gepast.")
            elif actie == "check":
                # Check of de speler de huidige inzet gelijk houdt
                if speler.current_bet < self.highest_bet:
                    # Als de inzet niet gelijk is, moet de speler de juiste hoeveelheid betalen
                    ontbrekend_bedrag = self.highest_bet - speler.current_bet
                    self.bet(speler_uuid, ontbrekend_bedrag)
                logging.info(f"Speler {speler.naam} heeft gecheckt.")
            elif actie == "raise":
                # Als de speler raise, verhogen we de inzet
                bedrag = speler.mostrecentaction.get("amount", 0)

                # moet deze check perse hier
                if bedrag <= self.highest_bet:
                    logging.warning(f"Speler {speler.naam} probeert te raisen met een bedrag dat lager is dan de hoogste inzet.")
                    continue  # We negeren dit, omdat het minder is dan de hoogste bet

                # self.highest_bet = bedrag  # Update de hoogste inzet
                # self.bet(speler_uuid, bedrag - speler.current_bet)  # Betale het verschil
                # logging.info(f"Speler {speler.naam} heeft verhoogd naar {bedrag}.")
                speler.bet(speler_uuid, bedrag)


            # Controleer of de biedronde klaar is (alle spelers hebben dezelfde inzet of gepast)
            if all(speler.current_bet == self.highest_bet or speler.is_Gepast for speler in self.spelers.values()):
                break  # Einde biedronde

        self.round_state = "fase_einde"
        logging.info("Biedronde is geëindigd.")

    def compare(self):
        # compare hands
        # get the best hand
        # give the pot to the player with the best hand
        # if there is a draw, split the pot
        # Not implemented yet, for now just give the pot to the first player
        return "1"
    

    def bepaal_winnaar(self):
        """Bepaal de winnaar van de ronde en deel de pot uit."""
        actieve_spelers = self.actieve_spelers()
        if len(actieve_spelers) == 1:
            winnaar_uuid = actieve_spelers[0]
        else:
            # for speler_uuid in actieve_spelers:
            #     for 
            #     self.compare()
            # not implemented yet, just give the pot to the first player
            winnaar_uuid = actieve_spelers[0]
        winnaar = self.spelers[winnaar_uuid]
        winnaar.coins += self.pot
        logging.info(f"Speler {winnaar.naam} wint de pot van {self.pot} coins.")
    
    async def doe_1_ronde(self,deler_uuid):
        """Execute one full poker round."""

        # SETUP

        self.pot = 0
        for _,speler in self.spelers.items():
            speler.current_bet = 0
    
        # reset kaarten
        self.river = [None,None,None,None,None] # None represents the lack of a card.
        for uuid, speler in self.spelers.items():
            speler.hand = [None,None]
        # schud kaarten
        self.kaarten = [Kaart(kleur, waarde) for kleur in self.SUIT_SYMBOLS.keys() for waarde in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "B", "V" "K"]]
        random.shuffle(self.kaarten)
        self.deel_kaarten()

        actieve_spelers:list[str] = self.spelers.keys()
        # turn it into an iterator that can loop
        iterator = cycle(actieve_spelers)
        while next(iterator) != deler_uuid:
            continue

        # BEGIN

        self.eerste_fase(iterator)
        await self.bied_fase()
        self.river[0] = self.kaarten.pop()
        self.river[1] = self.kaarten.pop()
        self.river[2] = self.kaarten.pop()
        await self.bied_fase()
        self.river[3] = self.kaarten.pop()
        await self.bied_fase()
        self.river[4] = self.kaarten.pop()
        await self.bied_fase()
        self.bepaal_winnaar()

    #     # Check for winner
    #     # made by a friend
    #     # hand out coins



state = GameState()

async def game_loop():
    """
    Periodieke taken voor de game, zoals het bijwerken van de staat.
    """
    await asyncio.sleep(3)
    deler = 7

    while len(state.spelers) < 2:
        await asyncio.sleep(3)
        print("not enough players")
    print("De game begint")


    while True:
        def advance_deler(deler):
            bezette_stoelen = state.bezette_stoelen()
            deler = deler%8
            deler+=1
            while not deler in bezette_stoelen:
                deler = deler%8
                deler+=1
            return deler
        deler = advance_deler(deler)
        deler_uuid = None
        for uuid,speler in state.spelers.items():
            if speler.stoelnummer == deler:
                deler_uuid = uuid
        if deler_uuid == None:
            exit() # rip

        print("[GAME] Game loopt. Bezig met state updates...", "Nieuwe ronde begint")
        # TODO: Voeg hier logica toe voor het beheren van rondes, inzetten, enz.
        await state.doe_1_ronde(deler)




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
    if "name" in event:
        speler_naam = event["name"]
    
    else:
    # Voeg een nieuwe speler toe aan de game met een standaardnaam en startcoins
        speler_naam = f"Speler_{len(state.spelers) + 1}"  # Dynamisch gegenereerde naam
        print("Er is iets fout gegaan bij het ontvangen van de naam van deze speler")
        print("Event is ",event)
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
                if not state.spelers[client_uuid].isAanDeBeurt:
                    continue
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
        # async with USERS_LOCK:
        #     del USERS[client_uuid]
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
    game_task = asyncio.create_task(game_loop())  # Start de game loop
    server_task = serve(network_manager, "192.168.178.110", 8000)  # WebSocket server

    print("[INFO] Server gestart op ws://192.168.178.110:8000")
    await asyncio.gather(game_task, server_task)  # Voer beide taken parallel uit



if __name__ == "__main__":
    asyncio.run(main())
