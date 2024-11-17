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
    print(df)
    return df

# Prepare the data for the LSTM model
def prepare_data(player, columns, test_size=0.2):
    df = feature_eng(player, columns)
    df = df.sort_values(by='DATE')

    # One-hot encode H/A status
    df['H/A Status'] = df['H/A Status'].apply(lambda x: 1 if x == '@' else 0)

    # Encode 'Opp' column
    df['OPP'] = df['OPP'].astype('category').cat.codes
    print(df)
    # Combine rolling lists into sequences for LSTM
    rolling_features = [f'L5 {col}' for col in columns]
   

     # Combine both sets of features
   
   
    X = np.array(df[rolling_features].map(np.array).values.tolist())
    print(X)  # Shape (samples, timesteps, features)
    y = df['PTS'].values  # Shape (samples,)

    # Split into training and testing
    split_index = int(len(X) * (1 - test_size))
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    return X_train, X_test, y_train, y_test

def train_lstm(X_train, y_train, X_test, y_test):
    model = Sequential()
    model.add(LSTM(100, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(LSTM(100))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.summary()

    history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

    loss = model.evaluate(X_test, y_test)
    #print(f'Test Loss: {loss}')
        # Predict the scores for the test set
    y_pred = model.predict(X_test)

    # Output the predicted and actual scores
    for actual, predicted in zip(y_test[:10], y_pred[:10]):  # Show first 10 predictions
        print(f"Actual: {actual:.2f}, Predicted: {predicted[0]:.2f}")
    return model


# Set a random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# Main function
def main():
    os.system('cls')
    player = "Lebron james"
    columns = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FGM', 'FGA', '3PM', '3PA', 
               'FTM', 'FTA', 'TS%', '+/-',"AVG D PTS ALLOWED","AVG D PTS ALLOWED L3","OPP DEF EFF","OPP DEF EFF L3","OPP F%","OPP F% L3","OPP FB PTS","OPP FB PTS L3","OPP FB EFF","OPP FB EFF L3","OPP 2PTS","OPP 2PTS L3","OPP 3PTS","OPP 3PTS L3"]


    # Prepare the data
    X_train, X_test, y_train, y_test = prepare_data(player, columns)

    # Train and evaluate the LSTM
    model = train_lstm(X_train, y_train, X_test, y_test)

if __name__ == "__main__":
    main()

