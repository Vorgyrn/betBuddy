import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt

# Main function
def main():
    global model
    player = "lebron james"
    df = pd.read_csv(f"{player.lower().strip()} NBA Game Log.csv")
    print(df.head())
    print(f"Total records: {len(df)}")

    # Process the MATCHUP column and replace '@' with 1 and other with 0
    df['MATCHUP'] = df['MATCHUP'].apply(lambda x: 1 if '@' in x else 0)

    # Define the feature columns
    player_features = ['MATCHUP', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
                       'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS']
    
    defensive_features = ['AVG D PTS ALLOWED', 'AVG D PTS ALLOWED L3', 'OPP DEF EFF', 'OPP DEF EFF L3', 
                          'OPP F%', 'OPP F% L3', 'OPP FB PTS', 'OPP FB PTS L3', 'OPP FB EFF', 
                          'OPP FB EFF L3', 'OPP 2PTS', 'OPP 2PTS L3', 'OPP 3PTS', 'OPP 3PTS L3']
    
    headers = player_features + defensive_features
    
    # Extract features and target variables
    features = df[headers]
    target = df["PTS"]

    # Apply MinMaxScaler to normalize the feature columns
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)

    # Define time steps for LSTM
    time_steps = 5

    # Function to create input sequences
    def create_sequences(features, time_steps):
        sequences = []
        indices = []
        for i in range(len(features) - time_steps):
            seq = features[i:(i + time_steps), :len(player_features)]  # Past performances
            defensive_stats = features[i + time_steps, len(player_features):]
            combined_seq = np.hstack((seq, np.tile(defensive_stats, (time_steps, 1))))
            sequences.append(combined_seq)
            indices.append(i + time_steps)
        return np.array(sequences), np.array(indices)

    # Call the function to create sequences and get indices
    input_sequences, game_indices = create_sequences(features_scaled, time_steps)
    # Adjust the target to match the number of sequences
    aligned_target = target[time_steps:].reset_index(drop=True)

    # Verify the shapes of the input sequences and target
    print(f"Input sequences shape: {input_sequences.shape}")
    print(f"Aligned target shape: {aligned_target.shape}")

    # Manually split the data into training and testing sets
    split_index = int(len(input_sequences) * 0.9)  # Keep last 10% for testing
    X_train, X_test = input_sequences[:split_index], input_sequences[split_index:]
    y_train, y_test = aligned_target[:split_index], aligned_target[split_index:]
    train_indices, test_indices = game_indices[:split_index], game_indices[split_index:]

    # Verify the shapes of the training and testing sets
    print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

    # Build the LSTM model
    model = Sequential()
    model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(time_steps, input_sequences.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(50, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(1))

    # Compile the model
    model.compile(optimizer='adam', loss='mse')

    # Train the model without shuffling
    history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.1, shuffle=False, verbose=1)

    # Evaluate the model
    loss = model.evaluate(X_test, y_test, verbose=1)
    print(f"Test loss: {loss}")

    # Make predictions on the test set
    y_pred = model.predict(X_test).flatten()
    y_test = y_test.to_numpy()

    # Sort test indices and their corresponding values
    sorted_indices = np.argsort(test_indices)
    test_indices_sorted = test_indices[sorted_indices]
    y_test_sorted = y_test[sorted_indices]
    y_pred_sorted = y_pred[sorted_indices]

    # Plot predictions vs. actual values using a line plot
    plt.figure(figsize=(12, 6))

    # Line plot for actual and predicted values
    plt.plot(test_indices_sorted, y_test_sorted, marker = 'o',label='Actual')
    plt.plot(test_indices_sorted, y_pred_sorted, marker = 'o', label='Predicted')

    # Adding labels to the axes, title, and grid for better readability
    plt.xlabel('Game Index')
    plt.ylabel('Points')
    plt.title('Predicted vs Actual Points')
    plt.legend()
    plt.grid()

    # Show plot
    plt.show()

    # Calculate the percentage of predictions within 5 points of the actual values
    tolerance = 5
    count = sum(abs(y_test_sorted - y_pred_sorted) < tolerance)
    print(f"Predictions within {tolerance} points:\n", f"Correct: {count}\n",f"Total: {len(y_test_sorted)}\n", f"Accuracy: {(count / len(y_test_sorted))*100}%")

    # Printing the prediction comparison for verification
    print('Game Index -- PTtest -- PTpred')
    for idx, actual, predicted in zip(test_indices_sorted, y_test_sorted, y_pred_sorted):
        print(f'{idx} -- {actual} -- {predicted}')

if __name__ == "__main__":
    main()
