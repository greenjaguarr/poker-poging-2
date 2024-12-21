class Kaart:
    def __init__(self, kleur, waarde):
        self.kleur = kleur
        self.waarde = waarde

    def __repr__(self):
        return f"Kaart(kleur='{self.kleur}', waarde='{self.waarde}')"

def waarde_naar_getal(waarde):
    waardes = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "B": 11, "V": 12, "K": 13, "A": 14}
    return waardes[waarde]

def contains_straight(cards):
    """
    Determine if the given 7-card hand contains one or more straights.

    Parameters:
        cards (list of Kaart): A list of 7 Kaart objects.

    Returns:
        tuple: A tuple containing a boolean indicating if any straight exists, and a list of all straights found as lists of Kaart objects.
    """
    # Map ranks to numerical values
    rank_map = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'T': 10, 'B': 11, 'V': 12, 'K': 13, 'A': 14
    }

    # Reverse map to get ranks back from values
    reverse_rank_map = {v: k for k, v in rank_map.items()}

    # Convert card ranks to their corresponding numerical values, maintaining colors
    card_ranks = [(rank_map[card.waarde], card.kleur) for card in cards]

    # Add special case for the low ace (A-2-3-4-5 straight)
    if any(rank == 14 for rank, _ in card_ranks):
        card_ranks.append((1, next(card.kleur for card in cards if card.waarde == 'A')))

    # Group cards by their ranks for multi-suit handling
    rank_groups = {}
    for rank, color in card_ranks:
        if rank not in rank_groups:
            rank_groups[rank] = []
        rank_groups[rank].append(color)

    # Sort the ranks to prepare for straight detection
    sorted_ranks = sorted(rank_groups.keys())

    # Find all straights (5 consecutive ranks)
    straights = []
    for i in range(len(sorted_ranks) - 4):
        if sorted_ranks[i] + 1 == sorted_ranks[i + 1] and \
           sorted_ranks[i] + 2 == sorted_ranks[i + 2] and \
           sorted_ranks[i] + 3 == sorted_ranks[i + 3] and \
           sorted_ranks[i] + 4 == sorted_ranks[i + 4]:
            # Generate all combinations of colors for the straight
            straight_combinations = [[]]
            for rank in sorted_ranks[i:i + 5]:
                new_combinations = []
                for combo in straight_combinations:
                    for color in rank_groups[rank]:
                        new_combinations.append(combo + [(rank, color)])
                straight_combinations = new_combinations
            straights.extend(straight_combinations)

    # Convert numerical values back to Kaart objects
    formatted_straights = [
        [Kaart(color, reverse_rank_map[rank]) for rank, color in straight]
        for straight in straights
    ]

    return [len(formatted_straights) > 0, formatted_straights if formatted_straights else None]

def bevat_flush(cards):
    
    def waarde_naar_getal(waarde):
        waardes = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "B": 11, "V": 12, "K": 13, "A": 14}
        return waardes[waarde]

    kaarten_gesorteerd = sorted(hand, key=lambda kaart: waarde_naar_getal(kaart.waarde), reverse=True)

    kleur_telling = {}
    for kaart in hand:
        if kaart.kleur in kleur_telling:
            kleur_telling[kaart.kleur] += 1
        else:
            kleur_telling[kaart.kleur] = 1
       
    high_cards = []
    for i in range(7):
        if kleur_telling[kaarten_gesorteerd[i].kleur] >= 5:
            high_cards.append(kaarten_gesorteerd[i].waarde)
    
    if len(high_cards) >= 5:
        return True, high_cards[:5]
    else:
        return False, []

def all_same_color(cards):
    """
    Check if all cards in the given list have the same color.

    Parameters:
        cards (list of Kaart): A list of Kaart objects.

    Returns:
        bool: True if all cards have the same color, False otherwise.
    """
    if not cards:
        return False
    first_color = cards[0].kleur
    return all(card.kleur == first_color for card in cards)

def kind_of_straight():
    all_straights = contains_straight(hand)[1]

    for i in range(len(all_straights)):
        if all_same_color(all_straights[i]):
            
            if all_straights[i][4].waarde == 'A':            
                return 10, "A"
            else:
                return 9, [all_straights[i][4].waarde]

        else:
            return 5, [all_straights[-1][4].waarde]

def bevat_four_of_a_kind(cards):
    """
    Controleert of de hand een 'Four of a Kind' bevat.

    Args:
        hand (list): Een lijst van Kaart-objecten (7 kaarten).

    Returns:
        tuple: Een tuple met een boolean en de waarde waarvan er 4 zijn (of None).
    """
    # Tel het aantal keren dat elke waarde voorkomt in de hand
    waarde_telling = {}
    for kaart in cards:
        if kaart.waarde in waarde_telling:
            waarde_telling[kaart.waarde] += 1
        else:
            waarde_telling[kaart.waarde] = 1

    # Controleer of een waarde precies 4 keer voorkomt
    for waarde, aantal in waarde_telling.items():
        if aantal == 4:
            return True, waarde

    return [False]

def bevat_three_of_a_kind(hand):
    """
    Controleert of de hand een of meer 'Three of a Kind' bevat.

    Args:
        hand (list): Een lijst van 7 Kaart-objecten.

    Returns:
        tuple: Een tuple met een boolean en een lijst van de waarden waarvan er 3 zijn (of een lege lijst als er geen 'Three of a Kind' is).
    """
    # Tel het aantal keren dat elke waarde voorkomt in de hand
    waarde_telling = {}
    for kaart in hand:
        if kaart.waarde in waarde_telling:
            waarde_telling[kaart.waarde] += 1
        else:
            waarde_telling[kaart.waarde] = 1

    # Verzamel alle waarden die precies 3 keer voorkomen
    drie_of_a_kind_waarden = [waarde for waarde, aantal in waarde_telling.items() if aantal == 3]

    # Sorteer de lijst van 'Three of a Kind'-waarden op sterkte (numerieke waarde)
    drie_of_a_kind_waarden.sort(key=lambda waarde: waarde_naar_getal(waarde), reverse=True)

    return (len(drie_of_a_kind_waarden) > 0, drie_of_a_kind_waarden)

def bevat_paar(hand):
    """
    Controleert of de hand een of meer paren bevat.

    Args:
        hand (list): Een lijst van 7 Kaart-objecten.

    Returns:
        tuple: Een tuple met een boolean en een lijst van de waarden waarvan er paren zijn (of een lege lijst als er geen paren zijn).
    """
    # Maak een dictionary om de kaarten te groeperen op hun waarde
    waarde_teller = {}

    # Groepeer de kaarten op waarde
    for kaart in hand:
        if kaart.waarde in waarde_teller:
            waarde_teller[kaart.waarde] += 1
        else:
            waarde_teller[kaart.waarde] = 1

    # Zoek naar alle paren (waarden met precies 2 kaarten)
    pair_waarden = [waarde for waarde, aantal in waarde_teller.items() if aantal == 2]

    # Sorteer de lijst van paren op sterkte (numerieke waarde)
    pair_waarden.sort(key=lambda waarde: waarde_naar_getal(waarde), reverse=True)

    return (len(pair_waarden) > 0, pair_waarden)

def high_card_ranker(hand):
# Functie om waarde als string om te zetten naar numerieke waarde
    def waarde_naar_getal(waarde):
        waardes = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "B": 11, "V": 12, "K": 13, "A": 14}
        return waardes[waarde]

    kaarten_gesorteerd = sorted(hand, key=lambda kaart: waarde_naar_getal(kaart.waarde), reverse=True)
    
    high_card_waardes = []
    for i in range(7):
        high_card_waardes.append(kaarten_gesorteerd[i].waarde)

    return high_card_waardes    

def bevat_full_house(quads, trips, paar):
    waardes_voor_trips = []
    waardes_voor_paar = []
    
    if quads[0] and trips[0]:
        waardes_voor_paar.append(quads[1])
        waardes_voor_trips.append(quads[1])

        for i in range(len(trips[1])):
            waardes_voor_trips.append(trips[1][i])
            waardes_voor_paar.append(trips[1][i])
        
        return [True, [waardes_voor_trips, waardes_voor_paar]]

    elif quads[0] and paar[0]:
        waardes_voor_paar.append(quads[1])
        waardes_voor_trips.append(quads[1])

        for i in range(len(paar[1])):
            waardes_voor_paar.append(paar[1][i])
        
        return [True, [waardes_voor_trips, waardes_voor_paar]]
    
    elif trips[0] and len(trips[1]) == 2:
        for i in range(len(trips[1])):
            waardes_voor_trips.append(trips[1][i])
            waardes_voor_paar.append(trips[1][i])
        
        return [True, [waardes_voor_trips, waardes_voor_paar]]
    
    elif trips[0] and paar[0]:
        waardes_voor_paar.append(trips[1][0])
        waardes_voor_trips.append(trips[1][0])

        for i in range(len(paar[1])):
            waardes_voor_paar.append(paar[1][i])
        
        return [True, [waardes_voor_paar, waardes_voor_trips]]
    
    else:
        return [False, []]

def beste_full_house():
    rank_map = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'T': 10, 'B': 11, 'V': 12, 'K': 13, 'A': 14
    }
    reverse_rank_map = {
        2: '2', 3: '3', 4: '4', 5 : '5', 6: '6', 7: '7', 8: '8', 9: '9',
        10 :'T', 11: 'B', 12: 'V', 13: 'K', 14: 'A'
    }
    mogelijkheden_full_house = bevat_full_house(bevat_four_of_a_kind(hand), bevat_three_of_a_kind(hand), bevat_paar(hand))
    
    trips_list = []
    paar_list = []

    for i in range(len(mogelijkheden_full_house[1][1])):
        trips_list.append(rank_map[mogelijkheden_full_house[1][1][i]])
    
    for i in range(len(mogelijkheden_full_house[1][0])):
        paar_list.append(rank_map[mogelijkheden_full_house[1][0][i]])
    
    trips_list.sort(reverse=True)
    paar_list.sort(reverse=True)

    beste_trips = []
    beste_paar = []

    for i in range(len(trips_list)):
        beste_trips.append(reverse_rank_map[trips_list[i]])
    for i in range(len(paar_list)):
        beste_paar.append(reverse_rank_map[paar_list[i]])
    
    if beste_paar[0] == beste_trips[0]:
        beste_FH = [beste_trips[0], beste_paar[1]]
    else:
        beste_FH = [beste_trips[0], beste_paar[0]]

    return 7, beste_FH

def score_of_hand(hand):
    ''' 
    Parameters:
        hand (list of Kaart): A list of 7 Kaart objects.
    
    Returns:
        twee waardes
        - score van de hand: 10 is het hoogste(royal flush), 1 het laagste(high card)
        - een lijst met eventuele tiebreakers
    '''
    high_cards = high_card_ranker(hand)
    quads = bevat_four_of_a_kind(hand)
    trips =  bevat_three_of_a_kind(hand)
    pairs = bevat_paar(hand)
    
    if contains_straight(hand)[0]: # als een straight, straigth flush of straigth het hoogste is
        return kind_of_straight()
    
    elif quads[0]: # als quads het hoogste is
        if high_cards[0] != quads[1]:
            return 8, [quads[1], high_cards[0]]
        else:
            return 8, [quads(hand)[1], high_cards[4]]

    elif bevat_full_house(bevat_four_of_a_kind(hand), bevat_three_of_a_kind(hand), bevat_paar(hand))[0]: # als full house het hoogste is
        return beste_full_house()
    
    elif bevat_flush(hand)[0]:
        return 6, bevat_flush(hand)[1]

    elif trips[0]: # als trips het hoogste is
       
        non_trips_in_hand = [trips[1][0]]
        for i in range(2):
            if high_cards[i] != trips[1][0]:
                non_trips_in_hand.append(high_cards[i])
            else:
                non_trips_in_hand.append(high_cards[i+3])
        return 4, non_trips_in_hand

    elif pairs[0] and len(pairs[1]) >= 2: # als two pair het hoogste is
        print(high_cards)
        if high_cards[0] == pairs[1][0] and high_cards[2] == pairs[1][1]:
            return 3, [pairs[0], pairs[1][1], high_cards[4]]
        elif high_cards[0] == pairs[1][0] and high_cards[2] != pairs[1][1]:
            return 3, [pairs[0][0], pairs[1][1], high_cards[2]]
        else:
            return 3, [pairs[1][0], pairs[1][1], high_cards[0]]

    elif pairs[0] and len(pairs[1]) == 1: # als single pair het hoogste is
        non_pairs_in_hand = [pairs[1][0]]
        for i in range(3):
            if high_cards[i] != pairs[1][0]:
                non_pairs_in_hand.append(high_cards[i])
            else:
                non_pairs_in_hand.append(high_cards[i+2])
        return 2, non_pairs_in_hand
    
    else: # als high card het hoogste is
        return 1, high_cards[:5]



# Example usage
hand = [
    Kaart('Harten', '8'),
    Kaart('Harten', '9'),
    Kaart('Harten', 'K'),
    Kaart('Harten', '3'),
    Kaart('Harten', 'V'),
    Kaart('Harten', '6'),
    Kaart('Harten', '2')
]

# beste_full_house()
print(score_of_hand(hand))
