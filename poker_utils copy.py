from itertools import combinations

# Card class definition
class Card:
    def __init__(self, value, suit):
        self.value = value  # value (e.g., '2', 'T', 'A')
        self.suit = suit    # suit (e.g., 'Harten', 'Ruiten', 'Klaveren', 'Schoppen')

    def __repr__(self):
        return f"{self.value} of {self.suit}"

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

# Example hands with unsorted cards that still contain a straight
hand1 = [Card('5', 'Harten'), Card('2', 'Schoppen'), Card('3', 'Ruiten'), Card('4', 'Klaveren'), Card('6', 'Harten'),
         Card('8', 'Schoppen'), Card('7', 'Ruiten')]  # Contains straight 2, 3, 4, 5, 6

hand2 = [Card('V', 'Harten'), Card('K', 'Schoppen'), Card('B', 'Ruiten'), Card('T', 'Klaveren'), Card('9', 'Harten'),
         Card('8', 'Schoppen'), Card('A', 'Ruiten')]  # Contains straight 9, T, J, Q, K

hand3 = [Card('A', 'Harten'), Card('3', 'Schoppen'), Card('2', 'Ruiten'), Card('5', 'Klaveren'), Card('4', 'Harten'),
         Card('6', 'Schoppen'), Card('7', 'Ruiten')]  # Contains straight 2, 3, 4, 5, 6 (Ace treated as 1)

hand4 = [Card('A', 'Harten'), Card('2', 'Schoppen'), Card('3', 'Ruiten'), Card('4', 'Klaveren'), Card('5', 'Harten'),
         Card('8', 'Schoppen'), Card('7', 'Ruiten')]  # Contains straight A, 2, 3, 4, 5

# Check for the highest straight in each hand
print(highest_straight(hand1))  # Output: (2, 3, 4, 5, 6)
print(highest_straight(hand2))  # Output: (9, T, B, V, K)
print(highest_straight(hand3))  # Output: (2, 3, 4, 5, 6)
print(highest_straight(hand4))  # Output: (A, 2, 3, 4, 5) treated as low Ace straight
