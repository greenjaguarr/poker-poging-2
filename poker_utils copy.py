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

    return (len(formatted_straights) > 0, formatted_straights if formatted_straights else None)

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

    return False, None

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
        return True, drie_of_a_kind_waarden
    else:
        return False, []


# Example usage
hand = [
    Kaart('Harten', '7'),
    Kaart('Schoppen', 'A'),
    Kaart('Ruiten', '10'),
    Kaart('Klaveren', 'A'),
    Kaart('Harten', 'A'),
    Kaart('Schoppen', '10'),
    Kaart('Ruiten', '10')
]

print(bevat_three_of_a_kind(hand))

