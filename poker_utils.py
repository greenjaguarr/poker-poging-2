class Kaart:
    def __init__(self, kleur, waarde):
        self.kleur = kleur
        self.waarde = waarde

    def __repr__(self):
        return f"Kaart(kleur='{self.kleur}', waarde='{self.waarde}')"

def heeft_paar(hand):
    # Maak een dictionary om de kaarten te groeperen op hun waarde
    waarde_teller = {}
    
    # Groepeer de kaarten op waarde
    for kaart in hand:
        if kaart.waarde in waarde_teller:
            waarde_teller[kaart.waarde].append(kaart)
        else:
            waarde_teller[kaart.waarde] = [kaart]
    
    # Zoek naar alle paren (waarden met precies 2 kaarten)
    paren = [kaarten for kaarten in waarde_teller.values() if len(kaarten) == 2]
    
    return paren if paren else None  # Retourneer de paren of None als er geen paren zijn

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
    print(f"Er zitten de volgende paren in de hand: {paren}")
else:
    print("Er zitten geen paren in de hand.")
