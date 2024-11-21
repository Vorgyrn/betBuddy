import ast
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import os

# TODO add a health metric based on rest/injuries/games in a row/home/away
scaler = StandardScaler()
def fuck_you(val):
    return np.array(ast.literal_eval(val))
# Main function
def main():
    df = pd.read_csv("lebron james NBA Game Log.csv")
    for i in range(len(df)):
        if '@' in df.iloc[i,4]:
            df.iloc[i,4] = 1
        else:
            df.iloc[i,4] = 0
    print(df.columns)   
    headers = ['MATCHUP','MIN_ROLLING', 'FGM_ROLLING',
       'FGA_ROLLING', 'FG_PCT_ROLLING', 'FG3M_ROLLING', 'FG3A_ROLLING',
       'FG3_PCT_ROLLING', 'FTM_ROLLING', 'FTA_ROLLING', 'FT_PCT_ROLLING',
       'OREB_ROLLING', 'DREB_ROLLING', 'REB_ROLLING', 'AST_ROLLING',
       'STL_ROLLING', 'BLK_ROLLING', 'TOV_ROLLING', 'PF_ROLLING',
       'PTS_ROLLING', 'PLUS_MINUS_ROLLING', 'AVG D PTS ALLOWED',
       'AVG D PTS ALLOWED L3', 'OPP DEF EFF', 'OPP DEF EFF L3', 'OPP F%',
       'OPP F% L3', 'OPP FB PTS', 'OPP FB PTS L3', 'OPP FB EFF',
       'OPP FB EFF L3', 'OPP 2PTS', 'OPP 2PTS L3', 'OPP 3PTS', 'OPP 3PTS L3']
    test_headers = ['MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
       'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
       'PTS', 'PLUS_MINUS']
    # drop na columns
    rolling_columns = [col for col in headers if "ROLLING" in col]
    non_rolling_columns = [col for col in headers if "ROLLING" not in col]

    for col in rolling_columns:
        df[col] = df[col].apply(fuck_you)
        

    

    scaler = StandardScaler()

    #df[non_rolling_columns] = scaler.fit_transform(df[non_rolling_columns])
    df[test_headers] = scaler.fit_transform(df[test_headers])
    features = df[test_headers]
    target = df['PTS']
    X = features
    y = target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(X_train.shape)
    
    

        # Reshape input data for LSTM (samples, timesteps, features)
    time_steps = 5
    X_train_reshaped = np.reshape(X_train.values, (X_train.shape[0], time_steps, int(X_train.shape[1]/time_steps)))  # 1 timestep
    X_test_reshaped = np.reshape(X_test.values, (X_test.shape[0], time_steps, int(X_test.shape[1]/time_steps)))  # 1 timestep
    
    model = Sequential()
    model.add(LSTM(128, input_shape=(time_steps, X_train_reshaped.shape[2]), activation='relu'))  # First hidden layer
    model.add(Dense(64, activation='relu'))  # Second hidden layer
    model.add(Dense(1))  # Output layer (regression task)

    # Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(X_train_reshaped, y_train, epochs=20, batch_size=32, validation_data=(X_test_reshaped, y_test))

    # Evaluate the model
    loss = model.evaluate(X_test_reshaped, y_test)
    print(f'Model Loss: {loss}')

    # Predict on test data
    predictions = model.predict(X_test_reshaped)
     # Unscale the predictions
    unscaled_ps = scaler.inverse_transform(np.concatenate([X_test.values[:, :X_test.shape[1]-1], predictions], axis=1))[:, -1]
    
    y_test_unscaled = scaler.inverse_transform(y_test.values.reshape(-1, 1))
    print("Actual vs Predicted (First 5 samples):")
    for actual, predicted in zip(y_test_unscaled[:5], unscaled_ps[:5]):
        print(f"Actual: {actual[0]}, Predicted: {predicted[0]}")
    

  
if __name__ == "__main__":
    main()

