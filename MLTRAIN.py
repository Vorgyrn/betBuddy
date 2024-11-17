import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import os

# Define the columns to use for feature extraction


def feature_eng(player):
    df = pd.read_csv(f"{player.lower()} NBA Game Log.csv")

    df = df.dropna()
    df['TARGET_PTS'] = df['PTS'].shift(-1)
    df['AVG D PTS ALLOWED NEXT'] = df['AVG D PTS ALLOWED'].shift(-1)
    df['AVG D PTS ALLOWED L3 NEXT'] = df['AVG D PTS ALLOWED L3'].shift(-1)
    df = df[:-1]
    features = df[['MIN', 'REB', 'AST', 'STL', 'BLK', 
                'L5 PTS AVG', 'L5 REB AVG', 'L5 AST AVG', 
                    'AVG D PTS ALLOWED NEXT', 'AVG D PTS ALLOWED L3 NEXT']]
    target = df["TARGET_PTS"]
    return features, target

def scale(features):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    return X_scaled

def split_data(features, target):
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42, shuffle=False)
    return X_train, X_test, y_train, y_test




def main():
    os.system('cls')
    player = "Lebron James"
    features, target = feature_eng(player)
    features_scaled = scale(features)

        # Split the data
    X_train, X_test, y_train, y_test = split_data(features_scaled, target)
    
    print("Training Features Shape:", X_train.shape)
    print("Test Features Shape:", X_test.shape)
    print("Training Target Shape:", y_train.shape)
    print("Test Target Shape:", y_test.shape)

if __name__ == "__main__":
    main()