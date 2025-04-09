import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Charger le CSV
df = pd.read_csv('/Users/bilaldelais/PokerLeoBilal/Poker/Poker_Finie/Données/poker_hands.csv')

# Afficher les premières lignes et les infos sur le DataFrame
print("Aperçu des données :")
print(df.head())
print(df.info())

#Extraction des informations des cartes : 
def parse_hole_cards(hole_cards_str):
    # Suppression d'éventuels espaces
    s = hole_cards_str.replace(" ", "")
    n = len(s)
    for i in range(n):
        # Première carte
        card1_rank = s[0]  # le premier caractère représente la valeur
        card1_suit = s[1]  # le deuxième représente la couleur
        # Deuxième carte
        card2_rank = s[2]
        card2_suit = s[3]
        return pd.Series({
            'Card1_Rank': card1_rank,
            'Card1_Suit': card1_suit,
            'Card2_Rank': card2_rank,
            'Card2_Suit': card2_suit
        })