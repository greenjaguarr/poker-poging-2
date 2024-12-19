
class Kaart:
    SUIT_SYMBOLS = {"harten": "♥", "ruiten": "♦", "klaveren": "♣", "schoppen": "♠"}

    def __init__(self, kleur, waarde):
        """
        kleur: str, bijv. "harten", "klaveren"
        waarde: str, bijv. "A", "K", "10"
        """
        self.kleur = kleur
        self.waarde = waarde


kaarten1 = [Kaart("harten","K"),
           Kaart("schoppen","K"),
           Kaart("klaveren","K"),
           Kaart("harten","K"),
           Kaart("harten","V"),
           Kaart("harten","T"),
           Kaart("harten","6")]

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

    kaartkleurfrequentie_list = list(kaartkleurfrequentie.values())
    for i in range(len(kaartkleurfrequentie)):
        if kaartkleurfrequentie_list[i] >= '5':
            handresult.append("flush")
        
    kaartwaardefrequentie_list = list(kaartwaardefrequentie.values())
    for i in range(len(kaartwaardefrequentie)):
        if kaartwaardefrequentie_list[i] == '2':
            handresult.append("pair")
        if kaartkleurfrequentie_list[i] == '3':
            handresult.append("3 of a kind")
        if kaartkleurfrequentie_list[i] == '4':
            handresult.append("quads")
        

    print(handresult)
        
            
    
    


    return ...

def compare(kaarten1, kaarten2):
    '''Return "1" if kaarten1 is beter,
    "2" als kaarten2 beter is
    "0" als het een gelijkspel is'''

calc_waarde(kaarten1)