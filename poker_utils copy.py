class Kaart:
    def __init__(self, kleur, waarde):
        self.kleur = kleur
        self.waarde = waarde

    def __repr__(self):
        return f"Kaart(kleur='{self.kleur}', waarde='{self.waarde}')"

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
        '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
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
    print(len(all_straights))
    for i in range(len(all_straights)):
        if all_same_color(all_straights[i]):
            
            if all_straights[i][4].waarde == 'A':            
                return {10: "A"}
            else:
                return {9: all_straights[i][4].waarde}

        else:
            return {5, all_straights[-1][4].waarde}

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
            return [True, waarde]

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

    # Retourneer True en de lijst van waarden als er Three of a Kind is, anders False en een lege lijst
    if drie_of_a_kind_waarden:
        return [True, drie_of_a_kind_waarden]
    else:
        return [False]

def bevat_paar(hand):
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

    # Retourneer True en de lijst van waarden als er een paar is, anders False en een lege lijst
    if pair_waarden:
        return [True, pair_waarden]
    else:
        return [False, []]

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
        '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    reverse_rank_map = {
        2: '2', 3: '3', 4: '4', 5 : '5', 6: '6', 7: '7', 8: '8', 9: '9',
        10 :'10', 11: "J", 12: 'Q', 13: 'K', 14: 'A'
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
        beste_FH = [beste_paar[1], beste_trips[0]]
    else:
        beste_FH = [beste_paar[0], beste_trips[0]]

    return {7: str(beste_FH)}

def score_of_hand(hand):
    score = {}

    if contains_straight(hand)[0]:
        print("IT WORKED")
        score.update(kind_of_straight())
    
    elif bevat_four_of_a_kind(hand)[0]:
        score.update({8: bevat_four_of_a_kind(hand)[1]})

    # elif bevat_full_house(bevat_four_of_a_kind(hand), bevat_three_of_a_kind(hand), bevat_paar(hand))[0]:
        
        score.update(beste_full_house())
    




    quads = bevat_four_of_a_kind(hand)
    trips = bevat_three_of_a_kind(hand)
    paar = bevat_paar(hand)
    bevat_full_house(quads, trips, paar)

    return score


# Example usage
hand = [
    Kaart('Harten', 'J'),
    Kaart('Harten', 'J'),
    Kaart('Harten', 'A'),
    Kaart('Harten', 'J'),
    Kaart('Harten', 'J'),
    Kaart('Harten', 'A'),
    Kaart('Harten', 'A')
]

# beste_full_house()
print(score_of_hand(hand))
