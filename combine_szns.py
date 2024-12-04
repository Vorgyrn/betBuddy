import os
import pandas as pd

def main():    
    # Initialize an empty list to store dataframes
    df_all = []
    
    # List of seasons
    szns = ["2018", "2019", "2020", "2021", "2022", "2023"]
    
    # Read and append each season's data
    for szn in szns:
            df = pd.read_csv(f"donovan mitchell NBA Game Log {szn}.csv")
            df_all.append(df)  # Append to the list

    # Concatenate all dataframes into one
    df = pd.concat(df_all, ignore_index=True)

    # Save to a new CSV in Google Drive
    output_file = "donovan mitchell NBA Game Log.csv"
    df.to_csv(output_file, index=False)  # Save without the index column
    print(f"Combined data saved to {output_file}")

# Run the main function
if __name__ == "__main__":
    main()
