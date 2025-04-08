import pandas as pd
import numpy as np
from collections import defaultdict
from itertools import combinations

# Charger le fichier Excel
df = pd.read_excel("/Users/leovasseur/Desktop/Projet Poker/Data/Dataset_Main.xlsx")

# Dictionnaire pour convertir les cartes
card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
               'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
suits = {'h': 0, 'd': 1, 'c': 2, 's': 3}

# Fonction pour encoder les cartes
def encode_card(card):
    if card and len(card) == 2:
        value = card_values.get(card[0], 0)
        suit = suits.get(card[1], 0)
        return (value, suit)
    return (0, 0)

# Fonction pour encoder les mains des joueurs
def encode_hand(hand_dict_str):
    encoded_hands = {}
    try:
        hand_dict = eval(hand_dict_str)
        for player, hand in hand_dict.items():
            cards = hand.split()
            encoded_hands[player] = [encode_card(card) for card in cards]
    except Exception as e:
        print(f"Erreur d'encodage des mains: {e}")
    return encoded_hands

# Fonction pour encoder les cartes de la communauté (flop, turn, river)
def encode_board(board_str):
    if pd.notnull(board_str):
        return [encode_card(card) for card in board_str.split()]
    return []

# Fonction de nettoyage des gagnants
def clean_winners(winners_str):
    return [w.strip("' ") for w in winners_str.strip("[]").split(',')] if pd.notnull(winners_str) else []

# Fonction pour évaluer la meilleure main d'un joueur
def evaluate_hand(player_hand, community_cards):
    all_cards = player_hand + community_cards
    if len(all_cards) < 5:
        return None  # Si le joueur n'a pas assez de cartes, retour à None
    best_hand = max(combinations(all_cards, 5), key=hand_value)
    return best_hand

# Fonction pour obtenir la valeur d'une main (simplifiée pour cet exemple)
def hand_value(hand):
    # Calculer la valeur de la main selon la règle du poker (exemple simplifié)
    values = [card[0] for card in hand]
    return sum(values)  # Somme des valeurs des cartes (à simplifier ou étendre avec des règles spécifiques)

# Fonction pour normaliser les mains (par exemple : "10-8", "A-K", etc.)
def normalize_hand(card1, card2):
    vals = sorted([card1[0], card2[0]], reverse=True)
    if vals[0] == vals[1]:  # Si les cartes sont égales, on les met dans un format adapté
        return f"{vals[0]}{vals[0]}"  # Par exemple : "10-10"
    return f"{vals[0]}{vals[1]}"  # Sinon : "10-8" ou "K-Q"

# Encodage des colonnes
df["Hole Cards Encoded"] = df["Hole Cards"].apply(encode_hand)
df["Flop Encoded"] = df["Flop"].apply(encode_board)
df["Turn Encoded"] = df["Turn"].apply(encode_board)
df["River Encoded"] = df["River"].apply(encode_board)

# Nettoyer la colonne des gagnants
df["Winners"] = df["Winners"].apply(clean_winners)

# Dictionnaire de stats avec les pots
main_stats = defaultdict(lambda: {"played": 0, "won": 0, "preflop_win": 0, "pots": []})

# Analyse des mains
for idx, row in df.iterrows():
    hole_cards = row["Hole Cards Encoded"]
    winners = row["Winners"]
    flop = row["Flop Encoded"]
    turn = row["Turn Encoded"]
    river = row["River Encoded"]
    community_cards = flop + turn + river

    # Vérification des gagnants
    best_hands = {}
    for player, cards in hole_cards.items():
        best_hand = evaluate_hand(cards, community_cards)
        if best_hand:
            best_hands[player] = best_hand

    if not best_hands:
        continue  # Si aucune main n'est calculée, on passe à la suivante

    # Identifier le gagnant
    best_hand_player = max(best_hands, key=lambda p: hand_value(best_hands[p]))

    # Récupérer la valeur du pot pour cette main
    pot_value = row.get("Total Pot", 0)  # Assurez-vous que la colonne 'Pot' existe dans votre fichier Excel

    # Ajouter des statistiques pour chaque joueur
    for player, cards in hole_cards.items():
        hand_label = normalize_hand(*cards)
        main_stats[hand_label]["played"] += 1
        if player == best_hand_player:
            main_stats[hand_label]["won"] += 1
            if not flop:  # win préflop = pas de flop affiché
                main_stats[hand_label]["preflop_win"] += 1
            main_stats[hand_label]["pots"].append(pot_value)

# Calcul des pots min, max et moyen
result_stats = []
for hand, stats in main_stats.items():
    played = stats["played"]
    won = stats["won"]
    preflop_win = stats["preflop_win"]
    pots = stats["pots"]

    if pots:
        avg_pot = round(np.mean(pots), 2)
        min_pot = min(pots)
        max_pot = max(pots)
    else:
        avg_pot = min_pot = max_pot = 0

    result_stats.append({
        "Main": hand,
        "Played": played,
        "Wins": won,
        "Preflop Wins": preflop_win,
        "Winrate (%)": round((won / played) * 100, 2) if played else 0,
        "Preflop Winrate (%)": round((preflop_win / played) * 100, 2) if played else 0,
        "Average Pot": avg_pot,
        "Min Pot": min_pot,
        "Max Pot": max_pot
    })

# Convertir en DataFrame
result_df = pd.DataFrame(result_stats)

# Trier par Winrate
result_df = result_df.sort_values(by="Winrate (%)", ascending=False)

# Sauvegarder les résultats
result_df.to_csv("/Users/leovasseur/Desktop/Projet Poker/Data/Winrates_by_Hand_with_Pot.csv", index=False)

print("✅ Analyse terminée ! Résultats enregistrés dans 'Winrates_by_Hand_with_Pot.csv'")