import random
import csv
import itertools
from collections import Counter

#############################
# Fonctions d'encodage des cartes

def creer_deck():
    """
    Crée un deck standard de 52 cartes.
    Chaque carte est représentée par une chaîne de caractères,
    par exemple '2C' pour le 2 de Clubs ou 'AH' pour l'As de Hearts.
    """
    rangs = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    couleurs = ['C', 'D', 'H', 'S']  # Clubs, Diamonds, Hearts, Spades
    deck = [r + c for r in rangs for c in couleurs]
    return deck

def card_to_encoded(card):
    """
    Encode une carte représentée par une chaîne en 5 valeurs :
      - Une valeur entière (2=2, 3=3, …, 10=10, J=11, Q=12, K=13, A=14)
      - Un vecteur one-hot pour la couleur correspondante.
    Exemple : "AH" → [14, 0, 0, 1, 0] (l'ordre des bits pour les couleurs est [C, D, H, S]).
    """
    # Dictionnaire pour la valeur
    rank_map = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9, 'T': 10,
        'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    # Dictionnaire pour le one-hot des couleurs
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

def generate_random_deal(deck):
    """
    Génère un deal complet aléatoire.
    Le deal est constitué de 17 cartes tirées aléatoirement dans le deck :
      - Les 5 premières cartes constituent le board.
      - Les 12 suivantes, réparties en 6 mains (2 cartes par joueur).
    Retourne board (liste de 5 cartes, en notation simple) et players (liste de 6 mains, chacune une liste de 2 cartes).
    """
    deal_cards = random.sample(deck, 17)
    board = deal_cards[:5]
    players = [deal_cards[5 + 2*i: 5 + 2*i + 2] for i in range(6)]
    return board, players

#############################
# Fonctions d'évaluation de la main

def evaluate_five(cards):
    """
    Évalue une main de 5 cartes et retourne un tuple (catégorie, tie_breaker).
    Les catégories définies sont :
      8 : Quinte flush
      7 : Carré (four of a kind)
      6 : Full house
      5 : Couleur (flush)
      4 : Quinte (straight)
      3 : Brelan (three of a kind)
      2 : Double paire (two pairs)
      1 : Paire (one pair)
      0 : Carte haute (high card)
    Le tie_breaker est un tuple des valeurs permettant de départager les mains.
    """
    # Conversion des cartes en valeurs et récupération des couleurs
    r_map = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7,
             '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}
    values = [r_map[card[0]] for card in cards]
    suits  = [card[1] for card in cards]
    values.sort(reverse=True)
    
    # Vérifie la couleur (flush)
    flush = (len(set(suits)) == 1)
    
    # Vérifie la présence d'une quinte (straight)
    unique_vals = sorted(set(values))
    if len(unique_vals) == 5:
        straight = unique_vals[-1] - unique_vals[0] == 4
        # Cas particulier de la "Wheel": A,2,3,4,5
        if set([14, 2, 3, 4, 5]) == set(values):
            straight = True
    else:
        straight = False

    # Comptage des occurrences de chaque valeur
    freq = Counter(values)
    counts = sorted(freq.values(), reverse=True)
    
    if flush and straight:
        category = 8
    elif counts[0] == 4:
        category = 7
    elif counts[0] == 3 and counts[1] == 2:
        category = 6
    elif flush:
        category = 5
    elif straight:
        category = 4
    elif counts[0] == 3:
        category = 3
    elif counts[0] == 2 and counts[1] == 2:
        category = 2
    elif counts[0] == 2:
        category = 1
    else:
        category = 0

    sorted_vals = sorted(freq.items(), key=lambda x: (x[1], x[0]), reverse=True)
    tie_breaker = tuple([val for val, cnt in sorted_vals for _ in range(cnt)])
    return (category, tie_breaker)

def evaluate_seven(cards):
    """
    À partir de 7 cartes (board + main d'un joueur), trouve la meilleure combinaison de 5 cartes.
    Retourne le meilleur score (tuple) obtenu parmi les 21 combinaisons possibles.
    """
    best = None
    for combo in itertools.combinations(cards, 5):
        score = evaluate_five(list(combo))
        if best is None or score > best:
            best = score
    return best

def determine_label(board, players):
    """
    Pour un deal complet, évalue la meilleure main de chaque joueur en combinant board et sa main.
    Retourne 1 si le joueur 1 gagne seul (sa main est strictement supérieure aux autres),
    0 sinon (égalité ou défaite).
    """
    best_hands = []
    for hand in players:
        seven_cards = board + hand
        best_hands.append(evaluate_seven(seven_cards))
    player1_best = best_hands[0]
    for other_score in best_hands[1:]:
        if other_score >= player1_best:
            return 0
    return 1

#############################
# Création et sauvegarde du dataset

def main():
    deck = creer_deck()
    n_deals = 5_00_000 # Nombre total de deals à générer
    output_file = "deals_encoded_with_winner.csv"
    
    # Constitution des en-têtes pour 17 cartes encodées (5 colonnes par carte)
    headers = []
    # Board (5 cartes)
    for i in range(1, 6):
        headers.extend([f"board{i}_val", f"board{i}_C", f"board{i}_D", f"board{i}_H", f"board{i}_S"])
    # 6 joueurs, 2 cartes par joueur
    for p in range(1, 7):
        for c in range(1, 3):
            headers.extend([f"p{p}_card{c}_val", f"p{p}_card{c}_C", f"p{p}_card{c}_D", f"p{p}_card{c}_H", f"p{p}_card{c}_S"])
    # Ajout d'une colonne pour indiquer si le joueur 1 gagne (winner)
    headers.append("winner")
    
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for i in range(n_deals):
            board, players = generate_random_deal(deck)
            # Calcul du label : 1 si joueur 1 gagne seul, 0 sinon.
            winner = determine_label(board, players)
            
            # Encodage des cartes en respectant l'ordre du header.
            row = []
            # Encodage du board
            for card in board:
                row.extend(card_to_encoded(card))
            # Encodage des mains des 6 joueurs
            for hand in players:
                for card in hand:
                    row.extend(card_to_encoded(card))
            # Ajout du label winner à la fin de la ligne
            row.append(winner)
            
            writer.writerow(row)
            
            # Affichage de la progression tous les 100000 deals
            if (i + 1) % 100000 == 0:
                print(f"{i + 1} deals générés...")
    
    print(f"Dataset de {n_deals} deals généré et sauvegardé dans '{output_file}'.")

if __name__ == "__main__":
    main()