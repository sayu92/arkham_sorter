import requests, json

#TODO Ajouter la distance entra chaines de caractères
#TODO Mettre toutes les possibilités avec l XP
#TODO Message en cas de non correspondance
#TODO Nettoyer

collection = []

url_pack = "https://fr.arkhamdb.com/api/public/packs"
x2 = requests.get(url_pack)
packs = json.loads(x2.text)

packs = [pack.get("code") for pack in packs ]

revised_core = packs[63]
x = requests.get(f"https://fr.arkhamdb.com/api/public/cards/{revised_core}.json")
revised_core = json.loads(x.text)

dunwich_legacy= [packs[i] for i in range(5,12)]

for cycle in dunwich_legacy :
    url = f"https://fr.arkhamdb.com/api/public/cards/{cycle}.json"
    x = requests.get(url)
    collection = collection + json.loads(x.text)

collection = [revised_core, collection]

xp = []
sansxp = [] 
gardien = []
chercheur = []
mystique = []
truand = []
survivant = []
neutre = []

CHERCHEUR = 0
GARDIEN = 1
MYSTIQUE = 2
TRUAND = 3
SURVIVANT = 4
NEUTRE = 5

unsort_0xp =[[] for i in range(6)]
gardien_sort_0xp = []
unsort_xp = [[] for i in range(6)]

sort_xp = [[] for i in range(6)]
sort_0xp = [[] for i in range(6)]

TRIE = True

def sort_type_cost_abc(card):
    if card.get("cost") is None : 
        return card.get("type_name")[5], -1, card.get("name")
    
    return card.get("type_name")[5], card.get("cost"), card.get("name")

def sort_xp_cost_abc(card):
    if card.get("cost") is None:
        return card.get("xp"), -1, card.get("name")
    return card.get("xp"), card.get("cost"), card.get("name")

if TRIE :
    for pack in collection :
        for i, card in enumerate(pack):
            if card.get("type_name") in ["Soutien", "Événement", "Compétence"] :
                
                if card.get("spoiler") is None and card.get("restrictions") is None:

                    if card.get("faction_name") == "Chercheur":
                        if card.get("xp") > 0:
                            unsort_xp[CHERCHEUR].append(card)
                        else:
                            unsort_0xp[CHERCHEUR].append(card)
                    
                    elif card.get("faction_name") == "Gardien" :
                        if card.get("xp") > 0:
                            unsort_xp[GARDIEN].append(card)
                        else:
                            unsort_0xp[GARDIEN].append(card)
                    elif card.get("faction_name") == "Mystique" :
                        if card.get("xp") > 0:
                            unsort_xp[MYSTIQUE].append(card)
                        else:
                            unsort_0xp[MYSTIQUE].append(card)
                    elif card.get("faction_name") == "Truand" :
                        if card.get("xp") > 0:
                            unsort_xp[TRUAND].append(card)
                        else:
                            unsort_0xp[TRUAND].append(card)                    
                    elif card.get("faction_name") == "Survivant" :
                        if card.get("xp") > 0:
                            unsort_xp[SURVIVANT].append(card)
                        else:
                            unsort_0xp[SURVIVANT].append(card)                    
                    elif card.get("faction_name") == "Neutre":
                        if card.get("xp") > 0:
                            unsort_xp[NEUTRE].append(card)
                        else:
                            unsort_0xp[NEUTRE].append(card)                                        

            #Classement par boite(cycle)
            if i == len(pack)-1: 
                for classe in [CHERCHEUR, GARDIEN, MYSTIQUE, TRUAND, SURVIVANT, NEUTRE]:
                    unsort_0xp[classe].sort(key=sort_type_cost_abc)
                    unsort_xp[classe].sort(key=sort_xp_cost_abc)  
                
                for classe in range(6) :
                    sort_0xp[classe].extend(unsort_0xp[classe])
                unsort_0xp = [[] for i in range(6)]
                
                for classe in range(6) :
                    sort_xp[classe].extend(unsort_xp[classe])
                unsort_xp = [[] for i in range(6)]  

                for i in range(6):
                    sort_xp[i].append(None)
                    sort_0xp[i].append(None)
b = 1 

def trouver_position(nom_carte, xp = 0 ):
    if xp > 0 :
        for classe in [CHERCHEUR, GARDIEN, MYSTIQUE, TRUAND, SURVIVANT, NEUTRE]:
            for pos, card in enumerate(sort_xp[classe]):
                if card is None:
                    continue
                                
                if card.get("name") == nom_carte and card.get("xp") == xp:
                    #print(f"page {pos//9 +1}, emplacement {pos%9 + 1}")
                    return [pos//9 +1, pos%9+1] #[page, pos]
        
    elif xp == 0:
        for classe in [CHERCHEUR, GARDIEN, MYSTIQUE, TRUAND, SURVIVANT, NEUTRE]:
            for pos, card in enumerate(sort_0xp[classe]):
                if card is None:
                    continue
                
                if card.get("name") == nom_carte :
                    #print(f"page {pos//9 +1}, emplacement {pos%9 + 1}")
                    return [pos//9 +1, pos%9+1] #[page, pos]
                
with open('collection.json', 'w') as fout:
    json.dump([sort_0xp, sort_xp], fout)

trouver_position("Flic en Patrouille", 2)    
## Atribut important :
# type_name : {Soutien, Co}
# faction_name : Neutre, Mystique
# name : Nom de la carte
# cost : cout de la carte
# pack_code : {dwl,} nom de la collection
# quantity : nombre dans la collection
# xp : nombre d'xp de la carte
# spoiler : 1 , attribut spoiler à 1 si la carte n'est pas une carte investigateur

# Regarde la classe (Gardien, Chercheur, Survivamt, Mystique, Truand):
#   Regarde si la carte à de l'XP
#       Si non : Regarde si Soutien, Événement, Compétence
#           Regarde le cout, si égalité -> classement par ordre alphabétique
#       Si oui : Classe selon le cout en XP, 
#                   Classe selon le Cout
#                       Classe selon l'ordre alpha      

# Code : Chercheur = 0 Gardien = 1 Mystique =2 Truand =3 Survivant = 4 Neutre = 5