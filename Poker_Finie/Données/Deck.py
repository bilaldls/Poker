import random
import csv

def creer_deck():
    """
    Crée un deck standard de 52 cartes.
    Chaque carte est représentée par une chaîne de caractères.
    Par exemple '2C' pour le 2 de trèfle, 'AH' pour l'As de cœur, etc.
    """
    rangs = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    couleurs = ['C', 'D', 'H', 'S']  # Clubs, Diamonds, Hearts, Spades
    deck = [r + c for r in rangs for c in couleurs]
    return deck

def generate_random_deal(deck):
    """
    Génère aléatoirement un deal complet.
    
    Un deal est constitué de 17 cartes tirées aléatoirement du deck.
    - Les 5 premières cartes forment le board (les cartes communes).
    - Les 12 cartes suivantes sont réparties en 6 mains de 2 cartes pour chaque joueur.
    """
    deal_cards = random.sample(deck, 17)
    board = deal_cards[:5]
    joueurs = [deal_cards[5 + 2*i : 5 + 2*i + 2] for i in range(6)]
    return board, joueurs

def card_to_encoded(card):
    """
    Encode une carte représentée par une chaîne en deux parties :
      - Une valeur entière (2=2, 3=3, …, 10=10, J=11, Q=12, K=13, A=14)
      - Un vecteur one-hot pour la couleur correspondante.
    
    La carte est donnée sous la forme "rC" où r est le rang et C la couleur.
    """
    # Dictionnaire de mapping pour la valeur
    rank_map = {
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        'T': 10,
        'J': 11,
        'Q': 12,
        'K': 13,
        'A': 14
    }
    # Dictionnaire pour l'encodage one-hot de la couleur
    suit_map = {
        'C': [1, 0, 0, 0],
        'D': [0, 1, 0, 0],
        'H': [0, 0, 1, 0],
        'S': [0, 0, 0, 1]
    }
    rank = card[0]
    suit = card[1]
    value = rank_map[rank]
    one_hot_suit = suit_map[suit]
    return [value] + one_hot_suit
def main():
    deck = creer_deck()
    n_deals = 3_000_000  # Taille de l'échantillon désiré
    output_file = "deals_encoded.csv"
    
    # Construction de l'en-tête pour le CSV.
    # Pour chaque carte, nous créons 5 colonnes : valeur, suit_C, suit_D, suit_H, suit_S.
    headers = []
    # Pour le board
    for i in range(1, 6):
        headers.extend([f"board{i}_val", f"board{i}_C", f"board{i}_D", f"board{i}_H", f"board{i}_S"])
    # Pour les 6 joueurs et leurs 2 cartes chacune
    for p in range(1, 7):
        for c in range(1, 3):
            headers.extend([f"p{p}_card{c}_val", f"p{p}_card{c}_C", f"p{p}_card{c}_D", f"p{p}_card{c}_H", f"p{p}_card{c}_S"])
    
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for i in range(n_deals):
            board, joueurs = generate_random_deal(deck)
            row = []
            # Encodage du board
            for card in board:
                row.extend(card_to_encoded(card))
            # Encodage des cartes des joueurs
            for main in joueurs:
                for card in main:
                    row.extend(card_to_encoded(card))
            writer.writerow(row)
            
            # Affichage de la progression tous les 100 000 deals
            if (i+1) % 100000 == 0:
                print(f"{i+1} deals générés...")
    
    print(f"Dataset de {n_deals} deals généré et sauvegardé dans '{output_file}'.")

if __name__ == "__main__":
    main()