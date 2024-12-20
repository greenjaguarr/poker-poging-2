class Kaart:
    def __init__(self, kleur, waarde):
        self.kleur = kleur
        self.waarde = waarde

    def __repr__(self):
        return f"Kaart(kleur='{self.kleur}', waarde='{self.waarde}')"

def heeft_paar(hand):
    # Maak een dictionary om de frequentie van elke waarde bij te houden
    waarde_teller = {}
    
    for kaart in hand:
        if kaart.waarde in waarde_teller:
            waarde_teller[kaart.waarde] += 1
        else:
            waarde_teller[kaart.waarde] = 1
    
    # Zoek naar alle waarden die precies twee keer voorkomen
    paren = [waarde for waarde, aantal in waarde_teller.items() if aantal == 2]
    
    return paren if paren else None  # Retourneer alle paren of None als er geen paren zijn

# Voorbeeld van een pokerhand van 7 kaarten
hand = [
    Kaart('Harten', '2'),
    Kaart('Schoppen', '3'),
    Kaart('Klaver', '4'),
    Kaart('Ruiten', '2'),
    Kaart('Harten', '5'),
    Kaart('Schoppen', '7'),
    Kaart('Klaver', '3')
]

# Test de functie
paren = heeft_paar(hand)
if paren:
    print(f"Er zitten paren in de hand van {', '.join(paren)}.")
else:
    print("Er zitten geen paren in de hand.")
