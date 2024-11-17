import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import os

# Define the feature engineering function
def feature_eng(player, columns):
    df = pd.read_csv(f"{player.lower()} NBA Game Log.csv")

    # Dictionary to hold rolling lists for each column
    rolling_data = {f'L5 {col}': [] for col in columns}

    for i in range(len(df)):
        for col in columns:
            if i < 6:
                rolling_data[f'L5 {col}'].append(None)
            else:
                rolling_list = df[col][i-6:i-1].tolist()
                rolling_data[f'L5 {col}'].append(rolling_list)

    for col in columns:
        df[f'L5 {col}'] = rolling_data[f'L5 {col}']

    df.dropna(subset=[f'L5 {col}' for col in columns], inplace=True)
    
    return df

# Prepare the data for the LSTM model
def prepare_data(player, columns, test_size=0.2):
    df = feature_eng(player, columns)
    df = df.sort_values(by='Date')

    # One-hot encode H/A status
    df['H/A'] = df['H/A'].apply(lambda x: 1 if x == '@' else 0)
    
    # Encode 'Opp' column
    df['Opp'] = df['Opp'].astype('category').cat.codes

    feature_columns = ['H/A', 'Opp'] + [f'L5 {col}' for col in columns]
    
    # Scaling the features
    scaler = StandardScaler()
    df[feature_columns] = scaler.fit_transform(df[feature_columns].apply(lambda x: pd.Series(x).explode()).unstack())

    split_index = int(len(df) * (1 - test_size))
    train_df, test_df = df.iloc[:split_index], df.iloc[split_index:]

    X_train, y_train = np.array(train_df[feature_columns].tolist()), np.array(train_df['PTS'].tolist())
    X_test, y_test = np.array(test_df[feature_columns].tolist()), np.array(test_df['PTS'].tolist())

    return X_train, X_test, y_train, y_test

# Set a random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# Main function
def main():
    os.system('cls')
    player = "Lebron James"
    columns = ['PTS', 'REB', 'AST','STL','BLK','FGM','FGA','3PM','3PA','FTM','FTA','TS%', '+/-', 'AVG D PTS ALLOWED', 'AVG D PTS ALLOWED L3']
    X_train, X_test, y_train, y_test = prepare_data(player, columns)

    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(LSTM(50))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.summary()

    history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

    loss = model.evaluate(X_test, y_test)
    print(f'Test Loss: {loss}')

if __name__ == "__main__":
    main()
