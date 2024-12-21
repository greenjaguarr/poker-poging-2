score = {
    "royal flush": 10,
    "straight flush": 9,
    "four_of_a_kind": 8,
    "full_house": 7,
    "flush": 6,
    "straight": 5,
    "three_of_a_kind": 4,
    "two_pair": 3,
    "pair": 2,
    "high_card": 1
}

class Kaart:
    def __init__(self, kleur, waarde):
        self.kleur = kleur
        self.waarde = waarde

    def __repr__(self):
        return f"Kaart(kleur='{self.kleur}', waarde='{self.waarde}')"

# Functie om waarde als string om te zetten naar numerieke waarde
def waarde_naar_getal(waarde):
    waardes = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
    return waardes[waarde]

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

# Lijst met 7 kaartobjecten
kaarten = [
    Kaart("Harten", "10"),
    Kaart("Schoppen", "6"),
    Kaart("Ruiten", "K"),
    Kaart("Klaver", "A"),
    Kaart("Harten", "4"),
    Kaart("Schoppen", "7"),
    Kaart("Ruiten", "9")
]

# Controleer op paren
bevat_paar_gevonden, paar_waarden = bevat_paar(kaarten)

if bevat_paar_gevonden:
    print("Paren gevonden met de volgende waarden:")
    print(paar_waarden)
else:
    print(bevat_paar_gevonden, paar_waarden)


