import pandas as pd
import re
import os

# Dossier contenant tous les fichiers
folder_path = "/Users/leovasseur/Desktop/Projet Poker/Data/pluribus_converted_logs"  # Remplace par le chemin du dossier contenant les fichiers
output_csv = "poker_hands.csv"

# Fonction pour extraire les informations d'un fichier
def extract_poker_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    hands = re.split(r'\n\n+', content.strip())  # Séparer les mains
    data = []

    for hand in hands:
        # Extraire l'ID de la main
        hand_id_match = re.search(r'PokerStars Hand #(\d+)', hand)
        hand_id = hand_id_match.group(1) if hand_id_match else None

        # Extraire les blinds
        small_blind_match = re.search(r'(.+): posts small blind (\d+)', hand)
        big_blind_match = re.search(r'(.+): posts big blind (\d+)', hand)
        small_blind = (small_blind_match.group(1), int(small_blind_match.group(2))) if small_blind_match else (None, None)
        big_blind = (big_blind_match.group(1), int(big_blind_match.group(2))) if big_blind_match else (None, None)

        # Extraire les cartes des joueurs
        hole_cards = re.findall(r'Dealt to (.+) \[([^\]]+)\]', hand)
        hole_cards_dict = {player: cards for player, cards in hole_cards}

        # Extraire les actions des joueurs par round
        rounds = {"Pre-Flop": [], "Flop": [], "Turn": [], "River": []}
        current_round = "Pre-Flop"

        for line in hand.split("\n"):
            if "*** FLOP ***" in line:
                current_round = "Flop"
            elif "*** TURN ***" in line:
                current_round = "Turn"
            elif "*** RIVER ***" in line:
                current_round = "River"

            action_match = re.match(r'(.+?): (folds|checks|calls|bets|raises) ?(\d+)?', line)
            if action_match:
                player, action, amount = action_match.groups()
                rounds[current_round].append((player, action, int(amount) if amount else None))

        # Extraire les cartes du board
        flop_match = re.search(r'\*\*\* FLOP \*\*\* \[([^\]]+)\]', hand)
        turn_match = re.search(r'\*\*\* TURN \*\*\* \[.*\] \[(..)\]', hand)
        river_match = re.search(r'\*\*\* RIVER \*\*\* \[.*\] \[(..)\]', hand)
        flop = flop_match.group(1) if flop_match else None
        turn = turn_match.group(1) if turn_match else None
        river = river_match.group(1) if river_match else None

        # Extraire le gagnant et le pot total
        summary_match = re.search(r'Total pot (\d+)', hand)
        total_pot = int(summary_match.group(1)) if summary_match else None

        winner_match = re.findall(r'(.+) collected (\d+)', hand)
        winners = [(winner, int(amount)) for winner, amount in winner_match]

        # Ajouter les données extraites à la liste
        data.append({
            "Hand ID": hand_id,
            "Small Blind": small_blind,
            "Big Blind": big_blind,
            "Hole Cards": hole_cards_dict,
            "Pre-Flop Actions": rounds["Pre-Flop"],
            "Flop Actions": rounds["Flop"],
            "Turn Actions": rounds["Turn"],
            "River Actions": rounds["River"],
            "Flop": flop,
            "Turn": turn,
            "River": river,
            "Total Pot": total_pot,
            "Winners": winners
        })

    return data

# Liste pour stocker toutes les mains des fichiers
all_data = []

# Lire chaque fichier du dossier
for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):  # Assurez-vous que ce sont bien des fichiers de poker
        file_path = os.path.join(folder_path, filename)
        all_data.extend(extract_poker_data(file_path))

# Convertir en DataFrame et enregistrer en CSV
df = pd.DataFrame(all_data)
df.to_csv(output_csv, index=False)

print(f"Fichier CSV créé : {output_csv}")