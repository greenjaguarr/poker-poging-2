from itertools import combinations

class Kaart:
    SUIT_SYMBOLS = {"harten": "♥", "ruiten": "♦", "klaveren": "♣", "schoppen": "♠"}

    def __init__(self, kleur, waarde):
        """
        kleur: str, bijv. "harten", "klaveren"
        waarde: str, bijv. "A", "K", "10"
        """
        self.kleur = kleur
        self.waarde = waarde


kaarten1 = [Kaart("harten","9"),
           Kaart("schoppen","K"),
           Kaart("klaveren","K"),
           Kaart("harten","B"),
           Kaart("harten","9"),
           Kaart("harten","T"),
           Kaart("harten","V")]

def calc_waarde(kaarten:list[Kaart]):
    # kaarten is een list met lengte 7
    # kleur: str, bijv. "harten", "klaveren"
    # waarde: str, bijv. "A", "K", "T"
    kaartwaardefrequentie = {}
    kaartkleurfrequentie = {}
    handresult = []
    for kaart in kaarten:
        
        if kaart.kleur in kaartkleurfrequentie:
            kaartkleurfrequentie[kaart.kleur] +=1
        else:
            kaartkleurfrequentie.update({kaart.kleur:1})
        
        if kaart.waarde in kaartwaardefrequentie:
            kaartwaardefrequentie[kaart.waarde] +=1
        else:
            kaartwaardefrequentie.update({kaart.waarde:1})
    
    kaartwaardefrequentie_list = list(kaartwaardefrequentie.values())
    kaartkleurfrequentie_list = list(kaartkleurfrequentie.values())
    
    # checking for flush
    if max(kaartkleurfrequentie_list) >= 5:
        waardes_in_flush = []
        
        for kaart in kaarten:
            if kaartkleurfrequentie[kaart.kleur] >= 5:
                waardes_in_flush.append(kaart.waarde)
        
        handresult.append(["flush", waardes_in_flush])

    # Function to determine if hand contains a straight
    def highest_straight(hand):
        # Define card values (mapping face cards and ace)
        card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'B': 11, 'V': 12, 'K': 13, 'A': 14}
        
        # Extract the ranks from the hand (ignoring the suits)
        values = [card_values[card.value] for card in hand]

        # Function to check for the highest straight from the list of values
        def find_highest_straight(values):
            values = sorted(set(values))  # Remove duplicates and sort
            highest_straight = None
            
            # Check all combinations of 5 cards from the 7 cards
            for combo in combinations(values, 5):
                # Check if the combo forms a straight (consecutive cards)
                if all(combo[i] == combo[i-1] + 1 for i in range(1, len(combo))):
                    # Keep track of the highest straight (based on the highest card in the straight)
                    if highest_straight is None or combo[-1] > highest_straight[-1]:
                        highest_straight = combo
            return highest_straight
        
        # First, try Ace as high (A = 14)
        highest_straight_high = find_highest_straight(values)

        # Now, try Ace as low (A = 1) by replacing all Aces (14) with 1
        values_as_low = [1 if value == 14 else value for value in values]
        highest_straight_low = find_highest_straight(values_as_low)

        return highest_straight_high or highest_straight_low

    # checking for quads
    if max(kaartwaardefrequentie_list) == 4:
        for kaart in kaarten: 
            if kaartwaardefrequentie[kaart.waarde] == 4:
                waarde_van_quads = kaart.waarde
        
        handresult.append(["quads", waarde_van_quads])
        kaartwaardefrequentie_list.remove(4)

    # checking for trips
    for i in range(2):
        if max(kaartwaardefrequentie_list) == 3:
            for kaart in kaarten: 

                if kaart.waarde in kaartwaardefrequentie:
                    if kaartwaardefrequentie[kaart.waarde] == 3:
                        waarde_van_trips = kaart.waarde
            
            handresult.append(["trips", waarde_van_trips])

            kaartwaardefrequentie.pop(waarde_van_trips)
            kaartwaardefrequentie_list.remove(3)
    
    # checking for pairs
    for i in range(3):
        if max(kaartwaardefrequentie_list) == 2:
            for kaart in kaarten: 

                if kaart.waarde in kaartwaardefrequentie:
                    if kaartwaardefrequentie[kaart.waarde] == 2:
                        waarde_van_pair = kaart.waarde
            
            handresult.append(["pair", waarde_van_pair])

            kaartwaardefrequentie.pop(waarde_van_pair)
            kaartwaardefrequentie_list.remove(2)
  


    print(handresult)


    return handresult

def compare(kaarten1, kaarten2):
    '''Return "1" if kaarten1 is beter,
    "2" als kaarten2 beter is
    "0" als het een gelijkspel is'''

calc_waarde(kaarten1)
