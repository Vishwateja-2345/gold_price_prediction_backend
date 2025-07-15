import pandas as pd
import os

# Fix the CSV file by removing problematic entries
try:
    print('Fixing CSV file...')
    csv_path = 'data/gold_data.csv'
    
    # Read the CSV with skipping bad lines
    df = pd.read_csv(csv_path, on_bad_lines='skip')
    print(f'Successfully loaded {df.shape[0]} rows with {len(df.columns)} columns')
    
    # Save the cleaned CSV
    df.to_csv(csv_path, index=False)
    print('CSV file fixed and saved')
    
    # Verify the fix
    df_check = pd.read_csv(csv_path)
    print(f'Verification: Successfully loaded {df_check.shape[0]} rows with {len(df_check.columns)} columns')
    print('First 3 rows:')
    print(df_check.head(3))
    
    # Create an empty historical_prices.json if it doesn't exist
    if not os.path.exists('data/historical_prices.json'):
        import json
        with open('data/historical_prices.json', 'w') as f:
            json.dump({"timestamp": "", "historical_prices": {}}, f, indent=2)
        print('Created empty historical_prices.json file')
        
except Exception as e:
    print('Error:', e)