import pandas as pd
import numpy as np

# Charger le fichier Excel
df = pd.read_excel("/Users/leovasseur/Desktop/Projet Poker/Data/Dataset_Main.xlsx")

# Afficher les premières lignes et les infos du DataFrame pour vérifier sa structure
print(df.head())
print(df.info())  # Vérifie les types de données

# Dictionnaire pour convertir les valeurs des cartes
card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
               'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

suits = {'h': 0, 'd': 1, 'c': 2, 's': 3}  # h = cœur, d = carreau, c = trèfle, s = pique

# Fonction pour convertir une carte (ex: 'Jd' → (11,1))
def encode_card(card):
    if card and len(card) == 2:
        value = card_values[card[0]]  # Ex: 'J' → 11
        suit = suits[card[1]]         # Ex: 'd' → 1
        return (value, suit)
    return (0, 0)  # Si carte absente, mettre (0,0)

# Fonction pour encoder une main complète (ex: {'MrPink': 'Jd Jh'} → [(11,1), (11,1)])
def encode_hand(hand_dict):
    encoded_hands = {}
    for player, hand in hand_dict.items():
        cards = hand.split()  # Sépare les cartes ex: 'Jd Jh' → ['Jd', 'Jh']
        encoded_hand = [encode_card(card) for card in cards]  # Applique encode_card()
        encoded_hands[player] = encoded_hand
    return encoded_hands

# Fonction pour encoder les cartes du board (ex: '6d Qd 6c' → [(6,1), (12,1), (6,2)])
def encode_board(board_str):
    if pd.notnull(board_str):  # Vérifie si la valeur du board est non nulle
        cards = board_str.split()  # Sépare les cartes du board
        return [encode_card(card) for card in cards]
    return []  # Retourne une liste vide si aucune carte n'est présente

# Fonction pour encoder les actions
def encode_actions(actions_str):
    actions = []
    if pd.notnull(actions_str):
        actions_list = actions_str.split(', ')  # Sépare les actions par virgules (ex: 'MrPink raises 100, Eddie folds')
        for action in actions_list:
            parts = action.split()  # Divise chaque action en [joueur, action, montant]
            player = parts[0]
            action_type = parts[1]
            if action_type == 'folds':
                actions.append((player, 'fold', None))  # Si "fold", on met None pour le montant
            else:
                amount = int(parts[2]) if len(parts) > 2 else None  # Si montant est présent
                actions.append((player, action_type, amount))
    return actions

# Appliquer l'encodage des mains des joueurs
df["Hole Cards Encoded"] = df["Hole Cards"].apply(lambda x: encode_hand(eval(x)) if isinstance(x, str) else {})
df["Flop Encoded"] = df["Flop"].apply(encode_board)
df["Turn Encoded"] = df["Turn"].apply(encode_board)
df["River Encoded"] = df["River"].apply(encode_board)

# Appliquer l'encodage des actions pour chaque phase du jeu
df["Pre-Flop Actions Encoded"] = df["Pre-Flop Actions"].apply(encode_actions)
df["Flop Actions Encoded"] = df["Flop Actions"].apply(encode_actions)
df["Turn Actions Encoded"] = df["Turn Actions"].apply(encode_actions)
df["River Actions Encoded"] = df["River Actions"].apply(encode_actions)

# Afficher le DataFrame après ajout des colonnes encodées
print(df[["Hand ID", "Hole Cards", "Hole Cards Encoded", "Flop", "Flop Encoded", "Turn", "Turn Encoded", "River", "River Encoded",
          "Pre-Flop Actions", "Pre-Flop Actions Encoded", "Flop Actions", "Flop Actions Encoded", "Turn Actions", "Turn Actions Encoded", "River Actions", "River Actions Encoded"]].head())